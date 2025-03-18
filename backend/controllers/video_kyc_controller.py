import asyncio
import json
import logging
import uuid
from typing import Dict, Any, List, Optional
import os

from pydantic import BaseModel
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Body
from starlette.responses import FileResponse
from aiortc import RTCSessionDescription

from backend.services.webrtc_service import process_offer, cleanup_peer_connection, reference_images
from backend.services.face_verification_service import get_last_verification_result
from backend.services.audio_service import AudioTranscriber
from backend.services.video_kyc_service import VideoKYCSession

router = APIRouter()
logger = logging.getLogger(__name__)

# Active Video KYC sessions
active_kyc_sessions: Dict[str, VideoKYCSession] = {}
# Active WebSocket connections
active_ws_connections: Dict[str, WebSocket] = {}

active_sessions: Dict[str, Dict[str, Any]] = {}

# Store conversation logs for each session
conversation_logs: Dict[str, list] = {}

# Models
class SessionRequest(BaseModel):
    loan_type: str
    applicant_info: Dict[str, str]

class Message(BaseModel):
    type: str
    message: str = ""

@router.get("/")
async def get_video_kyc_root():
    """Root endpoint for Video KYC API."""
    return {
        "message": "Video KYC API is available",
        "endpoints": [
            {"path": "/start-session", "method": "POST", "description": "Start a new Video KYC session"},
            {"path": "/ws/rtc/{session_id}", "method": "WebSocket", "description": "WebRTC signaling for video"},
            {"path": "/ws/kyc-conversation/{session_id}", "method": "WebSocket", "description": "KYC conversation flow"}
        ]
    }

@router.post("/start-session")
async def start_video_kyc_session(
    loan_type: str = Body(...),
    applicant_info: Dict[str, Any] = Body(...)
):
    """Initialize a new Video KYC session."""
    try:
        logger.info(f"Starting new Video KYC session with loan_type={loan_type}")
        logger.debug(f"Applicant info: {applicant_info}")
        
        session_id = str(uuid.uuid4())
        logger.info(f"Created new session ID: {session_id}")
        
        # Create a new Video KYC session
        active_kyc_sessions[session_id] = VideoKYCSession(
            session_id=session_id,
            loan_type=loan_type,
            applicant_info=applicant_info
        )
        
        response_data = {
            "session_id": session_id,
            "rtc_websocket_url": f"/api/video-kyc/ws/rtc/{session_id}",
            "conversation_websocket_url": f"/api/video-kyc/ws/kyc-conversation/{session_id}"
        }
        
        logger.info(f"Successfully created KYC session {session_id}")
        return response_data
        
    except Exception as e:
        logger.error(f"Error starting KYC session: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start KYC session: {str(e)}")

@router.websocket("/ws/rtc/{session_id}")
async def rtc_websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for WebRTC signaling in Video KYC."""
    if session_id not in active_kyc_sessions:
        await websocket.close(code=4000, reason="Invalid session ID")
        return
        
    await websocket.accept()
    
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
                
                # Get the KYC session
                kyc_session = active_kyc_sessions.get(session_id)
                if kyc_session:
                    # Initialize audio transcriber for this session
                    kyc_session.audio_transcriber = AudioTranscriber(
                        session_id=session_id,
                        use_whisper=True,
                        callback=kyc_session.process_transcription
                    )
                
                await websocket.send_json({
                    "type": answer.type,
                    "sdp": answer.sdp
                })
                
            elif message["type"] == "disconnect":
                # Handle disconnect request
                await cleanup_peer_connection(session_id)
                break
    
    except WebSocketDisconnect:
        logger.info(f"WebRTC WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebRTC WebSocket error: {str(e)}")
    finally:
        # Clean up session
        await cleanup_peer_connection(session_id)

@router.websocket("/ws/kyc-conversation/{session_id}")
async def kyc_conversation_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for KYC conversation flow."""
    if session_id not in active_kyc_sessions:
        await websocket.close(code=4000, reason="Invalid session ID")
        return
        
    await websocket.accept()
    active_ws_connections[session_id] = websocket
    
    # Get the Video KYC session
    kyc_session = active_kyc_sessions[session_id]
    kyc_session.set_websocket(websocket)
    
    try:
        # Send initial greeting from the KYC agent
        initial_message = await kyc_session.start_conversation()
        await websocket.send_json({
            "type": "agent_message",
            "message": initial_message
        })
        
        # Handle conversation messages
        while True:
            data = await websocket.receive_json()
            
            # Handle manual text input if voice isn't picked up correctly
            if data.get("type") == "manual_input":
                user_message = data.get("message", "").strip()
                if user_message:
                    # Process the manual input as if it came from speech
                    await kyc_session.process_user_message(user_message)
    
    except WebSocketDisconnect:
        logger.info(f"KYC conversation WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"KYC conversation WebSocket error: {str(e)}")
    finally:
        # Clean up the WebSocket connection
        if session_id in active_ws_connections:
            del active_ws_connections[session_id]

@router.get("/sessions/{session_id}/report")
async def get_kyc_session_report(session_id: str) -> Dict[str, Any]:
    """Get report for a completed KYC session."""
    if session_id not in active_kyc_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
        
    kyc_session = active_kyc_sessions[session_id]
    return await kyc_session.generate_report()


@router.get("/client")
async def get_video_kyc_client():
    """Serve the Video KYC client page"""
    return FileResponse("backend/video_kyc_client")

@router.post("/end-session/{session_id}")
async def end_video_kyc_session(session_id: str):
    """End a Video KYC session."""
    if session_id not in active_kyc_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
        
    try:
        # Generate final report
        report = await active_kyc_sessions[session_id].generate_report()
        
        # Clear resources (optional - you might want to keep sessions for reporting)
        # del active_kyc_sessions[session_id]
        
        return {"status": "success", "message": "Session ended successfully"}
    except Exception as e:
        logger.error(f"Error ending KYC session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to end KYC session: {str(e)}")