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

logger = logging.getLogger(__name__)

# Store verification results
verification_results: Dict[str, Dict] = {}

# Configuration from .env - use stricter default threshold
# Check both possible environment variable names with fallback
threshold_str = os.getenv("VERIFICATION_THRESHOLD", 
                         os.getenv("FACE_VERIFICATION_THRESHOLD", "0.6"))
try:
    # Try to parse just the number from the string
    threshold_value = threshold_str.split('#')[0].strip() if '#' in threshold_str else threshold_str.strip()
    VERIFICATION_THRESHOLD = float(threshold_value)
except (ValueError, AttributeError):
    # Default fallback if there's an error
    VERIFICATION_THRESHOLD = 0.6
    logger.warning(f"Could not parse threshold value '{threshold_str}', using default: {VERIFICATION_THRESHOLD}")

FACE_DETECTION_MODEL = os.getenv("FACE_DETECTION_MODEL", "opencv")
FACE_RECOGNITION_MODEL = os.getenv("FACE_RECOGNITION_MODEL", "Facenet")

logger.info(f"Face verification configured with: threshold={VERIFICATION_THRESHOLD}, " + 
            f"detection_model={FACE_DETECTION_MODEL}, recognition_model={FACE_RECOGNITION_MODEL}")

# Add a global counter for consecutive failures
consecutive_failures: Dict[str, int] = {}
MAX_CONSECUTIVE_FAILURES = 3

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
        verification_results[session_id] = {
            "timestamp": time.time(),
            "verified": False,
            "confidence": 0.0,
            "error": "No reference image found"
        }
        return False, 0.0
    
    # Use threaded executor for CPU-bound face verification
    loop = asyncio.get_event_loop()
    try:
        # First check if there's a face in the current frame
        faces_detected = await detect_faces(current_frame)
        if not faces_detected:
            logger.warning(f"No face detected in current frame for session {session_id}")
            verification_results[session_id] = {
                "timestamp": time.time(),
                "verified": False,
                "confidence": 0.0,
                "error": "No face detected in current frame"
            }
            # Increment consecutive failures
            consecutive_failures[session_id] = consecutive_failures.get(session_id, 0) + 1
            return False, 0.0
            
        # Run DeepFace in a separate thread to not block the event loop
        result = await loop.run_in_executor(
            None, 
            lambda: DeepFace.verify(
                reference_img,
                current_frame,
                model_name=FACE_RECOGNITION_MODEL,
                detector_backend=FACE_DETECTION_MODEL,
                enforce_detection=True,  # Changed to True for stricter detection
                distance_metric="cosine"  # More robust distance metric
            )
        )
        
        is_verified = result["verified"]
        distance = result["distance"]
        
        # Convert distance to confidence score (lower distance means higher confidence)
        # This conversion depends on the model used, for Facenet:
        confidence = 1.0 - min(distance / 1.0, 1.0)  # Adjusted scale for more accurate representation
        
        # Apply stricter verification threshold
        is_verified = confidence >= VERIFICATION_THRESHOLD
        
        # Store result with additional metadata
        verification_results[session_id] = {
            "timestamp": time.time(),
            "verified": is_verified,
            "confidence": confidence,
            "distance": distance,
            "threshold": VERIFICATION_THRESHOLD
        }
        
        if is_verified:
            # Reset consecutive failures on successful verification
            consecutive_failures[session_id] = 0
        else:
            # Increment consecutive failures
            consecutive_failures[session_id] = consecutive_failures.get(session_id, 0) + 1
        
        logger.info(f"Face verification for {session_id}: verified={is_verified}, confidence={confidence:.2f}, threshold={VERIFICATION_THRESHOLD}")
        
        return is_verified, confidence
        
    except Exception as e:
        logger.error(f"Face verification error: {str(e)}")
        verification_results[session_id] = {
            "timestamp": time.time(),
            "verified": False,
            "confidence": 0.0,
            "error": str(e)
        }
        return False, 0.0

async def detect_faces(image: np.ndarray) -> bool:
    """
    Detect if there are any faces in the image.
    
    Args:
        image: Image to check for faces
    
    Returns:
        Boolean indicating if faces were detected
    """
    try:
        # Use OpenCV's Haar cascade for quick face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        return len(faces) > 0
    except Exception as e:
        logger.error(f"Error detecting faces: {str(e)}")
        return False

async def get_last_verification_result(session_id: str) -> Optional[Dict]:
    """Get the last verification result for a session."""
    return verification_results.get(session_id)

async def get_consecutive_failures(session_id: str) -> int:
    """Get the number of consecutive verification failures."""
    return consecutive_failures.get(session_id, 0)

async def should_trigger_reauth(session_id: str) -> bool:
    """Check if re-authentication should be triggered based on consecutive failures."""
    return consecutive_failures.get(session_id, 0) >= MAX_CONSECUTIVE_FAILURES