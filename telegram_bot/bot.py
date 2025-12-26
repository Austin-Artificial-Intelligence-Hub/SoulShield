#!/usr/bin/env python3
"""
SoulShield Telegram Bot
A Persian/Farsi voice-enabled wellness companion bot
"""

import os
import logging
import tempfile
import requests
import uuid
from telegram import Update
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

# Configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
API_URL = os.environ.get('API_URL', 'https://pypwr35xf3.execute-api.us-east-1.amazonaws.com/prod')
API_KEY = os.environ.get('API_KEY', '')

# OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# User sessions
user_sessions = {}


class UserSession:
    def __init__(self, telegram_user_id: int):
        self.telegram_user_id = telegram_user_id
        self.soulshield_token = None
        self.session_id = str(uuid.uuid4())
        self.username = None
        self.is_authenticated = False


def get_or_create_session(user_id: int) -> UserSession:
    if user_id not in user_sessions:
        user_sessions[user_id] = UserSession(user_id)
    return user_sessions[user_id]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    welcome_message = f"""
🛡️ **به SoulShield خوش آمدید!**

سلام {user.first_name}! 👋

من یک همراه هوش مصنوعی برای سلامت روان هستم.

**دستورات:**
/register username password - ثبت نام
/login username password - ورود
/help - راهنما

🎤 پیام صوتی به فارسی ارسال کنید
💬 یا پیام متنی بنویسید
"""
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = """
🛡️ **راهنما**

/register username password - ثبت نام
/login username password - ورود

🎤 پیام صوتی فارسی
💬 پیام متنی
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        await update.message.reply_text("❌ `/register username password`", parse_mode='Markdown')
        return
    
    username, password = context.args[0], context.args[1]
    
    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            json={'username': username, 'password': password},
            headers={'x-api-key': API_KEY, 'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            await update.message.reply_text(f"✅ ثبت نام موفق! `/login {username} {password}`", parse_mode='Markdown')
        else:
            error = response.json().get('error', 'Error')
            await update.message.reply_text(f"❌ {error}")
    except Exception as e:
        logger.error(f"Register error: {e}")
        await update.message.reply_text("❌ خطا")


async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        await update.message.reply_text("❌ `/login username password`", parse_mode='Markdown')
        return
    
    username, password = context.args[0], context.args[1]
    session = get_or_create_session(update.effective_user.id)
    
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
            await update.message.reply_text(f"✅ خوش آمدید {username}! 💚")
        else:
            await update.message.reply_text("❌ خطا در ورود")
    except Exception as e:
        logger.error(f"Login error: {e}")
        await update.message.reply_text("❌ خطا")


async def transcribe_voice(voice_path: str) -> str:
    with open(voice_path, 'rb') as f:
        transcript = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            language="fa"
        )
    return transcript.text


async def text_to_speech(text: str, output_path: str) -> str:
    response = openai_client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text,
    )
    response.stream_to_file(output_path)
    return output_path


async def call_api(message: str, session: UserSession) -> dict:
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={
                'message': message,
                'sessionId': session.session_id,
                'token': session.soulshield_token
            },
            headers={'x-api-key': API_KEY, 'Content-Type': 'application/json'},
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        return {'response': 'خطا', 'options': []}
    except Exception as e:
        logger.error(f"API error: {e}")
        return {'response': 'خطا در ارتباط', 'options': []}


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session = get_or_create_session(update.effective_user.id)
    
    if not session.is_authenticated:
        await update.message.reply_text("⚠️ ابتدا `/login username password`", parse_mode='Markdown')
        return
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    try:
        voice = update.message.voice
        voice_file = await context.bot.get_file(voice.file_id)
        
        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as tmp:
            voice_path = tmp.name
            await voice_file.download_to_drive(voice_path)
        
        text = await transcribe_voice(voice_path)
        os.unlink(voice_path)
        
        await update.message.reply_text(f"🎤 _{text}_", parse_mode='Markdown')
        
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
        result = await call_api(text, session)
        
        response_text = result.get('response', '')
        await update.message.reply_text(f"💚 {response_text}")
        
        # Voice response
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='record_voice')
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
            audio_path = tmp.name
        
        await text_to_speech(response_text, audio_path)
        with open(audio_path, 'rb') as f:
            await update.message.reply_voice(voice=f)
        os.unlink(audio_path)
        
    except Exception as e:
        logger.error(f"Voice error: {e}")
        await update.message.reply_text("❌ خطا")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session = get_or_create_session(update.effective_user.id)
    
    if not session.is_authenticated:
        await update.message.reply_text("⚠️ ابتدا `/login username password`", parse_mode='Markdown')
        return
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    try:
        result = await call_api(update.message.text, session)
        response_text = result.get('response', '')
        await update.message.reply_text(f"💚 {response_text}")
    except Exception as e:
        logger.error(f"Text error: {e}")
        await update.message.reply_text("❌ خطا")


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not set!")
        return
    
    print("🛡️ Starting SoulShield Telegram Bot...")
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("register", register))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("✅ Bot running!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
