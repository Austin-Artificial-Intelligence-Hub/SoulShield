#!/usr/bin/env python3
"""
SoulShield Telegram Bot
A Persian/Farsi voice-enabled wellness companion bot

Features:
- Text messages in any language
- Voice messages with Persian (Farsi) speech-to-text via OpenAI Whisper
- Text-to-speech responses in Farsi via OpenAI TTS
- Integration with SoulShield API

Usage:
    export $(cat ../.env | xargs)
    export TELEGRAM_BOT_TOKEN="your_bot_token_here"
    python bot.py
"""

import os
import logging
import tempfile
import requests
from pathlib import Path
from telegram import Update, Voice
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from openai import OpenAI

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration from environment
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
API_URL = os.environ.get('API_URL', 'https://pypwr35xf3.execute-api.us-east-1.amazonaws.com/prod')
API_KEY = os.environ.get('API_KEY', '')

# OpenAI client for Whisper and TTS
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# User sessions (Telegram user_id -> SoulShield session data)
user_sessions = {}


class UserSession:
    """Manages user session state"""
    def __init__(self, telegram_user_id: int):
        self.telegram_user_id = telegram_user_id
        self.soulshield_token = None
        self.session_id = None
        self.username = None
        self.is_authenticated = False
    
    def to_dict(self):
        return {
            'telegram_user_id': self.telegram_user_id,
            'soulshield_token': self.soulshield_token,
            'session_id': self.session_id,
            'username': self.username,
            'is_authenticated': self.is_authenticated
        }


def get_or_create_session(user_id: int) -> UserSession:
    """Get or create a user session"""
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession(user_id)
    return user_sessions[user_id]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user = update.effective_user
    session = get_or_create_session(user.id)
    
    welcome_message = f"""
🛡️ **به SoulShield خوش آمدید!**
_Welcome to SoulShield!_

سلام {user.first_name}! 👋

من یک همراه هوش مصنوعی برای سلامت روان هستم. می‌توانید با من به فارسی صحبت کنید.

**چگونه از من استفاده کنید:**
🎤 یک پیام صوتی ارسال کنید - من گوش می‌دهم
💬 یا یک پیام متنی بنویسید

**دستورات:**
/start - شروع دوباره
/login - ورود به حساب کاربری
/register - ثبت نام
/help - راهنما

_برای شروع، یک پیام صوتی یا متنی ارسال کنید..._
"""
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_text = """
🛡️ **راهنمای SoulShield**

**پیام صوتی:**
می‌توانید به فارسی صحبت کنید و من متوجه می‌شوم.

**پیام متنی:**
به هر زبانی بنویسید.

**دستورات:**
/start - شروع مجدد
/login [username] [password] - ورود
/register [username] [password] - ثبت نام
/help - این راهنما

**نکته حریم خصوصی:**
گفتگوهای شما رمزگذاری شده و امن هستند. 🔒
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /register command"""
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ لطفاً نام کاربری و رمز عبور وارد کنید:\n"
            "`/register username password`",
            parse_mode='Markdown'
        )
        return
    
    username = context.args[0]
    password = context.args[1]
    
    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            json={'username': username, 'password': password},
            headers={'x-api-key': API_KEY, 'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            await update.message.reply_text(
                f"✅ ثبت نام موفق!\n"
                f"اکنون با `/login {username} {password}` وارد شوید.",
                parse_mode='Markdown'
            )
        else:
            error = response.json().get('error', 'Unknown error')
            await update.message.reply_text(f"❌ خطا در ثبت نام: {error}")
    except Exception as e:
        logger.error(f"Registration error: {e}")
        await update.message.reply_text("❌ خطا در ارتباط با سرور")


async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /login command"""
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ لطفاً نام کاربری و رمز عبور وارد کنید:\n"
            "`/login username password`",
            parse_mode='Markdown'
        )
        return
    
    username = context.args[0]
    password = context.args[1]
    user_id = update.effective_user.id
    session = get_or_create_session(user_id)
    
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={'username': username, 'password': password},
            headers={'x-api-key': API_KEY, 'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            session.soulshield_token = data.get('token')
            session.username = username
            session.is_authenticated = True
            
            await update.message.reply_text(
                f"✅ خوش آمدید {username}!\n"
                f"اکنون می‌توانید با من صحبت کنید. 💚",
                parse_mode='Markdown'
            )
        else:
            error = response.json().get('error', 'Invalid credentials')
            await update.message.reply_text(f"❌ خطا در ورود: {error}")
    except Exception as e:
        logger.error(f"Login error: {e}")
        await update.message.reply_text("❌ خطا در ارتباط با سرور")


async def transcribe_voice(voice_file_path: str) -> str:
    """Transcribe voice message using OpenAI Whisper (supports Persian)"""
    try:
        with open(voice_file_path, 'rb') as audio_file:
            transcript = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="fa"  # Persian/Farsi
            )
        return transcript.text
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise


async def text_to_speech(text: str, output_path: str) -> str:
    """Convert text to speech using OpenAI TTS"""
    try:
        response = openai_client.audio.speech.create(
            model="tts-1",
            voice="nova",  # Options: alloy, echo, fable, onyx, nova, shimmer
            input=text,
        )
        response.stream_to_file(output_path)
        return output_path
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise


async def call_soulshield_api(message: str, session: UserSession) -> dict:
    """Call SoulShield API with user message"""
    try:
        import uuid
        if not session.session_id:
            session.session_id = str(uuid.uuid4())
        
        payload = {
            'message': message,
            'sessionId': session.session_id,
            'token': session.soulshield_token
        }
        
        response = requests.post(
            f"{API_URL}/chat",
            json=payload,
            headers={
                'x-api-key': API_KEY,
                'Content-Type': 'application/json'
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"API error: {response.status_code} - {response.text}")
            return {'response': 'متأسفم، مشکلی پیش آمد. لطفاً دوباره تلاش کنید.', 'options': []}
    
    except Exception as e:
        logger.error(f"API call error: {e}")
        return {'response': 'خطا در ارتباط با سرور', 'options': []}


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice messages - transcribe Persian and respond"""
    user_id = update.effective_user.id
    session = get_or_create_session(user_id)
    
    # Check authentication
    if not session.is_authenticated:
        await update.message.reply_text(
            "⚠️ لطفاً ابتدا وارد شوید:\n"
            "`/login username password`\n"
            "یا ثبت نام کنید:\n"
            "`/register username password`",
            parse_mode='Markdown'
        )
        return
    
    # Show typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    try:
        # Download voice message
        voice = update.message.voice
        voice_file = await context.bot.get_file(voice.file_id)
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as tmp_file:
            voice_path = tmp_file.name
            await voice_file.download_to_drive(voice_path)
        
        # Transcribe Persian voice to text
        logger.info(f"Transcribing voice message from user {user_id}")
        transcribed_text = await transcribe_voice(voice_path)
        logger.info(f"Transcribed: {transcribed_text}")
        
        # Clean up voice file
        os.unlink(voice_path)
        
        # Show what was transcribed
        await update.message.reply_text(f"🎤 شنیدم: _{transcribed_text}_", parse_mode='Markdown')
        
        # Call SoulShield API
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
        api_response = await call_soulshield_api(transcribed_text, session)
        
        response_text = api_response.get('response', 'No response')
        options = api_response.get('options', [])
        
        # Send text response
        await update.message.reply_text(f"💚 {response_text}")
        
        # Send options if available
        if options:
            options_text = "\n".join([f"• {opt}" for opt in options])
            await update.message.reply_text(f"📝 گزینه‌ها:\n{options_text}")
        
        # Generate voice response
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='record_voice')
        
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_audio:
            audio_path = tmp_audio.name
        
        await text_to_speech(response_text, audio_path)
        
        # Send voice response
        with open(audio_path, 'rb') as audio_file:
            await update.message.reply_voice(voice=audio_file)
        
        # Clean up
        os.unlink(audio_path)
        
    except Exception as e:
        logger.error(f"Voice handling error: {e}")
        await update.message.reply_text("❌ خطا در پردازش پیام صوتی. لطفاً دوباره تلاش کنید.")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages"""
    user_id = update.effective_user.id
    session = get_or_create_session(user_id)
    
    # Check authentication
    if not session.is_authenticated:
        await update.message.reply_text(
            "⚠️ لطفاً ابتدا وارد شوید:\n"
            "`/login username password`\n"
            "یا ثبت نام کنید:\n"
            "`/register username password`",
            parse_mode='Markdown'
        )
        return
    
    user_message = update.message.text
    
    # Show typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    try:
        # Call SoulShield API
        api_response = await call_soulshield_api(user_message, session)
        
        response_text = api_response.get('response', 'No response')
        options = api_response.get('options', [])
        
        # Send text response
        await update.message.reply_text(f"💚 {response_text}")
        
        # Send options if available
        if options:
            options_text = "\n".join([f"• {opt}" for opt in options])
            await update.message.reply_text(f"📝 گزینه‌ها:\n{options_text}")
        
    except Exception as e:
        logger.error(f"Text handling error: {e}")
        await update.message.reply_text("❌ خطا در پردازش پیام. لطفاً دوباره تلاش کنید.")


def main() -> None:
    """Start the bot"""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set!")
        print("Get a token from @BotFather on Telegram and set it:")
        print("  export TELEGRAM_BOT_TOKEN='your_token_here'")
        return
    
    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY environment variable not set!")
        return
    
    print("🛡️ Starting SoulShield Telegram Bot...")
    print(f"📡 API URL: {API_URL}")
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(CommandHandler("login", login))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Start polling
    print("✅ Bot is running! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

