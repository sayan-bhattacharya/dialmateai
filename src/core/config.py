# src/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TELEGRAM_TOKEN: str
    DATABASE_URL: str
    MODEL_PATH: str

    class Config:
        env_file = ".env"

settings = Settings()

# src/core/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from dialmateai.dialmate.src.models.user_profile import User
from src.models.conversation import Conversation
from src.models.analysis import Analysis

async def init_db():
    client = AsyncIOMotorClient(settings.DATABASE_URL)
    await init_beanie(database=client.dialmate, document_models=[User, Conversation, Analysis])

# src/models/user.py
from beanie import Document
from typing import Optional, List
from pydantic import BaseModel

class PersonalityTraits(BaseModel):
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float

class User(Document):
    telegram_id: int
    username: Optional[str]
    personality_traits: Optional[PersonalityTraits]
    custom_preferences: Optional[str]

    class Settings:
        name = "users"

# src/bot/handlers.py
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from src.services.audio_processor import AudioProcessor
from src.services.text_analyzer import TextAnalyzer

PERSONALITY_QUESTIONS = range(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Dialmate! Let's start by understanding your personality better. "
        "Please answer a few questions."
    )
    return PERSONALITY_QUESTIONS

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    audio_processor = AudioProcessor()
    text_analyzer = TextAnalyzer()

    # Get audio file
    audio_file = await update.message.voice.get_file()

    # Process audio to text
    text = await audio_processor.convert_to_text(audio_file)

    # Analyze text
    analysis = await text_analyzer.analyze(text)

    # Store in database
    # Send insights
    await update.message.reply_text(f"Analysis: {analysis}")

# main.py
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from src.core.config import settings
from src.core.database import init_db
from src.bot.handlers import start, handle_audio

async def main():
    # Initialize database
    await init_db()

    # Initialize bot
    application = Application.builder().token(settings.TELEGRAM_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VOICE, handle_audio))

    # Start bot
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())