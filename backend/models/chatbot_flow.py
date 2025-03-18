from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from langchain import ConversationChain
from langchain.prompts import PromptTemplate
from typing import Dict, Any

router = APIRouter()

# In-memory storage for user sessions
user_sessions: Dict[str, Dict[str, Any]] = {}

# Define a prompt template for LangChain
prompt_template = PromptTemplate(
    input_variables=["user_input", "aadhar_details", "pan_details", "income"],
    template=(
        "You are a KYC agent. Validate the user's response based on the following details:\n"
        "Aadhar Details: {aadhar_details}\n"
        "PAN Details: {pan_details}\n"
        "Income: {income}\n"
        "User's response: {user_input}\n"
        "Ask follow-up questions based on the user's response."
    )
)

@router.websocket("/ws/kyc/{session_id}")
async def kyc_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    # Receive initial details from the frontend
    initial_data = await websocket.receive_json()
    aadhar_details = initial_data.get("aadhar_details")
    pan_details = initial_data.get("pan_details")
    income = initial_data.get("income")

    # Initialize user session with constant details
    user_sessions[session_id] = {
        "conversation_chain": ConversationChain(prompt_template=prompt_template),
        "aadhar_details": aadhar_details,
        "pan_details": pan_details,
        "income": income,
    }

    try:
        while True:
            data = await websocket.receive_json()
            user_input = data.get("user_input", "").strip()

            # Get the conversation chain and details for the session
            session_data = user_sessions[session_id]
            conversation_chain = session_data["conversation_chain"]
            aadhar_details = session_data["aadhar_details"]
            pan_details = session_data["pan_details"]
            income = session_data["income"]

            # Generate a follow-up question based on user input and context
            follow_up_question = conversation_chain.run(
                user_input=user_input,
                aadhar_details=aadhar_details,
                pan_details=pan_details,
                income=income
            )

            # Send the follow-up question to the client
            await websocket.send_json({"follow_up_question": follow_up_question})

    except WebSocketDisconnect:
        del user_sessions[session_id]

# Include the router in your FastAPI app
app.include_router(kyc_controller.router, prefix="/api/kyc", tags=["kyc"])