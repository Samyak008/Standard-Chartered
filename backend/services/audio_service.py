import asyncio
import logging
import numpy as np
import whisper
from typing import Dict, Optional, List, Callable
from vosk import Model, KaldiRecognizer
import json
import os
import sys
import ctypes
import platform
from pathlib import Path
import tempfile
from datetime import datetime

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
    
    def __init__(self, session_id: str, use_whisper: bool = False, callback: Optional[Callable] = None):
        """
        Initialize audio transcriber.
        
        Args:
            session_id: Unique session identifier
            use_whisper: Whether to use Whisper (more accurate but slower) over Vosk
            callback: Optional callback function to process transcribed text
        """
        self.session_id = session_id
        self.use_whisper = use_whisper
        self.callback = callback
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
                
                # Forward to the callback for processing
                if self.callback:
                    await self.callback(text)
                
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
                    
                    # Forward to the callback for processing
                    if self.callback:
                        await self.callback(text)
                    
        except Exception as e:
            logger.error(f"Vosk transcription error: {str(e)}")

    async def process_audio_with_openai(self, audio_data: bytes) -> str:
        """Use OpenAI Whisper API for better transcription when network is available"""
        try:
            from openai import OpenAI
            client = OpenAI()
            
            # Save temporary audio file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            # Use OpenAI API
            with open(temp_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            
            # Clean up temp file
            os.unlink(temp_path)
            
            return transcript.text
            
        except Exception as e:
            logger.error(f"OpenAI Whisper API error: {str(e)}")
            # Fall back to local Whisper if API fails
            if whisper_model:
                return self.transcribe_whisper_local(audio_data)
            return ""

    async def transcribe_audio(self, audio_data: bytes, session_id: str) -> str:
        """Transcribe audio using Whisper model"""
        try:
            # Save temporary audio file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            logging.info(f"Processing audio file: {temp_path}")
            
            # Transcribe with Whisper
            result = self.model.transcribe(temp_path)
            transcript = result["text"]
            
            # Save transcription to JSON file
            self._save_transcription(transcript, session_id)
            
            # Clean up temp file
            os.unlink(temp_path)
            
            return transcript
            
        except Exception as e:
            logging.error(f"Error transcribing audio: {str(e)}")
            return f"Transcription error: {str(e)}"
    
    def _save_transcription(self, transcript: str, session_id: str):
        """Save transcription to a JSON file"""
        try:
            # Create transcripts directory if it doesn't exist
            os.makedirs("transcripts", exist_ok=True)
            
            # Create a JSON object with metadata
            transcription_data = {
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "transcript": transcript
            }
            
            # Save to a JSON file named with the session ID
            file_path = f"transcripts/transcript_{session_id}.json"
            with open(file_path, "w") as f:
                json.dump(transcription_data, f, indent=4)
            
            logging.info(f"Transcription saved to {file_path}")
            
        except Exception as e:
            logging.error(f"Error saving transcription: {str(e)}")

    def __init__(self, session_id=None):
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.audio_chunks = []
        self.transcription = ""
        # Initialize whisper model once
        try:
            self.model = whisper.load_model("base")
            logging.info(f"Whisper model loaded successfully")
        except Exception as e:
            logging.error(f"Error loading Whisper model: {str(e)}")
            self.model = None
    
    async def process_audio_chunk(self, audio_data):
        """Store audio chunk for later processing"""
        self.audio_chunks.append(audio_data)
        return None  # Real-time transcription disabled for better performance
    
    async def transcribe_all(self):
        """Transcribe all stored audio chunks at once"""
        if not self.audio_chunks:
            return "No audio data available for transcription"
        
        try:
            # Save all audio to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                for chunk in self.audio_chunks:
                    temp_file.write(chunk)
                temp_path = temp_file.name
            
            # Use whisper for transcription
            if self.model:
                result = self.model.transcribe(temp_path)
                self.transcription = result["text"]
            else:
                self.transcription = "Transcription failed: Whisper model not available"
            
            # Save transcription to JSON file
            output_dir = Path("transcriptions")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"{self.session_id}_transcription.json"
            
            with open(output_path, "w") as f:
                json.dump({
                    "session_id": self.session_id,
                    "timestamp": datetime.now().isoformat(),
                    "transcription": self.transcription
                }, f, indent=2)
                
            logging.info(f"Transcription saved to {output_path}")
            
            # Clean up temp file
            os.unlink(temp_path)
            
            return self.transcription
            
        except Exception as e:
            error_msg = f"Error in transcription process: {str(e)}"
            logging.error(error_msg)
            return error_msg

async def get_session_transcriptions(session_id: str) -> List[str]:
    """Get all transcriptions for a session."""
    return transcriptions.get(session_id, [])

def load_whisper():
    # Set up library paths based on OS
    if platform.system() == 'Windows':
        lib_path = os.path.join(sys.prefix, 'Library', 'bin')
        if os.path.exists(lib_path):
            os.add_dll_directory(lib_path)
        
        # Add Windows system directory
        os.add_dll_directory(os.path.join(os.environ['SystemRoot'], 'System32'))
        
    # Initialize whisper model
    try:
        model = whisper.load_model("base")
        return model
    except Exception as e:
        print(f"Error loading Whisper model: {str(e)}")
        return None

def transcribe_audio(audio_file_path, model=None):
    if model is None:
        model = load_whisper()
    
    if model is None:
        raise RuntimeError("Failed to load Whisper model")
        
    try:
        result = model.transcribe(audio_file_path)
        return result["text"]
    except Exception as e:
        print(f"Error transcribing audio: {str(e)}")
        raise

import base64

# Try to import whisper, fallback to a placeholder if not available
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logging.warning("Whisper not available, transcription will be limited")

class AudioTranscriber:
    def __init__(self, session_id=None):
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.audio_chunks = []
        self.transcription = ""
        self.model = None
        
        # Initialize whisper model if available
        if WHISPER_AVAILABLE:
            try:
                self.model = whisper.load_model("base")
                logging.info(f"Whisper model loaded successfully")
            except Exception as e:
                logging.error(f"Error loading Whisper model: {str(e)}")
    
    async def process_audio_chunk(self, audio_data):
        """Store audio chunk for later processing"""
        try:
            # Decode base64 data
            binary_data = base64.b64decode(audio_data)
            logging.info(f"Received audio chunk: {len(binary_data)} bytes")
            self.audio_chunks.append(binary_data)
            return True
        except Exception as e:
            logging.error(f"Error processing audio chunk: {str(e)}")
            return False
    
    async def transcribe_all(self):
        """Transcribe all stored audio chunks at once"""
        if not self.audio_chunks:
            logging.warning("No audio data available for transcription")
            return "No audio data available for transcription"
        
        logging.info(f"Transcribing {len(self.audio_chunks)} audio chunks")
        
        try:
            # Create transcriptions directory if it doesn't exist
            output_dir = Path("transcriptions")
            output_dir.mkdir(exist_ok=True)
            
            # Save all audio to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
                for chunk in self.audio_chunks:
                    temp_file.write(chunk)
            
            logging.info(f"Saved audio to temporary file: {temp_path}")
            
            # Use whisper for transcription if available
            if self.model:
                logging.info("Starting Whisper transcription...")
                result = self.model.transcribe(temp_path)
                self.transcription = result["text"]
                logging.info(f"Transcription complete: {self.transcription[:100]}...")
            else:
                self.transcription = "Transcription unavailable: Whisper model not loaded"
                logging.warning("Transcription unavailable: Whisper model not loaded")
            
            # Save transcription to JSON file
            output_path = output_dir / f"{self.session_id}_transcription.json"
            
            with open(output_path, "w") as f:
                json.dump({
                    "session_id": self.session_id,
                    "timestamp": datetime.now().isoformat(),
                    "transcription": self.transcription,
                    "audio_chunks": len(self.audio_chunks),
                    "total_audio_bytes": sum(len(chunk) for chunk in self.audio_chunks)
                }, f, indent=2)
                
            logging.info(f"Transcription saved to {output_path}")
            
            # Clean up temp file
            os.unlink(temp_path)
            
            return self.transcription
            
        except Exception as e:
            error_msg = f"Error in transcription process: {str(e)}"
            logging.error(error_msg)
            return error_msg

import os
import json
import base64
import logging
import tempfile
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AudioTranscriber:
    def __init__(self, session_id=None):
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.audio_chunks = []
        
        # Create transcriptions directory
        os.makedirs("transcriptions", exist_ok=True)
        logger.info(f"AudioTranscriber initialized with session ID: {self.session_id}")
    
    async def process_audio_chunk(self, audio_data):
        """Store audio chunk for later processing"""
        try:
            # Decode base64 data
            binary_data = base64.b64decode(audio_data)
            logger.info(f"Received audio chunk: {len(binary_data)} bytes")
            self.audio_chunks.append(binary_data)
            return True
        except Exception as e:
            logger.error(f"Error processing audio chunk: {str(e)}")
            return False
    
    async def transcribe_all(self):
        """Create a simple transcription"""
        if not self.audio_chunks:
            logger.warning("No audio chunks to transcribe!")
            return "No audio data received"
        
        logger.info(f"Processing {len(self.audio_chunks)} audio chunks for transcription")
        
        try:
            # Save raw audio to a file
            audio_path = os.path.join("transcriptions", f"{self.session_id}_audio.webm")
            with open(audio_path, "wb") as f:
                for chunk in self.audio_chunks:
                    f.write(chunk)
            
            logger.info(f"Saved raw audio to {os.path.abspath(audio_path)}")
            
            # Create a simple JSON transcription for debugging
            json_path = os.path.join("transcriptions", f"{self.session_id}_transcription.json")
            
            # Simple placeholder transcription
            transcription = f"[Test transcription for call {self.session_id}]"
            
            with open(json_path, "w") as f:
                json.dump({
                    "session_id": self.session_id,
                    "timestamp": datetime.now().isoformat(),
                    "audio_chunks": len(self.audio_chunks),
                    "total_bytes": sum(len(chunk) for chunk in self.audio_chunks),
                    "transcription": transcription
                }, f, indent=2)
            
            logger.info(f"Saved debug transcription to {os.path.abspath(json_path)}")
            return transcription
            
        except Exception as e:
            error_msg = f"Error in transcription: {str(e)}"
            logger.error(error_msg)
            return error_msg

import os
import json
import base64
import logging
import tempfile
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("audio")

# Import whisper
try:
    import whisper
    WHISPER_AVAILABLE = True
    logger.info("Whisper imported successfully")
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("Whisper not available, trying to install...")
    try:
        import subprocess
        subprocess.check_call(["pip", "install", "openai-whisper"])
        import whisper
        WHISPER_AVAILABLE = True
        logger.info("Whisper installed successfully")
    except Exception as e:
        logger.error(f"Failed to install Whisper: {e}")

class AudioTranscriber:
    def __init__(self, session_id=None):
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.audio_chunks = []
        self.model = None
        
        # Create transcriptions directory
        os.makedirs("transcriptions", exist_ok=True)
        
        # Initialize whisper model
        if WHISPER_AVAILABLE:
            try:
                # Load the smallest model for faster processing
                self.model = whisper.load_model("tiny")
                logger.info(f"Whisper model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading Whisper model: {str(e)}")
        else:
            logger.warning("Whisper is not available, transcription will be limited")
    
    async def process_audio_chunk(self, audio_data):
        """Store audio chunk for later processing"""
        try:
            # Decode base64 data
            binary_data = base64.b64decode(audio_data)
            logger.info(f"Received audio chunk: {len(binary_data)} bytes")
            self.audio_chunks.append(binary_data)
            return True
        except Exception as e:
            logger.error(f"Error processing audio chunk: {str(e)}")
            return False
    
    async def transcribe_all(self):
        """Transcribe all stored audio chunks at once using Whisper"""
        if not self.audio_chunks:
            logger.warning("No audio chunks to transcribe!")
            return "No audio data received"
        
        logger.info(f"Processing {len(self.audio_chunks)} audio chunks for transcription")
        
        try:
            # Save raw audio to a file
            audio_path = os.path.join("transcriptions", f"{self.session_id}_audio.webm")
            with open(audio_path, "wb") as f:
                for chunk in self.audio_chunks:
                    f.write(chunk)
            
            logger.info(f"Saved raw audio to {os.path.abspath(audio_path)}")
            
            # Create temporary wav file for Whisper
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
                for chunk in self.audio_chunks:
                    temp_file.write(chunk)
            
            # Transcribe with Whisper
            transcription = "No transcription available"
            if WHISPER_AVAILABLE and self.model:
                logger.info("Starting Whisper transcription...")
                try:
                    result = self.model.transcribe(temp_path)
                    transcription = result["text"]
                    logger.info(f"Whisper transcription complete: {transcription[:100]}...")
                except Exception as e:
                    logger.error(f"Error during Whisper transcription: {e}")
                    transcription = f"Transcription error: {str(e)}"
            else:
                transcription = "Whisper model not available"
            
            # Create a JSON file with the transcription
            json_path = os.path.join("transcriptions", f"{self.session_id}_transcription.json")
            
            with open(json_path, "w") as f:
                json.dump({
                    "session_id": self.session_id,
                    "timestamp": datetime.now().isoformat(),
                    "audio_chunks": len(self.audio_chunks),
                    "total_bytes": sum(len(chunk) for chunk in self.audio_chunks),
                    "transcription": transcription
                }, f, indent=2)
            
            logger.info(f"Saved transcription to {os.path.abspath(json_path)}")
            
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
                
            return transcription
            
        except Exception as e:
            error_msg = f"Error in transcription: {str(e)}"
            logger.error(error_msg)
            return error_msg

import os
import json
import base64
import logging
import tempfile
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Try to import whisper
try:
    import whisper
    WHISPER_AVAILABLE = True
    logger.info("✅ Whisper imported successfully")
except ImportError:
    WHISPER_AVAILABLE = False
    logger.error("⚠️ Whisper not available!")

class AudioTranscriber:
    def __init__(self, session_id=None):
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.audio_chunks = []
        self.model = None
        
        # Create transcriptions directory
        os.makedirs("transcriptions", exist_ok=True)
        
        # Initialize whisper model
        if WHISPER_AVAILABLE:
            try:
                self.model = whisper.load_model("base")
                logger.info(f"✅ Whisper model loaded successfully for session {self.session_id}")
            except Exception as e:
                logger.error(f"❌ Error loading Whisper model: {str(e)}")
        
        logger.info(f"📱 AudioTranscriber initialized with session_id: {self.session_id}")
    
    async def process_audio_chunk(self, audio_data):
        """Store audio chunk for later processing"""
        try:
            # Decode base64 data
            binary_data = base64.b64decode(audio_data)
            logger.info(f"📥 Session {self.session_id}: Received audio chunk: {len(binary_data)} bytes")
            self.audio_chunks.append(binary_data)
            return True
        except Exception as e:
            logger.error(f"❌ Error processing audio chunk: {str(e)}")
            return False
    
    async def transcribe_all(self):
        """Transcribe all stored audio chunks at once"""
        if not self.audio_chunks:
            logger.warning(f"⚠️ Session {self.session_id}: No audio data available for transcription")
            return "No audio data available for transcription"
        
        logger.info(f"🎯 Session {self.session_id}: Transcribing {len(self.audio_chunks)} audio chunks")
        
        try:
            # Save all audio to a file (for debugging)
            audio_path = os.path.join("transcriptions", f"{self.session_id}_audio.webm")
            with open(audio_path, "wb") as f:
                for chunk in self.audio_chunks:
                    f.write(chunk)
            
            logger.info(f"💾 Saved audio to file: {os.path.abspath(audio_path)}")
            
            # Save to a temporary file for processing
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_file:
                temp_path = temp_file.name
                for chunk in self.audio_chunks:
                    temp_file.write(chunk)
            
            # Transcribe with Whisper
            if WHISPER_AVAILABLE and self.model:
                try:
                    logger.info(f"🔍 Starting Whisper transcription for session {self.session_id}...")
                    result = self.model.transcribe(temp_path)
                    transcription = result["text"]
                    logger.info(f"✅ Transcription complete: {transcription[:100]}...")
                except Exception as e:
                    logger.error(f"❌ Whisper transcription error: {str(e)}")
                    transcription = f"Error during transcription: {str(e)}"
            else:
                transcription = "Whisper model not available"
                logger.warning("⚠️ Whisper model not available, skipping transcription")
            
            # Save transcription to JSON file
            json_path = os.path.join("transcriptions", f"{self.session_id}_transcription.json")
            
            with open(json_path, "w") as f:
                json.dump({
                    "session_id": self.session_id,
                    "timestamp": datetime.now().isoformat(),
                    "transcription": transcription,
                    "audio_chunks_count": len(self.audio_chunks),
                    "total_bytes": sum(len(chunk) for chunk in self.audio_chunks)
                }, f, indent=2)
                
            logger.info(f"📄 Transcription saved to {os.path.abspath(json_path)}")
            
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.error(f"Error removing temp file: {str(e)}")
            
            return transcription
            
        except Exception as e:
            error_msg = f"❌ Error in transcription process: {str(e)}"
            logger.error(error_msg)
            return error_msg