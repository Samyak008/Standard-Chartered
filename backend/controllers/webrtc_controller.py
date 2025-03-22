import asyncio
import json
import logging
import uuid
from typing import Dict, Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Body
from aiortc import RTCSessionDescription

# Update imports to include the missing functions
from backend.services.webrtc_service import process_offer, cleanup_peer_connection
from backend.services.face_verification_service import (
    verify_face, 
    get_last_verification_result, 
    get_consecutive_failures,   # Add this import
    should_trigger_reauth       # Add this import
)
from backend.services.audio_service import AudioTranscriber
from backend.services.ai_chatbot_service import LoanAdvisorBot

router = APIRouter()
logger = logging.getLogger(__name__)

# Active websocket connections
active_connections: Dict[str, WebSocket] = {}

@router.get("/")
async def get_webrtc_root():
    """Root endpoint for WebRTC API."""
    return {
        "message": "WebRTC API is available",
        "endpoints": [
            {"path": "/start-video-call", "method": "POST", "description": "Start a new video call session"},
            {"path": "/ws/rtc/{session_id}", "method": "WebSocket", "description": "WebSocket endpoint for WebRTC signaling"},
            {"path": "/ws/verify-face-live/{session_id}", "method": "WebSocket", "description": "WebSocket for live face verification feedback"}
        ]
    }

@router.websocket("/ws/rtc/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for WebRTC signaling.
    
    Args:
        websocket: WebSocket connection
        session_id: Session identifier
    """
    await websocket.accept()
    active_connections[session_id] = websocket
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message["type"] == "offer":
                # Process WebRTC offer
                offer = RTCSessionDescription(sdp=message["sdp"], type=message["type"])
                answer = await process_offer(session_id, offer)
                
                await websocket.send_json({
                    "type": answer.type,
                    "sdp": answer.sdp
                })
                
            elif message["type"] == "ice_candidate":
                # Handle ICE candidate
                # Implementation depends on specific requirements
                pass
                
            elif message["type"] == "disconnect":
                # Handle disconnect request
                await cleanup_peer_connection(session_id)
                break
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        # Clean up session and connection
        await cleanup_peer_connection(session_id)
        if session_id in active_connections:
            del active_connections[session_id]

@router.post("/start-video-call")
async def start_video_call() -> Dict[str, Any]:
    """
    Initialize a new video call session.
    
    Returns:
        Dict with session_id for the client to connect to WebSocket
    """
    session_id = str(uuid.uuid4())
    return {
        "session_id": session_id,
        "websocket_url": f"/ws/rtc/{session_id}"
    }

@router.websocket("/ws/verify-face-live/{session_id}")
async def face_verification_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for live face verification feedback.
    
    Args:
        websocket: WebSocket connection
        session_id: Session identifier
    """
    await websocket.accept()
    
    try:
        # Send verification results every 5 seconds
        while True:
            verification_result = await get_last_verification_result(session_id)
            
            if verification_result:
                response_data = {
                    "type": "verification_result",
                    "verified": verification_result["verified"],
                    "confidence": verification_result["confidence"],
                    "timestamp": verification_result["timestamp"]
                }
                
                # Add error message if present
                if "error" in verification_result:
                    response_data["error"] = verification_result["error"]
                
                # Add warning for consecutive failures
                consecutive_failures = await get_consecutive_failures(session_id)
                if consecutive_failures > 0:
                    response_data["consecutive_failures"] = consecutive_failures
                
                # Check if re-authentication should be triggered
                if await should_trigger_reauth(session_id):
                    response_data["action_required"] = "re_authenticate"
                
                await websocket.send_json(response_data)
            
            # Wait before sending next update
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        logger.info(f"Face verification WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"Face verification WebSocket error: {str(e)}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass

@router.post("/set-reference-image/{session_id}")
async def set_reference_image(session_id: str, data: Dict[str, str] = Body(...)):
    """Set a reference image for face verification"""
    try:
        # Get base64 encoded image
        image_base64 = data.get("image")
        if not image_base64:
            return {"success": False, "error": "No image provided"}
            
        # Convert base64 to numpy array
        import base64
        import numpy as np
        import cv2
        
        img_data = base64.b64decode(image_base64)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Store as reference image
        from backend.services.webrtc_service import reference_images
        reference_images[session_id] = img
        
        return {"success": True}
    except Exception as e:
        logger.error(f"Error setting reference image: {str(e)}")
        return {"success": False, "error": str(e)}

@router.websocket("/ws/chat/{session_id}")
async def chat_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for loan advisor chat.
    
    Args:
        websocket: WebSocket connection
        session_id: Session identifier
    """
    await websocket.accept()
    
    # Initialize chatbot for this session
    chatbot = LoanAdvisorBot(session_id)
    
    try:
        await websocket.send_json({
            "type": "message",
            "text": "Welcome to Standard Chartered's Virtual Loan Advisor. How can I help you today?"
        })
        
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "message":
                user_message = data.get("text", "").strip()
                
                if user_message:
                    # Process user message and get response
                    response = await chatbot.process_message(user_message)
                    
                    # Send response back to client
                    await websocket.send_json({
                        "type": "message",
                        "text": response
                    })
    
    except WebSocketDisconnect:
        logger.info(f"Chat WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"Chat WebSocket error: {str(e)}")