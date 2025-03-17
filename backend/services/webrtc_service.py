import asyncio
import json
import logging
import uuid
from typing import Dict, Optional

from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.media import MediaBlackhole, MediaRecorder
import cv2
import numpy as np

logger = logging.getLogger(__name__)

# Store active peer connections
peer_connections: Dict[str, RTCPeerConnection] = {}
# Store reference images for face verification
reference_images: Dict[str, np.ndarray] = {}

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
                    reference_images[self.session_id] = img.copy()
                    logger.info(f"Reference image stored for session {self.session_id}")
                
                # Perform face verification at intervals
                self.frame_count += 1
                if self.frame_count - self.last_verified >= self.verification_interval * 30:  # Assuming 30fps
                    self.last_verified = self.frame_count
                    # This will be handled by face_verification_service
                    asyncio.create_task(self.verify_face(img))
                
        except Exception as e:
            logger.error(f"Error in video processing: {str(e)}")
        finally:
            await media_recorder.stop()
    
    async def verify_face(self, frame: np.ndarray):
        """
        Placeholder for face verification.
        Will be implemented by face_verification_service.
        """
        # This is a stub - actual implementation will be in face_verification_service
        pass

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
    
    @pc.on("track")
    async def on_track(track):
        logger.info(f"Track received: {track.kind}")
        if track.kind == "video":
            asyncio.create_task(video_receiver.receive_track(track))
    
    # Set the remote description
    await pc.setRemoteDescription(offer)
    
    # Create answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    
    return pc.localDescription