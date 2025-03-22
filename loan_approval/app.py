# from fastapi import FastAPI
# import joblib
# import pandas as pd


# app = FastAPI()


# model = joblib.load(r"C:\Users\Tamanna Grover\Loan-Approval-Predictor\best_model.pkl")  # Make sure your .pkl file is in the same folder

# @app.post("/predict/")
# async def predict(input_data: dict):
    
#     df = pd.DataFrame([input_data])
    
#     prediction = model.predict(df)
#     return {"loan_approval": bool(prediction[0])}

# @app.get("/")
# def read_root():
#     return {"message": "Welcome to the Loan Approval API!"}

from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect
import joblib
import pandas as pd
from langchain import ConversationChain
from langchain.prompts import PromptTemplate
from typing import Dict, Any

app = FastAPI()

# Load the prediction model
model = joblib.load("best_model.pkl")

# In-memory storage for user sessions
user_sessions: Dict[str, Dict[str, Any]] = {}

# Define a prompt template for LangChain
prompt_template = PromptTemplate(
    input_variables=["user_input", "aadhar_details", "pan_details", "income", "loan_approval"],
    template=(
        "You are a KYC agent. Validate the user's response based on the following details:\n"
        "Aadhar Details: {aadhar_details}\n"
        "PAN Details: {pan_details}\n"
        "Income: {income}\n"
        "Loan Approval: {loan_approval}\n"
        "User's response: {user_input}\n"
        "Ask follow-up questions based on the user's response."
    )
)

@app.websocket("/ws/kyc/{session_id}")
async def kyc_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    # Receive initial details from the frontend
    initial_data = await websocket.receive_json()
    aadhar_details = initial_data.get("aadhar_details")
    pan_details = initial_data.get("pan_details")
    income = initial_data.get("income")

    # Prepare input data for the prediction model
    input_data = {
        "aadhar_details": aadhar_details,
        "pan_details": pan_details,
        "income": income
    }
    df = pd.DataFrame([input_data])
    prediction = model.predict(df)
    loan_approval = bool(prediction[0])

    # Initialize user session with constant details and loan approval status
    user_sessions[session_id] = {
        "conversation_chain": ConversationChain(prompt_template=prompt_template),
        "aadhar_details": aadhar_details,
        "pan_details": pan_details,
        "income": income,
        "loan_approval": loan_approval
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
            loan_approval = session_data["loan_approval"]

            # Generate a follow-up question based on user input and context
            follow_up_question = conversation_chain.run(
                user_input=user_input,
                aadhar_details=aadhar_details,
                pan_details=pan_details,
                income=income,
                loan_approval=loan_approval
            )

            # Send the follow-up question to the client
            await websocket.send_json({"follow_up_question": follow_up_question})

    except WebSocketDisconnect:
        del user_sessions[session_id]

@app.post("/predict/")
async def predict(input_data: dict):
    df = pd.DataFrame([input_data])
    prediction = model.predict(df)
    return {"loan_approval": bool(prediction[0])}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Loan Approval API!"}