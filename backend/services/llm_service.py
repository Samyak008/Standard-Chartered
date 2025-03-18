import os
import logging
import asyncio
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class VideoKYCLLMService:
    """
    Service for LLM-based Video KYC conversations
    Integrates with OpenAI to provide interactive loan application guidance
    """
    
    def __init__(self, applicant_info: Dict[str, str], loan_type: str):
        """
        Initialize with applicant information and loan type
        """
        self.applicant_info = applicant_info
        self.loan_type = loan_type
        self.conversation_history: List[Dict[str, str]] = []
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Check if API key is available
        if not self.openai_api_key:
            logger.warning("OpenAI API key not found. Using fallback mode.")
            self.use_openai = False
        else:
            self.use_openai = True
            self._initialize_openai_client()
            
    def _initialize_openai_client(self):
        """
        Initialize OpenAI client
        """
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.openai_api_key)
            logger.info("OpenAI client initialized successfully")
        except ImportError:
            logger.error("Failed to import OpenAI. Make sure the package is installed.")
            self.use_openai = False
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {str(e)}")
            self.use_openai = False
    
    async def get_initial_greeting(self) -> str:
        """
        Get initial greeting message based on applicant info
        """
        applicant_name = self.applicant_info.get("name", "there")
        
        if self.use_openai:
            try:
                system_prompt = f"""
                You are a virtual loan officer at Standard Chartered Bank conducting a Video KYC session.
                You're speaking with {applicant_name} who is applying for a {self.loan_type} loan.
                Your goal is to verify their identity, collect necessary information, and assess their loan eligibility.
                Be professional, courteous, and thorough in your questioning.
                """
                
                user_prompt = f"Start a Video KYC session with {applicant_name} for a {self.loan_type} loan application. Introduce yourself and explain the process."
                
                # Call OpenAI API
                response = await self._call_openai_api(system_prompt, user_prompt)
                
                # Add to conversation history
                self.conversation_history.append({"role": "system", "content": system_prompt})
                self.conversation_history.append({"role": "user", "content": user_prompt})
                self.conversation_history.append({"role": "assistant", "content": response})
                
                return response
            except Exception as e:
                logger.error(f"Error getting greeting from OpenAI: {str(e)}")
                # Fall back to default greeting
        
        # Default greeting if OpenAI fails or isn't available
        loan_type_name = self.loan_type.replace("_", " ").title()
        return f"Hello {applicant_name}, welcome to Standard Chartered's Virtual Branch. I'll be assisting you with your {loan_type_name} application today. First, I'll need to verify your identity and then we'll discuss your loan requirements. How may I help you?"
    
    async def process_message(self, user_message: str) -> str:
        """
        Process user message and generate a response
        """
        if not user_message:
            return "I didn't catch that. Could you please repeat?"
        
        if self.use_openai:
            try:
                system_prompt = f"""
                You are a virtual loan officer at Standard Chartered Bank conducting a Video KYC session.
                You're speaking with {self.applicant_info.get('name', 'the applicant')} who is applying for a {self.loan_type} loan.
                
                Applicant information:
                - Name: {self.applicant_info.get('name', 'Not provided')}
                - ID: {self.applicant_info.get('id_number', 'Not provided')}
                - Contact: {self.applicant_info.get('contact', 'Not provided')}
                
                Your goal is to:
                1. Verify their identity matches the provided information
                2. Ask relevant questions about their loan requirements
                3. Assess their eligibility based on income, employment, and credit history
                4. Guide them through the application process
                
                Be professional, concise, and focus on getting necessary information.
                """
                
                # Call OpenAI API with full conversation history
                response = await self._call_openai_api(system_prompt, user_message, include_history=True)
                
                # Add to conversation history
                self.conversation_history.append({"role": "user", "content": user_message})
                self.conversation_history.append({"role": "assistant", "content": response})
                
                return response
            except Exception as e:
                logger.error(f"Error getting response from OpenAI: {str(e)}")
                # Fall back to simple response
        
        # Simple fallback response logic if OpenAI fails
        if "loan" in user_message.lower():
            return f"For the {self.loan_type} loan, we'll need to verify your income and credit history. Can you tell me about your monthly income and employment status?"
        elif "income" in user_message.lower() or "salary" in user_message.lower():
            return "Thank you for sharing your income details. This helps us determine your loan eligibility. Do you have any existing loans or credit commitments?"
        elif "document" in user_message.lower() or "id" in user_message.lower():
            return "I'll need to verify your identity documents. Please ensure your face is clearly visible in the camera for verification against your ID."
        else:
            return "I understand. Let me guide you through the next steps in your loan application process. Do you have any specific questions about the terms or requirements?"
    
    async def _call_openai_api(self, system_prompt: str, user_message: str, include_history: bool = False) -> str:
        """
        Make API call to OpenAI asynchronously
        """
        try:
            messages = [{"role": "system", "content": system_prompt}]
            
            # Include conversation history if requested
            if include_history and self.conversation_history:
                for entry in self.conversation_history[-10:]:
                    messages.append({"role": entry["role"], "content": entry["content"]})
            
            # Add the current user message
            messages.append({"role": "user", "content": user_message})
            
            # Use asyncio to prevent blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model="gpt-4o",  # Use the latest model specified in .env
                    messages=messages,
                    max_tokens=300,
                    temperature=0.7,
                )
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise