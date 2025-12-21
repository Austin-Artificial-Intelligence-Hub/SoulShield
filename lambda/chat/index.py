import json
import os
import time
import hashlib
import hmac
import base64
from decimal import Decimal
from typing import List, Dict, Optional
from uuid import uuid4
import boto3
from llm_provider import call_llm, run_chat_pipeline, generate_session_greeting

dynamodb = boto3.resource('dynamodb')
chat_table = dynamodb.Table(os.environ['CHAT_TABLE_NAME'])
users_table = dynamodb.Table(os.environ['USERS_TABLE_NAME'])
summaries_table = dynamodb.Table(os.environ['SUMMARIES_TABLE_NAME'])

DATA_RETENTION_DAYS = int(os.environ.get('DATA_RETENTION_DAYS', '30'))
SYSTEM_PROMPT = os.environ.get('SYSTEM_PROMPT', 'You are a helpful AI assistant.')


def handler(event, context):
    """Lambda handler for all API requests"""
    try:
        path = event.get('path', '')
        method = event.get('httpMethod', '')
        
        if path == '/auth/register' and method == 'POST':
            return handle_register(event)
        elif path == '/auth/login' and method == 'POST':
            return handle_login(event)
        elif path == '/chat' and method == 'POST':
            return handle_chat(event)
        elif path == '/summaries' and method == 'GET':
            return handle_get_summaries(event)
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Endpoint not found'})
            }

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }


def handle_register(event):
    """Handle user registration"""
    body = json.loads(event.get('body', '{}'))
    username = body.get('username', '').strip().lower()
    password = body.get('password', '')
    
    if not username or not password:
        return error_response('Username and password are required', 400)
    
    if len(password) < 6:
        return error_response('Password must be at least 6 characters', 400)
    
    # Check if user exists
    try:
        users_table.get_item(Key={'username': username})['Item']
        return error_response('Username already exists', 409)
    except KeyError:
        pass  # User doesn't exist, good to proceed
    
    # Hash password
    password_hash = hash_password(password)
    
    # Create user
    users_table.put_item(
        Item={
            'username': username,
            'password_hash': password_hash,
            'created_at': int(time.time()),
        }
    )
    
    return success_response({'message': 'User registered successfully'})


def handle_login(event):
    """Handle user login"""
    body = json.loads(event.get('body', '{}'))
    username = body.get('username', '').strip().lower()
    password = body.get('password', '')
    
    if not username or not password:
        return error_response('Username and password are required', 400)
    
    # Get user
    try:
        user = users_table.get_item(Key={'username': username})['Item']
    except KeyError:
        return error_response('Invalid username or password', 401)
    
    # Verify password
    if not verify_password(password, user['password_hash']):
        return error_response('Invalid username or password', 401)
    
    # Generate session token (simple JWT-like token)
    token = generate_user_token(username)
    
    return success_response({
        'message': 'Login successful',
        'token': token,
        'username': username
    })


def handle_chat(event):
    """Handle chat requests"""
    body = json.loads(event.get('body', '{}'))
    message = body.get('message')
    session_id = body.get('sessionId', str(uuid4()))
    token = body.get('token')
    
    if not message:
        return error_response('Message is required', 400)
    
    # Verify user token
    username = verify_user_token(token)
    if not username:
        return error_response('Invalid or expired token', 401)
    
    # Retrieve conversation history
    history = get_conversation_history(session_id)
    
    # Fetch user's past session summaries for context
    past_summaries = []
    is_new_session = len(history) == 0
    if is_new_session:
        past_summaries = get_user_summaries(username)[:3]  # Get last 3 summaries
        print(f"New session for {username}, found {len(past_summaries)} past summaries")
    
    # Build summary context string for the pipeline
    summary_context = ""
    if past_summaries:
        summary_context = "Previous session summaries:\n" + "\n".join([
            f"- {s['summary']}" for s in past_summaries
        ])
    
    # Generate personalized greeting for returning users on new session
    greeting = ""
    if is_new_session and past_summaries:
        greeting = generate_session_greeting(past_summaries)
        print(f"Generated greeting for returning user: {greeting[:50]}...")
    
    # If we have a greeting for a returning user, just use that (no double response)
    if greeting:
        response_text = greeting
        options = ["Share how I'm feeling", "Just checking in"]
    else:
        # Run the chat pipeline with summary context
        pipeline_result = run_chat_pipeline(message, history, summary_context)
        response_text = pipeline_result.get('response_text', '')
        options = pipeline_result.get('options', [])
    
    # Store user message and assistant response
    timestamp = int(time.time() * 1000)
    ttl = int(time.time()) + (DATA_RETENTION_DAYS * 24 * 60 * 60)
    
    store_message(session_id, timestamp, 'user', message, ttl, username)
    store_message(session_id, timestamp + 1, 'assistant', response_text, ttl, username)
    
    # Generate and store summary if conversation is getting long
    if len(history) >= 10:  # After 5 exchanges
        print(f"Generating summary for user {username}, session {session_id}")
        messages = [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            *history,
            {'role': 'user', 'content': message}
        ]
        summary = generate_conversation_summary(messages)
        store_summary(username, session_id, summary, ttl)
        print(f"Summary stored: {summary[:50]}...")
    
    # Return only response_text and options (no internal fields)
    return success_response({
        'sessionId': session_id,
        'response': response_text,
        'options': options,
        'timestamp': timestamp
    })


def handle_get_summaries(event):
    """Get user's conversation summaries"""
    token = event.get('queryStringParameters', {}).get('token') if event.get('queryStringParameters') else None
    
    print(f"Getting summaries for token: {token[:10] if token else 'None'}...")
    
    # Verify user token
    username = verify_user_token(token)
    if not username:
        print(f"Invalid token verification")
        return error_response('Invalid or expired token', 401)
    
    print(f"Getting summaries for user: {username}")
    
    # Get summaries
    summaries = get_user_summaries(username)
    
    print(f"Found {len(summaries)} summaries")
    
    return success_response({'summaries': summaries})


def get_conversation_history(session_id: str) -> List[Dict]:
    """Retrieve conversation history from DynamoDB"""
    response = table.query(
        KeyConditionExpression='sessionId = :sid',
        ExpressionAttributeValues={':sid': session_id},
        Limit=20,  # Last 10 exchanges
        ScanIndexForward=False
    )

    items = response.get('Items', [])
    items.reverse()

    return [
        {'role': item['role'], 'content': item['content']}
        for item in items
    ]


def store_message(session_id: str, timestamp: int, role: str, content: str, ttl: int):
    """Store message in DynamoDB"""
    table.put_item(
        Item={
            'sessionId': session_id,
            'timestamp': timestamp,
            'role': role,
            'content': content,
            'ttl': ttl
        }
    )


def get_conversation_history(session_id: str) -> List[Dict]:
    """Retrieve conversation history from DynamoDB"""
    response = chat_table.query(
        KeyConditionExpression='sessionId = :sid',
        ExpressionAttributeValues={':sid': session_id},
        Limit=20,  # Last 10 exchanges
        ScanIndexForward=False
    )

    items = response.get('Items', [])
    items.reverse()

    return [
        {'role': item['role'], 'content': item['content']}
        for item in items
    ]


def store_message(session_id: str, timestamp: int, role: str, content: str, ttl: int, username: str = None):
    """Store message in DynamoDB"""
    item = {
        'sessionId': session_id,
        'timestamp': timestamp,
        'role': role,
        'content': content,
        'ttl': ttl,
    }
    if username:
        item['username'] = username
    
    chat_table.put_item(Item=item)


def hash_password(password: str) -> str:
    """Hash password using PBKDF2"""
    salt = os.urandom(32)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return base64.b64encode(salt + pwdhash).decode('ascii')


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash"""
    try:
        stored_bytes = base64.b64decode(stored_hash.encode('ascii'))
        salt = stored_bytes[:32]
        stored_pwdhash = stored_bytes[32:]
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return hmac.compare_digest(stored_pwdhash, pwdhash)
    except:
        return False


def generate_user_token(username: str) -> str:
    """Generate simple user token (in production, use proper JWT)"""
    timestamp = str(int(time.time()))
    data = f"{username}:{timestamp}"
    return base64.b64encode(data.encode()).decode()


def verify_user_token(token: str) -> Optional[str]:
    """Verify user token and return username"""
    if not token:
        return None
    
    try:
        data = base64.b64decode(token.encode()).decode()
        username, timestamp = data.split(':')
        
        # Check if token is not too old (24 hours)
        if int(time.time()) - int(timestamp) > 86400:
            return None
            
        return username
    except:
        return None


def generate_conversation_summary(messages: List[Dict]) -> str:
    """Generate a summary of the conversation"""
    # Create a summary prompt
    conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages[-10:]])
    
    summary_prompt = [
        {'role': 'system', 'content': 'Summarize this conversation in 2-3 sentences. Focus on the main topics discussed and key points.'},
        {'role': 'user', 'content': f"Conversation to summarize:\n{conversation_text}"}
    ]
    
    try:
        summary = call_llm(summary_prompt)
        return summary
    except:
        return "Conversation summary unavailable"


def store_summary(username: str, session_id: str, summary: str, ttl: int):
    """Store conversation summary"""
    summaries_table.put_item(
        Item={
            'username': username,
            'sessionId': session_id,
            'summary': summary,
            'created_at': int(time.time()),
            'ttl': ttl,
        }
    )


def get_user_summaries(username: str) -> List[Dict]:
    """Get all summaries for a user"""
    response = summaries_table.query(
        KeyConditionExpression='username = :username',
        ExpressionAttributeValues={':username': username},
        ScanIndexForward=False,
        Limit=50
    )
    
    return [
        {
            'sessionId': item['sessionId'],
            'summary': item['summary'],
            'created_at': item['created_at']
        }
        for item in response.get('Items', [])
    ]


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder for DynamoDB Decimal types"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)


def success_response(data: dict) -> dict:
    """Return success response"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(data, cls=DecimalEncoder)
    }


def error_response(message: str, status_code: int = 400) -> dict:
    """Return error response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({'error': message}, cls=DecimalEncoder)
    }