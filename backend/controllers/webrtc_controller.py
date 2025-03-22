import asyncio
import json
import logging
import uuid
import traceback
from typing import Dict, Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Body
from aiortc import RTCSessionDescription, RTCPeerConnection, MediaStreamTrack

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
audio_data = {}  # Store audio data for each session
transcriber = AudioTranscriber()

class AudioReceiver(MediaStreamTrack):
    kind = "audio"
    
    def __init__(self, track, session_id):
        super().__init__()
        self.track = track
        self.session_id = session_id
        
        # Initialize buffer for this session if it doesn't exist
        if session_id not in audio_data:
            audio_data[session_id] = bytearray()
    
    async def recv(self):
        frame = await self.track.recv()
        
        # Store audio data in the buffer
        if hasattr(frame, "to_ndarray"):
            audio_samples = frame.to_ndarray()
            # Convert audio samples to bytes and append to buffer
            audio_data[self.session_id].extend(audio_samples.tobytes())
        
        return frame

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
async def websocket_rtc(websocket: WebSocket, session_id: str):
    await websocket.accept()
    logger.info(f"📱 New WebSocket connection established for session {session_id}")
    
    try:
        # Create transcriber with session_id
        transcriber = AudioTranscriber(session_id)
        
        # Store connection and transcriber in active_connections
        active_connections[session_id] = {
            "websocket": websocket,
            "transcriber": transcriber
        }
        
        logger.info(f"✅ Session {session_id} registered in active_connections, total sessions: {len(active_connections)}")
        
        # Log the status of active_connections
        logger.info(f"Active sessions: {list(active_connections.keys())}")
        
        # Main message handling loop
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle audio data for transcription
            if message.get("type") == "audio":
                audio_data = message.get("data")
                if audio_data:
                    # Process audio chunk
                    await transcriber.process_audio_chunk(audio_data)
            elif message.get("type") == "disconnect":
                # Handle disconnect message
                logger.info(f"🔌 Received disconnect request for session {session_id}")
                break
            else:
                # Echo other messages back (signaling)
                await websocket.send_text(data)
    
    except WebSocketDisconnect:
        logger.warning(f"🔌 WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"❌ WebSocket error for session {session_id}: {str(e)}")
        logger.error(traceback.format_exc())
    finally:
        logger.info(f"WebSocket loop ended for session {session_id}")
        # Note: Don't remove from active_connections here - we need it for the end-call endpoint

@router.post("/start-video-call")
async def start_video_call() -> Dict[str, Any]:
    """Initialize a new video call session."""
    session_id = str(uuid.uuid4())
    return {
        "session_id": session_id,
        "websocket_url": f"/ws/rtc/{session_id}"
    }

@router.websocket("/ws/verify-face-live/{session_id}")
async def face_verification_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for live face verification feedback."""
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
    """WebSocket endpoint for loan advisor chat."""
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

@router.get("/end-call/{session_id}")
async def end_call(session_id: str):
    """End call and get transcription"""
    logger.info(f"📞 End call requested for session {session_id}")
    logger.info(f"Active sessions: {list(active_connections.keys())}")
    
    if session_id not in active_connections:
        logger.warning(f"⚠️ Session {session_id} not found in active_connections!")
        # For debugging purposes, return a 200 response instead of 404
        return {
            "success": False,
            "session_id": session_id,
            "error": "Session not found",
            "active_sessions": list(active_connections.keys())
        }
    
    try:
        connection = active_connections[session_id]
        transcriber = connection["transcriber"]
        
        # Generate final transcription
        logger.info(f"Starting transcription for session {session_id}")
        transcript = await transcriber.transcribe_all()
        logger.info(f"Transcription completed for session {session_id}")
        
        # Send transcription to client
        try:
            websocket = connection["websocket"]
            await websocket.send_text(json.dumps({
                "type": "transcription",
                "transcript": transcript
            }))
            logger.info(f"Sent transcription to client for session {session_id}")
        except Exception as e:
            logger.error(f"Error sending transcription: {str(e)}")
        
        # Return response
        return {
            "success": True, 
            "session_id": session_id, 
            "transcript": transcript
        }
    except Exception as e:
        logger.error(f"Error in end_call: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "success": False,
            "session_id": session_id,
            "error": str(e)
        }
    finally:
        # Clean up connection
        if session_id in active_connections:
            del active_connections[session_id]
            logger.info(f"Removed session {session_id} from active connections")