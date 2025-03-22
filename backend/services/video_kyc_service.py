import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Callable
import json
import os

from fastapi import WebSocket
from langchain import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

logger = logging.getLogger(__name__)

class VideoKYCSession:
    """Manages a Video KYC session with LLM-powered conversation."""
    
    def __init__(self, session_id: str, loan_type: str, applicant_info: Dict[str, Any]):
        """
        Initialize a Video KYC session.
        
        Args:
            session_id: Unique session identifier
            loan_type: Type of loan being applied for
            applicant_info: Basic information about the applicant
        """
        self.session_id = session_id
        self.loan_type = loan_type
        self.applicant_info = applicant_info
        self.conversation_history = []
        self.verification_results = []
        self.transcribed_responses = []
        self.websocket = None
        self.audio_transcriber = None
        self.start_time = time.time()
        self.status = "initiated"
        
        # Initialize the LLM chain for conversation
        self._initialize_llm_chain()
    
    def _initialize_llm_chain(self):
        """Initialize the LangChain components for the KYC agent."""
        try:
            # Create OpenAI chat model
            self.llm = ChatOpenAI(
                model_name=os.getenv("OPENAI_MODEL_NAME", "gpt-4o"),
                temperature=0.2,  # Lower temperature for more predictable responses
                streaming=False,
                verbose=True
            )
            
            # Create system prompt based on loan type
            system_prompt = self._create_system_prompt()
            
            # Initialize the conversation with a system message
            self.messages = [
                SystemMessage(content=system_prompt)
            ]
            
            logger.info(f"Initialized LLM chain for session {self.session_id}")
        except ImportError:
            logger.warning("LangChain not installed. Using fallback mode.")
            self.status = "fallback"
            self.messages = [{"role": "system", "content": self._create_system_prompt()}]
        except Exception as e:
            logger.error(f"Failed to initialize LLM chain: {str(e)}")
            self.status = "error"
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt based on loan type and applicant info."""
        loan_specific_info = ""
        
        if self.loan_type == "personal":
            loan_specific_info = (
                "For personal loans, focus on income verification, employment stability, "
                "credit score, and existing debt obligations."
            )
        elif self.loan_type == "home":
            loan_specific_info = (
                "For home loans, focus on property details, down payment source, "
                "income verification, employment stability, and existing debt obligations."
            )
        elif self.loan_type == "auto":
            loan_specific_info = (
                "For auto loans, focus on the vehicle details, down payment source, "
                "income verification, and existing debt obligations."
            )
        elif self.loan_type == "business":
            loan_specific_info = (
                "For business loans, focus on business performance, financial statements, "
                "business plans, revenue projections, and existing business debts."
            )
        
        return f"""
You are a professional Video KYC agent for Standard Chartered Bank. You are conducting a video interview with a loan applicant.

Your role is to:
1. Verify the applicant's identity and details against their provided documentation
2. Collect information needed for {self.loan_type} loan processing
3. Ask clear, specific questions one at a time
4. Listen to the applicant's verbal responses (which will be transcribed to text)
5. Maintain a professional, friendly tone
6. Be concise and direct in your questions

{loan_specific_info}

Applicant Information:
Name: {self.applicant_info.get('name', 'Not provided')}
ID/Document Number: {self.applicant_info.get('id_number', 'Not provided')}
Contact: {self.applicant_info.get('contact', 'Not provided')}

Guidelines:
- Ask only ONE question at a time, then wait for the applicant's response
- If you need clarification, ask specifically about the unclear information
- Follow a logical progression of questions for KYC verification
- Only ask relevant questions for {self.loan_type} loan KYC verification
- DO NOT ask for sensitive information like passwords or PINs
- Keep your responses brief and professional
- End the interview when you have collected all necessary information
"""
    
    def set_websocket(self, websocket: WebSocket):
        """Set the WebSocket connection for this session."""
        self.websocket = websocket
    
    async def start_conversation(self) -> str:
        """
        Start the KYC conversation.
        
        Returns:
            Initial message from the KYC agent
        """
        self.status = "in_progress"
        
        # Generate the initial greeting/question
        initial_message = (
            f"Hello {self.applicant_info.get('name', 'there')}, "
            f"I'm your Standard Chartered KYC verification agent for your {self.loan_type} loan application. "
            "I'll ask you a series of questions to verify your details. "
            "Please speak clearly into your microphone when answering. "
            "Let's start: Could you please state your full name and date of birth for verification?"
        )
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "agent",
            "content": initial_message,
            "timestamp": time.time()
        })
        
        self.messages.append(AIMessage(content=initial_message))
        
        return initial_message
    
    async def process_transcription(self, text: str):
        """
        Process a transcribed speech segment from the user.
        
        Args:
            text: Transcribed text from user's speech
        """
        if not text.strip():
            return
        
        logger.info(f"Received transcription for session {self.session_id}: {text}")
        
        # Store the transcribed response
        self.transcribed_responses.append({
            "text": text,
            "timestamp": time.time()
        })
        
        # Process the user's message
        await self.process_user_message(text)
    
    async def process_user_message(self, message: str):
        """
        Process a user message and generate an agent response.
        
        Args:
            message: User's message (either transcribed or manually entered)
        """
        # Add user message to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": time.time()
        })
        
        # Add to LangChain messages
        self.messages.append(HumanMessage(content=message))
        
        # Log the user's response
        logger.info(f"User response in session {self.session_id}: {message}")
        
        if self.websocket:
            # Send user message acknowledgment
            await self.websocket.send_json({
                "type": "transcription_received",
                "message": message
            })
        
        # Generate agent response
        try:
            # Get response from LLM
            response = self.llm(self.messages)
            agent_message = response.content
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "agent",
                "content": agent_message,
                "timestamp": time.time()
            })
            
            # Add to LangChain messages
            self.messages.append(AIMessage(content=agent_message))
            
            # Send to client
            if self.websocket:
                await self.websocket.send_json({
                    "type": "agent_message",
                    "message": agent_message
                })
            
        except Exception as e:
            logger.error(f"Error generating agent response: {str(e)}")
            agent_message = "I'm sorry, I'm having trouble processing your response. Could you please repeat that?"
            
            # Send error message to client
            if self.websocket:
                await self.websocket.send_json({
                    "type": "error",
                    "message": agent_message
                })
    
    async def add_verification_result(self, is_verified: bool, confidence: float, metadata: Dict):
        """Add face verification result to session."""
        result = {
            "verified": is_verified,
            "confidence": confidence,
            "timestamp": time.time(),
            "metadata": metadata
        }
        self.verification_results.append(result)
        
        # Notify client of verification result
        if self.websocket:
            await self.websocket.send_json({
                "type": "verification_update",
                "result": result
            })
    
    async def generate_report(self) -> Dict[str, Any]:
        """
        Generate a final report for the KYC session.
        
        Returns:
            Report data including conversation, verification results, and assessment
        """
        self.status = "completed"
        end_time = time.time()
        duration = end_time - self.start_time
        
        # Generate a final assessment using LLM
        final_assessment = await self._generate_assessment()
        
        report = {
            "session_id": self.session_id,
            "loan_type": self.loan_type,
            "applicant_info": self.applicant_info,
            "start_time": self.start_time,
            "end_time": end_time,
            "duration": duration,
            "conversation": self.conversation_history,
            "verification_results": self.verification_results,
            "assessment": final_assessment,
            "status": self.status
        }
        
        logger.info(f"Generated report for session {self.session_id}")
        return report
    
    async def _generate_assessment(self) -> Dict[str, Any]:
        """
        Generate a final assessment of the KYC session.
        
        Returns:
            Assessment data
        """
        try:
            # Create a summary prompt for the LLM
            assessment_prompt = f"""
Based on the KYC interview for {self.loan_type} loan application, provide an assessment with the following:
1. Identity verification result
2. Key information collected
3. Discrepancies or concerns (if any)
4. Recommendation for the loan application
5. Risk assessment (Low, Medium, High)

Conversation Summary:
{json.dumps(self.conversation_history[-10:], indent=2)}  # Include last 10 exchanges

Verification Results:
{json.dumps(self.verification_results, indent=2)}
"""
            
            # Add to messages
            self.messages.append(HumanMessage(content=assessment_prompt))
            
            # Get response
            response = self.llm(self.messages)
            assessment_text = response.content
            
            # Parse the assessment text (a simplistic approach, could be improved)
            assessment = {
                "summary": assessment_text,
                "risk_level": "Medium",  # Default
                "recommended_action": "Review",  # Default
            }
            
            # Extract risk level if present
            if "Risk assessment: Low" in assessment_text:
                assessment["risk_level"] = "Low"
            elif "Risk assessment: Medium" in assessment_text:
                assessment["risk_level"] = "Medium"
            elif "Risk assessment: High" in assessment_text:
                assessment["risk_level"] = "High"
            
            # Extract recommendation if present
            if "Recommended for approval" in assessment_text or "Recommendation: Approve" in assessment_text:
                assessment["recommended_action"] = "Approve"
            elif "Recommended for rejection" in assessment_text or "Recommendation: Reject" in assessment_text:
                assessment["recommended_action"] = "Reject"
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error generating assessment: {str(e)}")
            return {
                "summary": "Assessment could not be generated due to an error.",
                "risk_level": "Unknown",
                "recommended_action": "Manual Review Required"
            }