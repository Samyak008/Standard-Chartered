import logging
import numpy as np
import asyncio
import time
from typing import Tuple, Dict, Optional
from deepface import DeepFace
import cv2

from .webrtc_service import reference_images

logger = logging.getLogger(__name__)

# Store verification results
verification_results: Dict[str, Dict] = {}

# Configuration
VERIFICATION_THRESHOLD = 0.8  # Confidence threshold for face verification
FACE_DETECTION_MODEL = "opencv"  # Options: opencv, ssd, dlib, mtcnn, retinaface
FACE_RECOGNITION_MODEL = "Facenet"  # Options: VGG-Face, Facenet, OpenFace, DeepFace, etc.

async def verify_face(session_id: str, current_frame: np.ndarray) -> Tuple[bool, float]:
    """
    Verify face in the current frame against the reference image.
    
    Args:
        session_id: Unique session identifier
        current_frame: Current video frame for verification
        
    Returns:
        Tuple of (is_verified, confidence_score)
    """
    if session_id not in reference_images:
        logger.warning(f"No reference image found for session {session_id}")
        return False, 0.0
    
    reference_img = reference_images[session_id]
    
    # Use threaded executor for CPU-bound face verification
    loop = asyncio.get_event_loop()
    try:
        # Run DeepFace in a separate thread to not block the event loop
        result = await loop.run_in_executor(
            None, 
            lambda: DeepFace.verify(
                reference_img,
                current_frame,
                model_name=FACE_RECOGNITION_MODEL,
                detector_backend=FACE_DETECTION_MODEL,
                enforce_detection=False
            )
        )
        
        is_verified = result["verified"]
        distance = result["distance"]
        
        # Convert distance to confidence score (lower distance means higher confidence)
        # This conversion depends on the model used, for Facenet:
        confidence = 1.0 - min(distance / 2.0, 1.0)
        
        # Store result
        verification_results[session_id] = {
            "timestamp": time.time(),
            "verified": is_verified,
            "confidence": confidence
        }
        
        logger.info(f"Face verification for {session_id}: verified={is_verified}, confidence={confidence:.2f}")
        
        return is_verified, confidence
        
    except Exception as e:
        logger.error(f"Face verification error: {str(e)}")
        return False, 0.0

async def get_last_verification_result(session_id: str) -> Optional[Dict]:
    """Get the last verification result for a session."""
    return verification_results.get(session_id)