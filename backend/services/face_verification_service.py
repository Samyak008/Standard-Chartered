import logging
import numpy as np
import asyncio
import time
from typing import Tuple, Dict, Optional
from deepface import DeepFace
import cv2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Avoid circular import
# Instead of importing reference_images directly, we'll define a function to get them
logger = logging.getLogger(__name__)

# Store verification results
verification_results: Dict[str, Dict] = {}

# Configuration from .env
VERIFICATION_THRESHOLD = float(os.getenv("VERIFICATION_THRESHOLD", "0.8"))
FACE_DETECTION_MODEL = os.getenv("FACE_DETECTION_MODEL", "opencv")
FACE_RECOGNITION_MODEL = os.getenv("FACE_RECOGNITION_MODEL", "Facenet")

# Function to get reference images from another module
def get_reference_image(session_id: str) -> Optional[np.ndarray]:
    """Get reference image for a session."""
    # Importing here to avoid circular imports
    from backend.services.webrtc_service import reference_images
    return reference_images.get(session_id)

async def verify_face(session_id: str, current_frame: np.ndarray) -> Tuple[bool, float]:
    """
    Verify face in the current frame against the reference image.
    
    Args:
        session_id: Unique session identifier
        current_frame: Current video frame for verification
        
    Returns:
        Tuple of (is_verified, confidence_score)
    """
    reference_img = get_reference_image(session_id)
    if reference_img is None:
        logger.warning(f"No reference image found for session {session_id}")
        return False, 0.0
    
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