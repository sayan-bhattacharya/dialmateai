# tests/test_audio_processor.py
import pytest
import os
from src.services.audio_processor import AudioProcessor

@pytest.mark.asyncio
async def test_audio_processor():
    # Create test audio processor
    processor = AudioProcessor()

    # Test file paths
    test_dir = "tests/test_files"
    os.makedirs(test_dir, exist_ok=True)

    # Test with non-existent file
    result = await processor.transcribe("nonexistent.wav")
    assert result is None

    # Test with invalid format
    with open(f"{test_dir}/invalid.txt", "w") as f:
        f.write("test")
    result = await processor.transcribe(f"{test_dir}/invalid.txt")
    assert result is None

    # Clean up
    os.remove(f"{test_dir}/invalid.txt")