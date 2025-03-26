import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = "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"


# Streamlit app title
st.title("Loan Advisor Bot")

# Input fields for user details
st.header("Applicant Information")
aadhar_details = st.text_input("Aadhar Details")
pan_details = st.text_input("PAN Details")
income = st.text_input("Annual Income")

# Initialize the ChatGroq model
groq_api_key = os.getenv("GROQ_API_KEY")

# chat = ChatGroq(
#     groq_api_key=groq_api_key,
#     model_name="llama3-8b-8192",
#     temperature=0.7
# )
chat = ChatOpenAI(
    model_name="gpt-4o-mini",
    temperature=0.4
)

# Create a chat prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", 
     """You are a KYC agent helping with loan applications. Be friendly but thorough in your questions.
     
     Context information:
     Aadhar Details: {aadhar_details}
     PAN Details: {pan_details}
     Income: {income}
     Loan Approval Status: {loan_approval}
     
     Based on this information, ask relevant follow-up questions to verify the user's identity and 
     assess their loan eligibility. Be conversational and helpful."""),
    ("human", "{input}")
])

# Create the chain
chain = prompt | chat

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add an initial message from the bot
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Hello! I'm your loan advisor bot. I'll help you through the loan application process. Please provide your details and I'll assist you with any questions."
    })

st.header("Chat with Loan Advisor Bot")
user_message = st.text_input("Your Message")

if st.button("Send") and user_message:
    # Add user message to display
    st.session_state.messages.append({"role": "user", "content": user_message})
    
    # Collect all previous messages to create context
    conversation_history = "\n".join([
        f"{'You' if msg['role'] == 'user' else 'Bot'}: {msg['content']}" 
        for msg in st.session_state.messages[:-1]  # Exclude the message we just added
    ])
    
    # Generate response using the chain
    response = chain.invoke({
        "input": user_message,
        "aadhar_details": aadhar_details or "Not provided",
        "pan_details": pan_details or "Not provided",
        "income": income or "Not provided",
        "loan_approval": "Pending"  # Placeholder for loan approval status
    })
    
    # Add bot response to display
    st.session_state.messages.append({"role": "assistant", "content": response.content})

# Display chat messages
st.subheader("Conversation")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Display additional details
with st.sidebar:
    st.header("Application Details")
    st.write(f"Aadhar Details: {aadhar_details}")
    st.write(f"PAN Details: {pan_details}")
    st.write(f"Annual Income: {income}")
    st.write(f"Loan Status: Pending")
    
    # Add a section for loan options
    st.header("Available Loan Products")
    st.write("- Personal Loan (8-15% interest)")
    st.write("- Home Loan (7-9% interest)")
    st.write("- Education Loan (6-8% interest)")
    st.write("- Vehicle Loan (9-12% interest)")