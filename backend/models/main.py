import streamlit as st
import os
from pathlib import Path
import time
import json
from urllib.parse import urlencode, parse_qs
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import sys

# Add the backend directory to path so we can import modules
sys.path.append("backend")

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Standard Chartered Loan Assistant",
    page_icon="🏦",
    layout="wide"
)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'journey'  # 'journey' or 'chatbot'

# CSS for custom styling - combined styles from both apps
st.markdown("""
<style>
    /* Common styles */
    .main-header {
        font-size: 2.5rem;
        color: #0066b2;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0066b2;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    /* Video journey styles */
    .video-container {
        margin: 1rem 0;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }
    .option-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        cursor: pointer;
    }
    .option-card h3 {
        color: #0066b2;
        margin-top: 0;
    }
    .option-card p {
        color: #666;
        margin-bottom: 0;
    }
    .option-selected {
        border: 3px solid #0066b2;
    }
    .progress-tracker {
        padding: 20px;
        background-color: #f8f9fa;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .centered {
        display: flex;
        justify-content: center;
    }
    .spacer {
        height: 20px;
    }
    .info-box {
        background-color: #f0f7ff;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #0066b2;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

#################################################
# VIDEO JOURNEY CODE
#################################################

# Define the structure for the video journey
journey_structure = {
    "intro": {
        "title": "Welcome to Standard Chartered Bank",
        "description": "Please select an option to continue.",
        "video_path": "video1.mp4",
        "options": [
            {
                "id": "new_loan",
                "title": "Apply for a New Loan",
                "description": "Start a new loan application process",
                "video_path": "videos/apply_new_loan.mp4",
                "next_step": "loan_type"
            },
            {
                "id": "check_status",
                "title": "Check Application Status",
                "description": "Check the status of your existing application",
                "video_path": "videos/check_status.mp4",
                "next_step": "status_check"
            }
        ]
    },
    "status_check": {
        "title": "Application Status Check",
        "description": "Please enter your application reference number to check status.",
        "video_path": "videos/status_check_info.mp4",
        "next_step": "chatbot"  # This will redirect to chatbot for status check
    },
    "loan_type": {
        "title": "Select Your Loan Type",
        "description": "Choose the type of loan that fits your needs.",
        "video_path":  "video2.mp4",
        "options": [
            {
                "id": "home",
                "title": "Home Loan",
                "description": "Finance your dream home with competitive interest rates",
                "video_path":  "video3.mp4",

                "next_step": "loan_info"  # Changed from thank_you to loan_info
            },
            {
                "id": "car",
                "title": "Car Loan",
                "description": "Drive your dream car with affordable financing",
                "video_path": "video3.mp4",
                "next_step": "loan_info"  # Changed from thank_you to loan_info
            },
            {
                "id": "education",
                "title": "Education Loan",
                "description": "Invest in your future with education financing",
                "video_path": "video3.mp4",
                "next_step": "loan_info"  # Changed from thank_you to loan_info
            },
            {
                "id": "business",
                "title": "Business Loan",
                "description": "Grow your business with our financial solutions",
                "video_path": "video3.mp4",
                "next_step": "loan_info"  # Changed from thank_you to loan_info
            }
        ]
    },
    # Added loan_info step for displaying loan-specific information
    "loan_info": {
        "title": "Loan Information",
        "description": "Here's more information about your selected loan type.",
        # No video path here - we'll use the selected loan's video
        "next_step": "thank_you"
    },
    "thank_you": {
        "title": "Thank You & Next Steps",
        "description": "Thank you for your interest. Let's proceed with document verification and KYC.",
        "video_path": "video4.mp4",
        "next_step": "chatbot"  # After thank you, redirect to chatbot
    }
}

# Function to create dummy local video paths for testing
def create_dummy_videos():
    videos_dir = Path("videos")
    videos_dir.mkdir(exist_ok=True)
    
    # Create a placeholder text file for each expected video
    for step, content in journey_structure.items():
        if "video_path" in content:
            file_path = Path(content["video_path"])
            if not file_path.exists():
                file_path.parent.mkdir(exist_ok=True)
                file_path.with_suffix(".txt").write_text(f"Placeholder for {file_path}")
        
        if "options" in content:
            for option in content["options"]:
                file_path = Path(option["video_path"])
                if not file_path.exists():
                    file_path.parent.mkdir(exist_ok=True)
                    file_path.with_suffix(".txt").write_text(f"Placeholder for {file_path}")

# Journey session state initialization
if 'current_step' not in st.session_state:
    st.session_state.current_step = "intro"

if 'journey_selections' not in st.session_state:
    st.session_state.journey_selections = {}

if 'progress' not in st.session_state:
    st.session_state.progress = 0

# For auto-progression timer
if 'video_played' not in st.session_state:
    st.session_state.video_played = False

# For local development - create dummy video placeholders
create_dummy_videos()

def render_video(video_path):
    """Render video player or placeholder for the given path"""
    try:
        if os.path.exists(video_path):
            st.video(video_path)
            # Mark as played for auto-progression
            st.session_state.video_played = True
        else:
            # If video doesn't exist, show a placeholder
            st.info(f"Video placeholder for: {video_path}")
            # For development purposes, you can add a fake progress bar to simulate video playback
            if st.button("Simulate Video Playback"):
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.02)  # Faster for testing
                    progress_bar.progress(i + 1)
                # Mark as played for auto-progression
                st.session_state.video_played = True
    except Exception as e:
        st.error(f"Error loading video: {str(e)}")

def select_option(option_id, option_title, next_step):
    """Process user selection and update journey progress"""
    # Save the selection
    current_step = st.session_state.current_step
    st.session_state.journey_selections[current_step] = {
        "option_id": option_id,
        "option_title": option_title
    }
    
    # Update progress
    total_steps = 4  # Modified for the new flow: intro, loan_type, loan_info, thank_you
    progress_increment = 100 / total_steps
    st.session_state.progress = min(100, st.session_state.progress + progress_increment)
    
    # Move to next step
    st.session_state.current_step = next_step
    
    # If next step is "chatbot", switch to chatbot page
    if next_step == "chatbot":
        switch_to_chatbot()
    else:
        # Reset video played status for the new step
        st.session_state.video_played = False
        
        # Trigger rerun to show the next step
        st.rerun()

def switch_to_chatbot():
    """Switch to chatbot page with data from journey"""
    st.session_state.page = 'chatbot'
    
    # Reset the chat messages when switching to the chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    st.rerun()

def render_progress_tracker():
    """Render the progress tracker UI"""
    st.markdown('<div class="progress-tracker">', unsafe_allow_html=True)
    st.progress(st.session_state.progress / 100)
    
    # Show journey path - updated for new flow
    cols = st.columns(4)  # Now 4 columns for the 4 steps
    if st.session_state.journey_selections.get("intro", {}).get("option_id") == "check_status":
        steps = ["Start", "Status Check", "Chat", ""]
    else:
        steps = ["Start", "Loan Type", "Information", "Next Steps"]
    
    # Calculate current step index based on the journey structure
    if st.session_state.current_step == "intro":
        current_step_index = 0
    elif st.session_state.current_step == "loan_type":
        current_step_index = 1
    elif st.session_state.current_step == "loan_info":
        current_step_index = 2
    elif st.session_state.current_step == "thank_you":
        current_step_index = 3
    else:
        current_step_index = 0
    
    for i, step in enumerate(steps):
        if i < current_step_index:
            cols[i].markdown(f"✅ {step}")
        elif i == current_step_index:
            cols[i].markdown(f"**→ {step}**")
        elif step:  # Only show non-empty steps
            cols[i].markdown(f"○ {step}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_selected_choices():
    """Render summary of user's selected choices"""
    if st.session_state.journey_selections:
        st.markdown("<div class='info-box'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#0066b2; margin-top:0;'>Your Selection</h3>", unsafe_allow_html=True)
        
        # Get the selected option from intro and loan_type
        intro_selection = st.session_state.journey_selections.get("intro", {}).get("option_title", "Not selected")
        
        if st.session_state.journey_selections.get("intro", {}).get("option_id") == "new_loan":
            loan_type = st.session_state.journey_selections.get("loan_type", {}).get("option_title", "Not selected")
            st.markdown(f"**Selected Action**: {intro_selection}")
            st.markdown(f"**Loan Type**: {loan_type}")
        else:
            st.markdown(f"**Selected Action**: {intro_selection}")
            
        st.markdown("</div>", unsafe_allow_html=True)

# Main journey flow
def render_journey_page():
    # Standard Chartered header
    st.markdown('<h1 class="main-header">Standard Chartered Bank</h1>', unsafe_allow_html=True)
    
    # Render progress tracker
    render_progress_tracker()
    
    # Get the current step data
    current_step = st.session_state.current_step
    step_data = journey_structure.get(current_step)
    
    if not step_data:
        st.error(f"Error: Step '{current_step}' not found in journey structure.")
        return
    
    # Display step title
    st.markdown(f'<h2 class="sub-header">{step_data["title"]}</h2>', unsafe_allow_html=True)
    
    # Display step description if available
    if "description" in step_data:
        st.markdown(step_data["description"])
    
    # Display selected choices so far
    if current_step != "intro":
        render_selected_choices()
    
    # Handle the loan_info step specially to show video based on selection
    if current_step == "loan_info":
        # Get the selected loan type
        loan_type_id = st.session_state.journey_selections.get("loan_type", {}).get("option_id", "")
        
        # Find the corresponding loan type option from journey_structure
        selected_loan_option = None
        for option in journey_structure["loan_type"]["options"]:
            if option["id"] == loan_type_id:
                selected_loan_option = option
                break
        
        if selected_loan_option:
            # Display the video for the selected loan type
            st.markdown('<div class="video-container">', unsafe_allow_html=True)
            render_video(selected_loan_option["video_path"])
            st.markdown('</div>', unsafe_allow_html=True)
            
            # After the video, show a continue button
            st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
            if st.button("Continue to Next Steps", key="goto_thank_you"):
                select_option("continue", "Continue", step_data["next_step"])
    
    # Handle the thank_you step
    elif current_step == "thank_you":
        # Show selected loan type info
        selected_loan = st.session_state.journey_selections.get("loan_type", {}).get("option_title", "your loan")
        
        # Display the thank you video
        if "video_path" in step_data:
            st.markdown('<div class="video-container">', unsafe_allow_html=True)
            render_video(step_data["video_path"])
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown(f"<div class='info-box'>", unsafe_allow_html=True)
        st.markdown(f"### You've selected: {selected_loan}")
        st.markdown(f"We'll need to verify your documents and complete KYC before proceeding.", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Add some space
        st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
        
        # Show chatbot button
        if st.button("Continue to Loan Advisor", key="goto_chatbot"):
            select_option("chat", "Speak with a Loan Advisor", step_data["next_step"])
        
        # Auto-progress functionality for thank_you page
        if st.session_state.video_played:
            # Add a message to let user know they'll be redirected
            st.info("Video completed. You'll be redirected to the Loan Advisor shortly...")
            
            # Create an invisible container for the auto-redirect countdown
            placeholder = st.empty()
            
            # Wait 3 seconds then redirect
            import time
            time.sleep(3)
            
            # Clear the placeholder and redirect
            placeholder.empty()
            select_option("chat", "Speak with a Loan Advisor", step_data["next_step"])
    
    # For status check, provide a reference number input and continue button
    elif current_step == "status_check":
        reference_number = st.text_input("Enter your application reference number", key="reference_number")
        
        # Only enable the button if a reference number is provided
        button_disabled = not reference_number
        
        # Add some space
        st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
        
        # Only show one button
        if st.button("Check Status with Advisor", key="check_status", disabled=button_disabled):
            select_option("status", "Check Status", step_data["next_step"])
    
    # Display video for other steps
    elif "video_path" in step_data:
        st.markdown('<div class="video-container">', unsafe_allow_html=True)
        render_video(step_data["video_path"])
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display options if available
    if "options" in step_data:
        st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
        
        # Create a grid for options (2x2 or 2x1 depending on number of options)
        num_cols = 2 if len(step_data["options"]) >= 2 else 1
        cols = st.columns(num_cols)
        
        for i, option in enumerate(step_data["options"]):
            col = cols[i % num_cols]
            with col:
                # Create a clickable card that selects the option
                if st.button(f"{option['title']}", key=f"opt_{option['id']}", 
                             help=f"{option['description']}", use_container_width=True):
                    select_option(option['id'], option['title'], option['next_step'])
                
                # Display description below button
                st.caption(option['description'])
    
    # Option to restart the journey
    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
    if st.session_state.current_step != "intro":
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            if st.button("Start Over", use_container_width=True):
                st.session_state.current_step = "intro"
                st.session_state.journey_selections = {}
                st.session_state.progress = 0
                st.session_state.video_played = False
                st.rerun()

#################################################
# LOAN BOT CODE
#################################################

# Loan type mapping
loan_type_map = {
    "personal": "Personal Loan",
    "home": "Home Loan",
    "education": "Education Loan",
    "car": "Vehicle Loan",
    "business": "Business Loan"
}

def render_chatbot_page():
    # Get data from journey selections
    journey_data = st.session_state.journey_selections
    loan_type = journey_data.get("loan_type", {}).get("option_id", "")
    is_status_check = journey_data.get("intro", {}).get("option_id", "") == "check_status"
    reference_number = st.session_state.get("reference_number", "")
    
    # Display the header
    st.markdown('<h1 class="main-header">Loan Advisor Bot</h1>', unsafe_allow_html=True)
    
    # Show journey info
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("<h3>Your Loan Journey Selections</h3>")
    
    # Display selections based on previous choices
    if is_status_check:
        col1, col2 = st.columns(2)
        col1.metric("Action", "Check Application Status")
        col2.metric("Reference Number", reference_number if reference_number else "Not provided")
    else:
        col1, col2 = st.columns(2)
        col1.metric("Action", "Apply for New Loan")
        col2.metric("Loan Type", loan_type_map.get(loan_type, "Not specified"))
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input fields for user details
    st.markdown('<h2 class="sub-header">Applicant Information</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        aadhar_details = st.text_input("Aadhar Details")
        pan_details = st.text_input("PAN Details")
    with col2:
        income = st.text_input("Annual Income")
        employment_type = st.selectbox("Employment Type", ["Salaried", "Self-employed", "Business Owner", "Retired", "Other"])
    
    # Initialize the chatbot with Groq
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        st.warning("GROQ API key not found. Some functionality will be limited.")
        groq_api_key = "dummy_key"
    
    try:
        chat = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama3-8b-8192",
            temperature=0.7
        )
    except Exception as e:
        st.error(f"Error initializing Groq: {str(e)}")
        chat = None
    
    # Create a more context-aware chat prompt template
    system_template = """You are a KYC agent helping with loan applications at Standard Chartered Bank. 
    Be friendly but thorough in your questions.
     
    Context information:
    Aadhar Details: {aadhar_details}
    PAN Details: {pan_details}
    Income: {income}
    Employment Type: {employment_type}
    Loan Type: {loan_type}
    Reference Number: {reference_number}
    Is Status Check: {is_status_check}
    
    If any of the above context information is missing, politely ask for it as it's essential for the loan application process.
    
    Based on this information, ask relevant follow-up questions to verify the user's identity and 
    assess their loan eligibility. Be conversational and helpful."""
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("human", "{input}")
    ])
    
    # Create the chain
    if chat:
        chain = prompt | chat
    
    # Add initial message if needed
    if "messages" not in st.session_state:
        st.session_state.messages = []
        initial_message = "Hello! I'm your loan advisor bot at Standard Chartered Bank."
        
        if is_status_check:
            initial_message += f" I see you're checking the status of your application{' #' + reference_number if reference_number else ''}. Could you please confirm your Aadhar and PAN details for verification?"
        else:
            initial_message += f" I see you're interested in a {loan_type_map.get(loan_type, 'loan')}. Let me help you complete your application. Please provide your Aadhar and PAN details along with your income information."
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": initial_message
        })
    
    # Display chat messages
    st.markdown('<h2 class="sub-header">Chat with Loan Advisor Bot</h2>', unsafe_allow_html=True)
    
    # Chat message display with better styling
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    user_message = st.chat_input("Type your message here...")
    
    if user_message:
        # Add user message to display
        st.session_state.messages.append({"role": "user", "content": user_message})
        
        # Determine values to use in prompt
        loan_type_value = loan_type_map.get(loan_type, "Not provided")
        
        try:
            if chat:
                # Generate response using the chain
                response = chain.invoke({
                    "input": user_message,
                    "aadhar_details": aadhar_details or "Not provided",
                    "pan_details": pan_details or "Not provided",
                    "income": income or "Not provided",
                    "employment_type": employment_type,
                    "loan_type": loan_type_value,
                    "reference_number": reference_number or "Not provided",
                    "is_status_check": "Yes" if is_status_check else "No"
                })
                
                # Add bot response to display
                st.session_state.messages.append({"role": "assistant", "content": response.content})
            else:
                # Fallback response if API not configured
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "I'm sorry, I'm having trouble connecting to my knowledge base. Please make sure the GROQ API key is properly configured."
                })
        except Exception as e:
            # Fallback response if API fails
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "I'm sorry, I'm having trouble processing your request. Please try again or provide more information about your loan requirements."
            })
            st.error(f"Error: {str(e)}")
        
        # Rerun to update the chat display
        st.rerun()
    
    # Display additional details in the sidebar
    with st.sidebar:
        st.header("Application Details")
        st.write(f"Aadhar Details: {aadhar_details or 'Not provided'}")
        st.write(f"PAN Details: {pan_details or 'Not provided'}")
        st.write(f"Annual Income: {income or 'Not provided'}")
        st.write(f"Employment Type: {employment_type}")
        
        if not is_status_check:
            st.write(f"Loan Type: {loan_type_map.get(loan_type, 'Not specified')}")
        else:
            st.write(f"Reference Number: {reference_number or 'Not provided'}")
        
        # Application status section
        st.header("Application Status")
        
        # Determine status based on provided information
        missing_fields = []
        if not aadhar_details:
            missing_fields.append("Aadhar details")
        if not pan_details:
            missing_fields.append("PAN details")
        if not income:
            missing_fields.append("Income")
        
        if missing_fields:
            status = "Incomplete"
            status_color = "🔴"
            missing_text = ", ".join(missing_fields)
            st.write(f"{status_color} Status: {status} (Missing: {missing_text})")
        else:
            status = "Ready for Review"
            status_color = "🟡"
            st.write(f"{status_color} Status: {status}")
            st.button("Submit Application for Review", type="primary")
        
        # Add a section for loan options
        st.header("Available Loan Products")
        st.write("- Personal Loan (8-15% interest)")
        st.write("- Home Loan (7-9% interest)")
        st.write("- Education Loan (6-8% interest)")
        st.write("- Vehicle Loan (9-12% interest)")
        
        # Help section
        st.header("Need Help?")
        st.write("📞 Call: 1800-XXX-XXXX")
        st.write("📧 Email: support@sc-loans.com")
        st.write("🌐 Visit: standardchartered.com/loans")
    
    # Button to go back to journey
    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("Back to Loan Journey", use_container_width=True):
            st.session_state.page = 'journey'
            st.rerun()

# Main application logic - determine which page to show
def main():
    if st.session_state.page == 'journey':
        render_journey_page()
    else:
        render_chatbot_page()

if __name__ == "__main__":
    main()