import streamlit as st
import os
from pathlib import Path
import time
import json
from urllib.parse import urlencode

# Set page configuration
st.set_page_config(
    page_title="Standard Chartered Loan Journey",
    page_icon="🏦",
    layout="wide"
)

# CSS for custom styling - removed button styling to avoid conflicts
st.markdown("""
<style>
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
    .video-container {
        margin: 1rem 0;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        max-width: 800px; /* Smaller video size */
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
        "video_path": "video2.mp4",
        "options": [
            {
                "id": "home",
                "title": "Home Loan",
                "description": "Finance your dream home with competitive interest rates",
                "video_path": "video3.mp4",
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

# Initialize session state
if 'current_step' not in st.session_state:
    st.session_state.current_step = "intro"

if 'journey_selections' not in st.session_state:
    st.session_state.journey_selections = {}

if 'progress' not in st.session_state:
    st.session_state.progress = 0

# For auto-progression timer
if 'video_played' not in st.session_state:
    st.session_state.video_played = False

if 'auto_progress_timer' not in st.session_state:
    st.session_state.auto_progress_timer = 0

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
    
    # Reset video played status for the new step
    st.session_state.video_played = False
    st.session_state.auto_progress_timer = 0
    
    # Trigger rerun to show the next step
    st.rerun()

def go_to_chatbot():
    """Redirect user to the loan bot app with context parameters"""
    # Collect journey data
    journey_data = st.session_state.journey_selections
    
    # Get loan type selection
    loan_type = journey_data.get("loan_type", {}).get("option_id", "")
    is_status_check = journey_data.get("intro", {}).get("option_id", "") == "check_status"
    
    # Create query parameters
    params = {
        "loan_type": loan_type,
        "journey_complete": "true",
        "is_status_check": str(is_status_check).lower()
    }
    
    # Get reference number if provided
    if is_status_check and "reference_number" in st.session_state:
        params["reference_number"] = st.session_state.reference_number
    
    query_string = urlencode(params)
    chatbot_url = "loan_bot_app?" + query_string  # Remove leading slash for relative path
    
    st.success("Redirecting to loan advisor...")
    
    # Use JavaScript to redirect
    js = f"""
    <script>
    window.location.href = "{chatbot_url}";
    </script>
    """
    st.markdown(js, unsafe_allow_html=True)
    
    # Fallback for when JavaScript doesn't work
    st.markdown(f"[Continue to Loan Advisor Bot]({chatbot_url})")

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

# Main app flow
def main():
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
            go_to_chatbot()
        
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
            go_to_chatbot()
    
    # For status check, provide a reference number input and continue button
    elif current_step == "status_check":
        reference_number = st.text_input("Enter your application reference number", key="reference_number")
        
        # Only enable the button if a reference number is provided
        button_disabled = not reference_number
        
        # Add some space
        st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
        
        # Only show one button
        if st.button("Check Status with Advisor", key="check_status", disabled=button_disabled):
            go_to_chatbot()
    
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

if __name__ == "__main__":
    main()