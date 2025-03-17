import asyncio
import logging
from typing import Dict, List, Optional
import json
import os
import requests

logger = logging.getLogger(__name__)

# Store conversation context
conversations: Dict[str, List[Dict]] = {}

# Basic loan eligibility rules
INCOME_THRESHOLD = 300000  # ₹3 lakh per annum
MIN_AGE = 21
MAX_AGE = 60

class LoanAdvisorBot:
    """AI-powered loan advisor chatbot."""
    
    def __init__(self, session_id: str):
        """
        Initialize loan advisor chatbot.
        
        Args:
            session_id: Unique session identifier
        """
        self.session_id = session_id
        
        # Initialize conversation history
        if session_id not in conversations:
            conversations[session_id] = [
                {"role": "system", "content": "You are a helpful loan advisor at a bank. Help customers understand their loan eligibility and guide them through the application process. Be polite, professional and concise."}
            ]
    
    async def process_message(self, message: str) -> str:
        """
        Process user message and generate response.
        
        Args:
            message: User message
        
        Returns:
            Bot response
        """
        # Add user message to conversation history
        conversations[self.session_id].append({
            "role": "user",
            "content": message
        })
        
        try:
            # Get response from LLM (would normally call an API)
            response = await self._get_ai_response(conversations[self.session_id])
            
            # Add response to conversation history
            conversations[self.session_id].append({
                "role": "assistant",
                "content": response
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return "I'm sorry, I'm having trouble processing your request at the moment. Please try again in a few moments."
    
    async def evaluate_loan_eligibility(self, user_data: Dict) -> Dict:
        """
        Evaluate loan eligibility based on user data.
        
        Args:
            user_data: User information dict with name, age, income, etc.
            
        Returns:
            Dict with eligibility result and reasons
        """
        income = user_data.get("income", 0)
        age = user_data.get("age", 0)
        employment_type = user_data.get("employment_type", "")
        
        eligible = True
        reasons = []
        
        # Check income threshold
        if income < INCOME_THRESHOLD:
            eligible = False
            reasons.append(f"Income below minimum threshold of ₹{INCOME_THRESHOLD/100000} lakhs per annum")
        
        # Check age requirements
        if age < MIN_AGE or age > MAX_AGE:
            eligible = False
            reasons.append(f"Age must be between {MIN_AGE} and {MAX_AGE} years")
        
        # Check employment type (simplified)
        if employment_type.lower() not in ["salaried", "self-employed", "business"]:
            eligible = False
            reasons.append("Employment type not eligible")
        
        # Prepare result
        result = {
            "eligible": eligible,
            "reasons": reasons if not eligible else ["You meet our basic eligibility criteria"],
            "next_steps": "Please upload your income proof and identity documents" if eligible else "Unfortunately, you don't qualify at this time"
        }
        
        return result
    
    async def _get_ai_response(self, conversation: List[Dict]) -> str:
        """
        Get response from LLM.
        
        In a real implementation, this would call an API like OpenAI.
        For now, we'll use a simple rule-based response system.
        """
        last_message = conversation[-1]["content"].lower()
        
        # Simple rule-based responses
        if "loan" in last_message and "eligib" in last_message:
            return "To check your loan eligibility, we need to know your annual income, age, and employment type. Could you please provide these details?"
        
        elif "income" in last_message or "salary" in last_message:
            return "Thank you for sharing your income details. Could you also confirm your age and employment type (salaried, self-employed, or business)?"
        
        elif "document" in last_message or "upload" in last_message:
            return "You'll need to upload your identity proof (Aadhaar or PAN card) and income proof (salary slips or bank statements). Would you like to upload them now?"
        
        elif "interest rate" in last_message or "emi" in last_message:
            return "Our current interest rates start from 10.5% p.a. The exact rate and EMI will depend on your loan amount, tenure, and credit profile."
        
        elif "thank" in last_message or "bye" in last_message:
            return "You're welcome! If you have any more questions, feel free to ask. Have a great day!"
        
        else:
            return "I'm here to help with your loan application. Would you like to know about eligibility criteria, required documents, or interest rates?"

async def get_conversation_history(session_id: str) -> List[Dict]:
    """Get conversation history for a session."""
    return conversations.get(session_id, [])