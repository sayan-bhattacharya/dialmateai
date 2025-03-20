# src/models/conversation.py
from beanie import Document
from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel

class SpeakerStats(BaseModel):
    speaking_time: float
    word_count: int
    interruptions: int
    sentiment_score: float
    toxicity_score: float
    key_phrases: List[str]

class Conversation(Document):
    call_id: str
    caller_id: str
    caller_name: str
    timestamp: datetime = datetime.now()
    duration: float
    transcript: str
    summary: str
    speaker_stats: Dict[str, SpeakerStats]
    relationship_score: float
    suggestions: List[str]

    class Settings:
        name = "conversations"

# src/core/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from dialmateai.dialmate.src.models.user_profile import User
from src.models.conversation import Conversation
import logging

async def init_db():
    try:
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        await init_beanie(database=client.dialmate, document_models=[User, Conversation])
        logging.info("Database connection established")
        return client
    except Exception as e:
        logging.error(f"Database connection failed: {str(e)}")
        raise