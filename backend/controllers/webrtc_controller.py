import asyncio
import json
import logging
import uuid
from typing import Dict, Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from aiortc import RTCSessionDescription

from ..services.webrtc_service import process_offer, cleanup_peer_connection
from ..services.face_verification_service import verify_face, get_last_verification_result
from ..services.audio_service import AudioTranscriber
from ..services.ai_chatbot_service import LoanAdvisorBot

router = APIRouter()
logger = logging.getLogger(__name__)

# Active websocket connections
active_connections: Dict[str, WebSocket] = {}

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
                await websocket.send_json({
                    "type": "verification_result",
                    "verified": verification_result["verified"],
                    "confidence": verification_result["confidence"],
                    "timestamp": verification_result["timestamp"]
                })
            
            # Wait before sending next update
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        logger.info(f"Face verification WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"Face verification WebSocket error: {str(e)}")