import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = "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"
# Configure page
st.set_page_config(
    page_title="Finance Assistant",
    page_icon="💰",
    layout="centered"
)

# Add custom CSS
st.markdown("""
<style>
    .stTextInput {
        background-color: #2e2e2e;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .assistant {
        background-color: #2e2e2e;
    }
    .human {
        background-color: #1e1e1e;
    }
</style>
""", unsafe_allow_html=True)

# Initialize ChatOpenAI
chat = ChatOpenAI(
    model_name="gpt-4o-mini",
    temperature=0.7
)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="""You are a knowledgeable financial advisor specializing in:
        - Loan products and eligibility
        - Financial planning
        - Investment basics
        - Credit management
        Please provide clear, concise answers to financial questions.""")
    ]

st.title("💬 Financial Assistant")
st.subheader("Ask me anything about loans and finance!")

# User input
user_input = st.text_input("Your question:", key="user_input")

if st.button("Send"):
    if user_input:
        # Add user message to chat history
        st.session_state.messages.append(HumanMessage(content=user_input))
        
        try:
            # Get response from ChatOpenAI
            response = chat(st.session_state.messages)
            
            # Add assistant response to chat history
            st.session_state.messages.append(response)
            
            # Clear input
            # st.session_state.user_input = ""
            
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Display chat history
for message in st.session_state.messages[1:]:  # Skip system message
    role = "assistant" if isinstance(message, SystemMessage) else "human"
    with st.container():
        st.markdown(f"""
        <div class="chat-message {role}">
            <b>{"Assistant" if role == "assistant" else "You"}:</b><br/>
            {message.content}
        </div>
        """, unsafe_allow_html=True)