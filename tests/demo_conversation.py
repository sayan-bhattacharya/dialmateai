# tests/demo_conversation.py
import wave
import numpy as np

def create_demo_audio():
    """Create a demo audio file with two speakers"""
    # Parameters
    duration = 10  # seconds
    sample_rate = 44100
    t = np.linspace(0, duration, duration * sample_rate)

    # Generate two different tones for two speakers
    speaker1 = np.sin(2 * np.pi * 440 * t)  # 440 Hz tone
    speaker2 = np.sin(2 * np.pi * 880 * t)  # 880 Hz tone

    # Combine speakers
    audio = np.zeros_like(t)
    audio[:len(t)//2] = speaker1[:len(t)//2]  # First half is speaker 1
    audio[len(t)//2:] = speaker2[len(t)//2:]  # Second half is speaker 2

    # Save to WAV file
    with wave.open('demo_conversation.wav', 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio.astype(np.int16).tobytes())

    return 'demo_conversation.wav'