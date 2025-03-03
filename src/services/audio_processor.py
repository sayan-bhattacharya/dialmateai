# src/services/audio_processor.py
import speech_recognition as sr
import logging
from pydub import AudioSegment
import os
from typing import Optional, Union

class AudioProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.supported_formats = ['.ogg', '.wav', '.mp3']

    async def transcribe(self, audio_path: str) -> Union[str, None]:
        """
        Transcribe audio file to text

        Args:
            audio_path (str): Path to audio file

        Returns:
            str: Transcribed text or None if transcription fails
        """
        try:
            # Validate file
            if not os.path.exists(audio_path):
                logging.error(f"Audio file not found: {audio_path}")
                return None

            file_ext = os.path.splitext(audio_path)[1].lower()
            if file_ext not in self.supported_formats:
                logging.error(f"Unsupported audio format: {file_ext}")
                return None

            # Convert to wav if needed
            wav_path = audio_path
            if file_ext != '.wav':
                wav_path = await self._convert_to_wav(audio_path)

            # Transcribe
            with sr.AudioFile(wav_path) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio)
                logging.info(f"Successfully transcribed audio: {audio_path}")
                return text

        except sr.UnknownValueError:
            logging.error("Speech recognition could not understand the audio")
            return None
        except sr.RequestError as e:
            logging.error(f"Could not request results from speech recognition service: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Error transcribing audio: {str(e)}")
            return None
        finally:
            # Cleanup temporary wav file
            if 'wav_path' in locals() and wav_path != audio_path:
                try:
                    os.remove(wav_path)
                    logging.debug(f"Cleaned up temporary file: {wav_path}")
                except Exception as e:
                    logging.warning(f"Failed to cleanup temporary file: {str(e)}")

    async def _convert_to_wav(self, audio_path: str) -> str:
        """
        Convert audio file to wav format

        Args:
            audio_path (str): Path to audio file

        Returns:
            str: Path to converted wav file
        """
        try:
            wav_path = os.path.splitext(audio_path)[0] + '.wav'
            audio = AudioSegment.from_file(audio_path)
            audio.export(wav_path, format='wav')
            logging.info(f"Successfully converted {audio_path} to WAV")
            return wav_path
        except Exception as e:
            logging.error(f"Error converting audio to WAV: {str(e)}")
            raise

    async def process_voice_message(self, file_path: str) -> dict:
        """
        Process voice message and return analysis

        Args:
            file_path (str): Path to voice message file

        Returns:
            dict: Analysis results including transcription and audio metrics
        """
        try:
            # Transcribe audio
            transcript = await self.transcribe(file_path)
            if not transcript:
                return {"error": "Failed to transcribe audio"}

            # Basic audio analysis (you can expand this)
            audio = AudioSegment.from_file(file_path)

            return {
                "transcript": transcript,
                "duration_seconds": len(audio) / 1000,
                "channels": audio.channels,
                "sample_width": audio.sample_width,
                "frame_rate": audio.frame_rate,
                "status": "success"
            }

        except Exception as e:
            logging.error(f"Error processing voice message: {str(e)}")
            return {"error": str(e)}
        