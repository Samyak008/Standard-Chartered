import asyncio
import logging
import numpy as np
import whisper
from typing import Dict, Optional, List
from vosk import Model, KaldiRecognizer
import json

logger = logging.getLogger(__name__)

# Store transcriptions
transcriptions: Dict[str, List[str]] = {}

# Load Whisper model (small for faster processing)
try:
    whisper_model = whisper.load_model("small")
    logger.info("Whisper model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load Whisper model: {str(e)}")
    whisper_model = None

# Load Vosk model for faster, offline processing
try:
    vosk_model = Model(lang="en-us")
    logger.info("Vosk model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load Vosk model: {str(e)}")
    vosk_model = None

class AudioTranscriber:
    """Transcribes audio using either Whisper or Vosk."""
    
    def __init__(self, session_id: str, use_whisper: bool = False):
        """
        Initialize audio transcriber.
        
        Args:
            session_id: Unique session identifier
            use_whisper: Whether to use Whisper (more accurate but slower) over Vosk
        """
        self.session_id = session_id
        self.use_whisper = use_whisper
        self.buffer = []
        
        # Initialize session transcriptions
        if session_id not in transcriptions:
            transcriptions[session_id] = []
        
        # Initialize Vosk recognizer
        if not use_whisper and vosk_model:
            self.recognizer = KaldiRecognizer(vosk_model, 16000)
    
    async def process_audio(self, audio_frame: np.ndarray, sample_rate: int = 16000):
        """
        Process incoming audio frame.
        
        Args:
            audio_frame: Audio data as numpy array
            sample_rate: Audio sample rate
        """
        if self.use_whisper:
            # Buffer audio for batch processing with Whisper
            self.buffer.append(audio_frame)
            
            # Process audio in chunks (every ~5 seconds)
            if len(self.buffer) >= 5:  # Assuming 1-second audio frames
                await self.transcribe_whisper()
        else:
            # Use Vosk for real-time processing
            await self.transcribe_vosk(audio_frame)
    
    async def transcribe_whisper(self):
        """Transcribe audio buffer using Whisper."""
        if not whisper_model or not self.buffer:
            return
        
        # Concatenate audio buffer
        audio = np.concatenate(self.buffer)
        self.buffer = []  # Clear buffer
        
        try:
            # Run Whisper in a separate thread
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: whisper_model.transcribe(audio)
            )
            
            text = result["text"].strip()
            if text:
                transcriptions[self.session_id].append(text)
                logger.info(f"Whisper transcription: {text}")
                
                # Forward to the chatbot for processing
                await self.forward_to_chatbot(text)
                
        except Exception as e:
            logger.error(f"Whisper transcription error: {str(e)}")
    
    async def transcribe_vosk(self, audio_frame: np.ndarray):
        """Transcribe audio frame using Vosk."""
        if not vosk_model:
            return
        
        try:
            # Convert to bytes for Vosk
            audio_data = (audio_frame * 32767).astype('int16').tobytes()
            
            if self.recognizer.AcceptWaveform(audio_data):
                result = json.loads(self.recognizer.Result())
                text = result.get("text", "").strip()
                
                if text:
                    transcriptions[self.session_id].append(text)
                    logger.info(f"Vosk transcription: {text}")
                    
                    # Forward to the chatbot for processing
                    await self.forward_to_chatbot(text)
                    
        except Exception as e:
            logger.error(f"Vosk transcription error: {str(e)}")
    
    async def forward_to_chatbot(self, text: str):
        """Forward transcribed text to the chatbot service."""
        # This will be implemented in the AI chatbot service
        pass

async def get_session_transcriptions(session_id: str) -> List[str]:
    """Get all transcriptions for a session."""
    return transcriptions.get(session_id, [])