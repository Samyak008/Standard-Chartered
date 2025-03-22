import asyncio
import json
import logging
import uuid
import os
import time
from typing import Dict, Optional

from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.media import MediaBlackhole, MediaRecorder
import cv2
import numpy as np

from .face_verification_service import verify_face as verify_face_service
from .audio_service import AudioTranscriber

logger = logging.getLogger(__name__)

# Store active peer connections
peer_connections: Dict[str, RTCPeerConnection] = {}
# Store reference images for face verification
reference_images: Dict[str, np.ndarray] = {}
# Store transcribers
audio_transcribers: Dict[str, AudioTranscriber] = {}

class VideoReceiver:
    """Handles receiving video frames from the client."""
    
    def __init__(self, session_id: str, verification_interval: int = 30):
        """
        Initialize video receiver.
        
        Args:
            session_id: Unique session identifier
            verification_interval: Interval in seconds for face verification
        """
        self.session_id = session_id
        self.verification_interval = verification_interval
        self.frame_count = 0
        self.last_verified = 0
        self.fps = 30  # Assuming 30fps, adjust based on actual frame rate
        
    async def receive_track(self, track: VideoStreamTrack):
        """Process incoming video track."""
        media_recorder = MediaBlackhole()
        
        # Start recording the media
        await media_recorder.start()
        
        try:
            while True:
                frame = await track.recv()
                
                # Convert frame to numpy array for OpenCV processing
                img = frame.to_ndarray(format="bgr24")
                
                # Store the first frame as reference image
                if self.session_id not in reference_images:
                    # Extract a face from the first frame to use as reference
                    face = self._extract_face(img)
                    if face is not None:
                        reference_images[self.session_id] = face
                        logger.info(f"Reference face stored for session {self.session_id}")
                    else:
                        # If no face is detected, use the whole frame
                        reference_images[self.session_id] = img.copy()
                        logger.warning(f"No face detected in reference frame for session {self.session_id}")
                
                # Perform face verification at intervals
                self.frame_count += 1
                frames_per_interval = self.verification_interval * self.fps
                if self.frame_count - self.last_verified >= frames_per_interval:
                    self.last_verified = self.frame_count
                    # Create a task for face verification to avoid blocking
                    asyncio.create_task(self.verify_face(img))
                
        except Exception as e:
            logger.error(f"Error in video processing: {str(e)}")
        finally:
            await media_recorder.stop()
    
    async def verify_face(self, frame: np.ndarray):
        """
        Verify face in the current frame against the reference image.
        
        Args:
            frame: Current video frame
        """
        try:
            # Call the face verification service
            is_verified, confidence = await verify_face_service(self.session_id, frame)
            
            # Log the verification result
            logger.info(f"Face verification for session {self.session_id}: verified={is_verified}, confidence={confidence:.2f}")
            
            # Additional actions based on verification result could be added here
            if not is_verified:
                logger.warning(f"Face verification failed for session {self.session_id}")
                # Could trigger re-authentication or alert
        
        except Exception as e:
            logger.error(f"Error in face verification: {str(e)}")
    
    def _extract_face(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract face from image using multiple detection methods.
        
        Args:
            image: Image containing face
            
        Returns:
            Face image or None if no face detected
        """
        try:
            # Try multiple detection methods for better accuracy
            # 1. Try Haar cascade first (faster)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) > 0:
                # Take the largest face by area
                largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
                x, y, w, h = largest_face
                
                # Add padding around the face (20%)
                padding = int(w * 0.2)
                x_start = max(0, x - padding)
                y_start = max(0, y - padding)
                x_end = min(image.shape[1], x + w + padding)
                y_end = min(image.shape[0], y + h + padding)
                
                # Extract face with padding
                face = image[y_start:y_end, x_start:x_end]
                logger.info(f"Face detected with dimensions: {face.shape}")
                return face
            
            # 2. If Haar cascade fails, try to use the MTCNN from DeepFace 
            # (This is a fallback and will be slower)
            try:
                from deepface import FaceDetector
                faces = FaceDetector.detect_faces(image, detector_backend="opencv")
                if len(faces) > 0:
                    face = faces[0]
                    logger.info(f"Face detected with DeepFace detector")
                    return face
                else:
                    logger.warning(f"No face detected with any method")
                    return None
            except Exception as detector_error:
                logger.error(f"DeepFace detector error: {str(detector_error)}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting face: {str(e)}")
            return None

    # Add recording capability for compliance and audit

    async def start_recording(self, session_id: str):
        """Start recording the session for compliance purposes"""
        output_path = f"recordings/{session_id}_{int(time.time())}.mp4"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        self.media_recorder = MediaRecorder(output_path)
        await self.media_recorder.start()
        logger.info(f"Started recording session {session_id} to {output_path}")
        return output_path

    async def stop_recording(self):
        """Stop recording the session"""
        if hasattr(self, 'media_recorder'):
            await self.media_recorder.stop()
            logger.info("Recording stopped")

class AudioReceiver:
    """Handles receiving audio frames from the client."""
    
    def __init__(self, session_id: str):
        """
        Initialize audio receiver.
        
        Args:
            session_id: Unique session identifier
        """
        self.session_id = session_id
    
    async def receive_track(self, track):
        """Process incoming audio track."""
        transcriber = audio_transcribers.get(self.session_id)
        
        while True:
            try:
                frame = await track.recv()
                
                # Forward to transcriber if available
                if (transcriber):
                    # Convert audio to numpy array
                    audio_array = frame.to_ndarray()
                    await transcriber.process_audio(audio_array)
                
            except Exception as e:
                logger.error(f"Error in audio processing: {str(e)}")
                break

async def create_peer_connection(session_id: str) -> RTCPeerConnection:
    """Create a new WebRTC peer connection."""
    pc = RTCPeerConnection()
    peer_connections[session_id] = pc
    
    # Handle ICE connection state changes
    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        logger.info(f"ICE connection state is {pc.iceConnectionState}")
        if pc.iceConnectionState == "failed" or pc.iceConnectionState == "closed":
            await cleanup_peer_connection(session_id)
    
    return pc

async def cleanup_peer_connection(session_id: str):
    """Clean up and close peer connection."""
    if session_id in peer_connections:
        pc = peer_connections[session_id]
        await pc.close()
        del peer_connections[session_id]
    
    if session_id in reference_images:
        del reference_images[session_id]
    
    if session_id in audio_transcribers:
        del audio_transcribers[session_id]
    
    logger.info(f"Cleaned up session {session_id}")

async def process_offer(session_id: str, offer: RTCSessionDescription) -> RTCSessionDescription:
    """
    Process WebRTC offer and create answer.
    
    Args:
        session_id: Unique session identifier
        offer: SDP offer from client
    
    Returns:
        SDP answer to send back to client
    """
    pc = await create_peer_connection(session_id)
    video_receiver = VideoReceiver(session_id)
    audio_receiver = AudioReceiver(session_id)
    
    @pc.on("track")
    async def on_track(track):
        logger.info(f"Track received: {track.kind}")
        if track.kind == "video":
            asyncio.create_task(video_receiver.receive_track(track))
        elif track.kind == "audio":
            asyncio.create_task(audio_receiver.receive_track(track))
    
    # Set the remote description
    await pc.setRemoteDescription(offer)
    
    # Create answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    
    return pc.localDescription

# Add function to set transcriber for a session
def set_audio_transcriber(session_id: str, transcriber: AudioTranscriber):
    """Set the audio transcriber for a session."""
    audio_transcribers[session_id] = transcriber