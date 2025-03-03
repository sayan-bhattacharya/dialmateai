# tests/test_bot.py
import asyncio
import pytest
from src.core.database import Database
from src.services.text_analyzer import TextAnalyzer
from src.services.audio_processor import AudioProcessor
import os
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
async def database():
    db = await Database.connect_db()
    yield db
    await Database.close()

@pytest.fixture
def text_analyzer():
    return TextAnalyzer()

@pytest.fixture
def audio_processor():
    return AudioProcessor()

async def test_database_connection(database):
    assert database is not None
    db = Database.get_database()
    assert db is not None

async def test_text_analyzer(text_analyzer):
    text = "I am happy to talk with you!"
    analysis = await text_analyzer.analyze_text(text)
    assert analysis is not None
    assert 'sentiment' in analysis
    assert 'communication_patterns' in analysis

async def test_audio_processor(audio_processor):
    # Create a test audio file first
    test_audio_path = "tests/test_audio.ogg"
    if os.path.exists(test_audio_path):
        transcript = await audio_processor.transcribe(test_audio_path)
        assert transcript is not None

def test_environment_variables():
    assert os.getenv('TELEGRAM_TOKEN') is not None
    assert os.getenv('MONGODB_URI') is not None
    assert os.getenv('DB_NAME') is not None