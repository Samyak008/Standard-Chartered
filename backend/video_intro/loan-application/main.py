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

if 'language' not in st.session_state:
    st.session_state.language = 'en'  # Default to English

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
    .language-selector {
        display: flex;
        justify-content: flex-end;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    .language-button {
        background-color: #f0f0f0;
        border: 1px solid #ddd;
        padding: 5px 10px;
        margin-left: 5px;
        cursor: pointer;
        border-radius: 4px;
    }
    .language-button.active {
        background-color: #0066b2;
        color: white;
        border-color: #0066b2;
    }
</style>
""", unsafe_allow_html=True)

# Load translations
def load_translations(language):
    """Load language-specific translations"""
    try:
        translation_path = Path(f"backend/video_intro/translations/{language}.json")
        if not translation_path.exists():
            # Try alternative path
            translation_path = Path(f"video_intro/translations/{language}.json")
        
        if not translation_path.exists():
            # Fallback to default content for development
            if language == "en":
                return get_english_defaults()
            else:
                return get_hindi_defaults()
        
        with open(translation_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading translations: {str(e)}")
        # Return default content
        if language == "en":
            return get_english_defaults()
        else:
            return get_hindi_defaults()

def get_english_defaults():
    """Default English content if translation file is missing"""
    return {
        "welcome_title": "Welcome to Standard Chartered Bank",
        "welcome_description": "Please select an option to continue.",
        "language_selector": "Choose your preferred language:",
        "intro_options": [
            {
                "id": "new_loan",
                "title": "Apply for a New Loan",
                "description": "Start a new loan application process",
                "video_path": "videos/english/video1.mp4",
                "next_step": "loan_type"
            },
            {
                "id": "check_status",
                "title": "Check Application Status",
                "description": "Check the status of your existing application",
                "video_path": "videos/english/check_status.mp4",
                "next_step": "status_check"
            }
        ],
        "status_check_title": "Application Status Check",
        "status_check_description": "Please enter your application reference number to check status.",
        "reference_number_placeholder": "Enter your application reference number",
        "check_status_button": "Check Status with Advisor",
        "loan_type_title": "Select Your Loan Type",
        "loan_type_description": "Choose the type of loan that fits your needs.",
        "loan_types": [
            {
                "id": "home",
                "title": "Home Loan",
                "description": "Finance your dream home with competitive interest rates",
                "video_path": "videos/english/video3.mp4",
                "next_step": "loan_info"
            },
            {
                "id": "car",
                "title": "Car Loan",
                "description": "Drive your dream car with affordable financing",
                "video_path": "videos/english/video3.mp4",
                "next_step": "loan_info"
            },
            {
                "id": "education",
                "title": "Education Loan",
                "description": "Invest in your future with education financing",
                "video_path": "videos/english/video3.mp4",
                "next_step": "loan_info"
            },
            {
                "id": "business",
                "title": "Business Loan",
                "description": "Grow your business with our financial solutions",
                "video_path": "videos/english/video3.mp4",
                "next_step": "loan_info"
            }
        ],
        "loan_info_title": "Loan Information",
        "loan_info_description": "Here's more information about your selected loan type.",
        "continue_button": "Continue to Next Steps",
        "thank_you_title": "Thank You & Next Steps",
        "thank_you_description": "Thank you for your interest. Let's proceed with document verification and KYC.",
        "continue_to_advisor": "Continue to Loan Advisor",
        "redirecting_message": "Video completed. You'll be redirected to the Loan Advisor shortly...",
        "start_over": "Start Over",
        "your_selection": "Your Selection",
        "selected_action": "Selected Action",
        "loan_type_label": "Loan Type",
        "kyc_message": "We'll need to verify your documents and complete KYC before proceeding."
    }

def get_hindi_defaults():
    """Default Hindi content if translation file is missing"""
    return {
        "welcome_title": "स्टैंडर्ड चार्टर्ड बैंक में आपका स्वागत है",
        "welcome_description": "कृपया जारी रखने के लिए एक विकल्प चुनें।",
        "language_selector": "अपनी पसंदीदा भाषा चुनें:",
        "intro_options": [
            {
                "id": "new_loan",
                "title": "नया ऋण के लिए आवेदन करें",
                "description": "नए ऋण आवेदन प्रक्रिया शुरू करें",
                "video_path": "videos/hindi/p1.mp4",
                "next_step": "loan_type"
            },
            {
                "id": "check_status",
                "title": "आवेदन की स्थिति जांचें",
                "description": "अपने मौजूदा आवेदन की स्थिति जांचें",
                "video_path": "videos/hindi/check_status.mp4",
                "next_step": "status_check"
            }
        ],
        "status_check_title": "आवेदन स्थिति जांच",
        "status_check_description": "स्थिति जांचने के लिए कृपया अपना आवेदन संदर्भ नंबर दर्ज करें।",
        "reference_number_placeholder": "अपना आवेदन संदर्भ नंबर दर्ज करें",
        "check_status_button": "सलाहकार के साथ स्थिति जांचें",
        "loan_type_title": "अपना ऋण प्रकार चुनें",
        "loan_type_description": "अपनी जरूरतों के अनुसार ऋण का प्रकार चुनें।",
        "loan_types": [
            {
                "id": "home",
                "title": "होम लोन",
                "description": "प्रतिस्पर्धी ब्याज दरों के साथ अपने सपनों का घर वित्त करें",
                "video_path": "videos/hindi/p3.mp4",
                "next_step": "loan_info"
            },
            {
                "id": "car",
                "title": "कार लोन",
                "description": "किफायती वित्तपोषण के साथ अपनी सपनों की कार चलाएं",
                "video_path": "videos/hindi/p3.mp4",
                "next_step": "loan_info"
            },
            {
                "id": "education",
                "title": "शिक्षा ऋण",
                "description": "शिक्षा वित्तपोषण के साथ अपने भविष्य में निवेश करें",
                "video_path": "videos/hindi/p3.mp4",
                "next_step": "loan_info"
            },
            {
                "id": "business",
                "title": "व्यापार ऋण",
                "description": "हमारे वित्तीय समाधानों के साथ अपने व्यवसाय को बढ़ाएं",
                "video_path": "videos/hindi/p3.mp4",
                "next_step": "loan_info"
            }
        ],
        "loan_info_title": "ऋण जानकारी",
        "loan_info_description": "आपके चयनित ऋण प्रकार के बारे में अधिक जानकारी यहां है।",
        "continue_button": "अगले चरण पर जाएं",
        "thank_you_title": "धन्यवाद और अगले कदम",
        "thank_you_description": "आपकी रुचि के लिए धन्यवाद। चलिए दस्तावेज़ सत्यापन और KYC के साथ आगे बढ़ते हैं।",
        "continue_to_advisor": "ऋण सलाहकार के पास जाएं",
        "redirecting_message": "वीडियो पूरा हो गया है। आपको शीघ्र ही ऋण सलाहकार के पास भेज दिया जाएगा...",
        "start_over": "फिर से शुरू करें",
        "your_selection": "आपका चयन",
        "selected_action": "चयनित कार्रवाई",
        "loan_type_label": "ऋण प्रकार",
        "kyc_message": "आगे बढ़ने से पहले हमें आपके दस्तावेजों का सत्यापन और KYC पूरा करना होगा।"
    }

# Define dynamic journey structure based on selected language
def generate_journey_structure():
    """Generate journey structure based on selected language"""
    translations = load_translations(st.session_state.language)

    return {
        "intro": {
            "title": translations["welcome_title"],
            "description": translations["welcome_description"],
            "video_path": translations["intro_options"][0]["video_path"],
            "options": translations["intro_options"]
        },
        "status_check": {
            "title": translations["status_check_title"],
            "description": translations["status_check_description"],
            "video_path": "videos/status_check_info.mp4",  # This could be language-specific too
            "next_step": "chatbot"  # This will redirect to chatbot for status check
        },
        "loan_type": {
            "title": translations["loan_type_title"],
            "description": translations["loan_type_description"],
            "video_path": r'C:\Users\Samyak Varia\Downloads\sc\2ND VID.mp4',  # This could be language-specific
            "options": translations["loan_types"]
        },
        "loan_info": {
            "title": translations["loan_info_title"],
            "description": translations["loan_info_description"],
            "next_step": "thank_you"
        },
        "thank_you": {
            "title": translations["thank_you_title"],
            "description": translations["thank_you_description"],
            "video_path": r'C:\Users\Samyak Varia\Downloads\sc\4TH VID.mp4',  # This could be language-specific
            "next_step": "chatbot"  # After thank you, redirect to chatbot
        }
    }

# Function to create dummy local video paths for testing
def create_dummy_videos():
    videos_dir = Path("videos")
    videos_dir.mkdir(exist_ok=True)
    
    # Create language-specific directories
    for lang in ["english", "hindi"]:
        lang_dir = videos_dir / lang
        lang_dir.mkdir(exist_ok=True)
    
    # Get the journey structure for both languages
    for lang in ["en", "hi"]:
        temp_lang = st.session_state.language
        st.session_state.language = lang
        journey_structure = generate_journey_structure()
        
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
        
        # Restore original language
        st.session_state.language = temp_lang

# Initialize journey session state
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

def language_selector():
    """Render language selector"""
    translations = load_translations(st.session_state.language)
    
    st.markdown(f"<div class='language-selector'><span>{translations['language_selector']}</span>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 10])
    
    with col1:
        english_class = "language-button active" if st.session_state.language == "en" else "language-button"
        hindi_class = "language-button active" if st.session_state.language == "hi" else "language-button"
        
        if st.button("English", key="lang_en"):
            st.session_state.language = "en"
            # Reset to intro when changing language
            if st.session_state.page == 'journey':
                st.session_state.current_step = "intro"
                st.session_state.journey_selections = {}
                st.session_state.progress = 0
                st.session_state.video_played = False
            st.rerun()
        
        if st.button("हिन्दी", key="lang_hi"):
            st.session_state.language = "hi"
            # Reset to intro when changing language
            if st.session_state.page == 'journey':
                st.session_state.current_step = "intro"
                st.session_state.journey_selections = {}
                st.session_state.progress = 0
                st.session_state.video_played = False
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

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
    
    translations = load_translations(st.session_state.language)
    
    if st.session_state.journey_selections.get("intro", {}).get("option_id") == "check_status":
        # Translate these steps
        if st.session_state.language == "hi":
            steps = ["शुरू", "स्थिति जांचें", "चैट", ""]
        else:
            steps = ["Start", "Status Check", "Chat", ""]
    else:
        if st.session_state.language == "hi":
            steps = ["शुरू", "ऋण प्रकार", "जानकारी", "अगले कदम"]
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
        translations = load_translations(st.session_state.language)
        
        st.markdown("<div class='info-box'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color:#0066b2; margin-top:0;'>{translations['your_selection']}</h3>", unsafe_allow_html=True)
        
        # Get the selected option from intro and loan_type
        intro_selection = st.session_state.journey_selections.get("intro", {}).get("option_title", "Not selected")
        
        if st.session_state.journey_selections.get("intro", {}).get("option_id") == "new_loan":
            loan_type = st.session_state.journey_selections.get("loan_type", {}).get("option_title", "Not selected")
            st.markdown(f"**{translations['selected_action']}**: {intro_selection}")
            st.markdown(f"**{translations['loan_type_label']}**: {loan_type}")
        else:
            st.markdown(f"**{translations['selected_action']}**: {intro_selection}")
            
        st.markdown("</div>", unsafe_allow_html=True)

# Main journey flow
def render_journey_page():
    # Language selector
    language_selector()
    
    # Get translations for current language
    translations = load_translations(st.session_state.language)
    
    # Generate dynamic journey structure
    journey_structure = generate_journey_structure()
    
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
            if st.button(translations["continue_button"], key="goto_thank_you"):
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
        st.markdown(f"### {translations['your_selection']}: {selected_loan}")
        st.markdown(f"{translations['kyc_message']}", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Add some space
        st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
        
        # Show chatbot button
        if st.button(translations["continue_to_advisor"], key="goto_chatbot"):
            select_option("chat", "Speak with a Loan Advisor", step_data["next_step"])
        
        # Auto-progress functionality for thank_you page
        if st.session_state.video_played:
            # Add a message to let user know they'll be redirected
            st.info(translations["redirecting_message"])
            
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
        reference_number = st.text_input(translations["reference_number_placeholder"], key="reference_number")
        
        # Only enable the button if a reference number is provided
        button_disabled = not reference_number
        
        # Add some space
        st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
        
        # Only show one button
        if st.button(translations["check_status_button"], key="check_status", disabled=button_disabled):
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
            if st.button(translations["start_over"], use_container_width=True):
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
    "personal": {"en": "Personal Loan", "hi": "पर्सनल लोन"},
    "home": {"en": "Home Loan", "hi": "होम लोन"},
    "education": {"en": "Education Loan", "hi": "शिक्षा ऋण"},
    "car": {"en": "Vehicle Loan", "hi": "वाहन ऋण"},
    "business": {"en": "Business Loan", "hi": "व्यापार ऋण"}
}

# Chatbot translations
chatbot_translations = {
    "en": {
        "header": "Loan Advisor Bot",
        "journey_selections": "Your Loan Journey Selections",
        "action_check_status": "Check Application Status",
        "action_apply_loan": "Apply for New Loan",
        "reference_number": "Reference Number",
        "not_provided": "Not provided",
        "applicant_info": "Applicant Information",
        "aadhar_details": "Aadhar Details",
        "pan_details": "PAN Details",
        "annual_income": "Annual Income",
        "employment_type": "Employment Type",
        "employment_options": ["Salaried", "Self-employed", "Business Owner", "Retired", "Other"],
        "chat_header": "Chat with Loan Advisor Bot",
        "message_placeholder": "Type your message here...",
        "application_details": "Application Details",
        "loan_status": "Application Status",
        "status_incomplete": "Incomplete",
        "status_ready": "Ready for Review",
        "missing_fields": "Missing",
        "submit_button": "Submit Application for Review",
        "available_loans": "Available Loan Products",
        "loan_products": [
            "Personal Loan (8-15% interest)",
            "Home Loan (7-9% interest)",
            "Education Loan (6-8% interest)",
            "Vehicle Loan (9-12% interest)"
        ],
        "need_help": "Need Help?",
        "help_contact": [
            "📞 Call: 1800-XXX-XXXX",
            "📧 Email: support@sc-loans.com",
            "🌐 Visit: standardchartered.com/loans"
        ],
        "back_button": "Back to Loan Journey"
    },
    "hi": {
        "header": "ऋण सलाहकार बॉट",
        "journey_selections": "आपके ऋण यात्रा चयन",
        "action_check_status": "आवेदन स्थिति जांचें",
        "action_apply_loan": "नए ऋण के लिए आवेदन करें",
        "reference_number": "संदर्भ संख्या",
        "not_provided": "प्रदान नहीं किया गया",
        "applicant_info": "आवेदक जानकारी",
        "aadhar_details": "आधार विवरण",
        "pan_details": "पैन विवरण",
        "annual_income": "वार्षिक आय",
        "employment_type": "रोजगार प्रकार",
        "employment_options": ["वेतनभोगी", "स्वरोजगार", "व्यवसाय मालिक", "सेवानिवृत्त", "अन्य"],
        "chat_header": "ऋण सलाहकार बॉट के साथ चैट करें",
        "message_placeholder": "अपना संदेश यहां लिखें...",
        "application_details": "आवेदन विवरण",
        "loan_status": "आवेदन की स्थिति",
        "status_incomplete": "अधूरा",
        "status_ready": "समीक्षा के लिए तैयार",
        "missing_fields": "अनुपलब्ध",
        "submit_button": "समीक्षा के लिए आवेदन जमा करें",
        "available_loans": "उपलब्ध ऋण उत्पाद",
        "loan_products": [
            "पर्सनल लोन (8-15% ब्याज)",
            "होम लोन (7-9% ब्याज)",
            "शिक्षा ऋण (6-8% ब्याज)",
            "वाहन ऋण (9-12% ब्याज)"
        ],
        "need_help": "मदद चाहिए?",
        "help_contact": [
            "📞 कॉल करें: 1800-XXX-XXXX",
            "📧 ईमेल: support@sc-loans.com",
            "🌐 विजिट करें: standardchartered.com/loans"
        ],
        "back_button": "ऋण यात्रा पर वापस जाएं"
    }
}

def render_chatbot_page():
    # Language selector
    language_selector()
    
    # Get translations for current language
    translations = chatbot_translations[st.session_state.language]
    
    # Get data from journey selections
    journey_data = st.session_state.journey_selections
    loan_type = journey_data.get("loan_type", {}).get("option_id", "")
    is_status_check = journey_data.get("intro", {}).get("option_id", "") == "check_status"
    reference_number = st.session_state.get("reference_number", "")
    
    # Display the header
    st.markdown(f'<h1 class="main-header">{translations["header"]}</h1>', unsafe_allow_html=True)
    
    # Show journey info
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown(f"<h3>{translations['journey_selections']}</h3>", unsafe_allow_html=True)
    
    # Display selections based on previous choices
    if is_status_check:
        col1, col2 = st.columns(2)
        col1.metric("Action", translations["action_check_status"])
        col2.metric(translations["reference_number"], reference_number if reference_number else translations["not_provided"])
    else:
        col1, col2 = st.columns(2)
        col1.metric("Action", translations["action_apply_loan"])
        loan_display = loan_type_map.get(loan_type, {}).get(st.session_state.language, translations["not_provided"])
        col2.metric(translations["loan_type_label"] if st.session_state.language == "hi" else "Loan Type", loan_display)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input fields for user details
    st.markdown(f'<h2 class="sub-header">{translations["applicant_info"]}</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        aadhar_details = st.text_input(translations["aadhar_details"])
        pan_details = st.text_input(translations["pan_details"])
    with col2:
        income = st.text_input(translations["annual_income"])
        employment_type = st.selectbox(translations["employment_type"], translations["employment_options"])
    
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
    User Language: {language}
    
    If the user's language is Hindi (hi), please respond in Hindi.
    If the user's language is English (en), please respond in English.
    
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
        
        # Generate initial message based on language
        if st.session_state.language == "hi":
            initial_message = "नमस्ते! मैं स्टैंडर्ड चार्टर्ड बैंक में आपका ऋण सलाहकार बॉट हूँ।"
            
            if is_status_check:
                initial_message += f" मैं देख रहा हूँ कि आप अपने आवेदन की स्थिति जांच रहे हैं{' #' + reference_number if reference_number else ''}। सत्यापन के लिए कृपया अपना आधार और पैन विवरण की पुष्टि करें।"
            else:
                loan_name = loan_type_map.get(loan_type, {}).get("hi", "ऋण")
                initial_message += f" मैं देख रहा हूँ कि आप {loan_name} में रुचि रखते हैं। मैं आपको आवेदन पूरा करने में मदद करूँगा। कृपया अपनी आय जानकारी के साथ अपना आधार और पैन विवरण प्रदान करें।"
        else:
            initial_message = "Hello! I'm your loan advisor bot at Standard Chartered Bank."
            
            if is_status_check:
                initial_message += f" I see you're checking the status of your application{' #' + reference_number if reference_number else ''}. Could you please confirm your Aadhar and PAN details for verification?"
            else:
                loan_name = loan_type_map.get(loan_type, {}).get("en", "loan")
                initial_message += f" I see you're interested in a {loan_name}. Let me help you complete your application. Please provide your Aadhar and PAN details along with your income information."
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": initial_message
        })
    
    # Display chat messages
    st.markdown(f'<h2 class="sub-header">{translations["chat_header"]}</h2>', unsafe_allow_html=True)
    
    # Chat message display with better styling
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    user_message = st.chat_input(translations["message_placeholder"])
    
    if user_message:
        # Add user message to display
        st.session_state.messages.append({"role": "user", "content": user_message})
        
        # Determine values to use in prompt
        if st.session_state.language == "hi":
            loan_type_value = loan_type_map.get(loan_type, {}).get("hi", translations["not_provided"])
        else:
            loan_type_value = loan_type_map.get(loan_type, {}).get("en", translations["not_provided"])
        
        try:
            if chat:
                # Generate response using the chain
                response = chain.invoke({
                    "input": user_message,
                    "aadhar_details": aadhar_details or translations["not_provided"],
                    "pan_details": pan_details or translations["not_provided"],
                    "income": income or translations["not_provided"],
                    "employment_type": employment_type,
                    "loan_type": loan_type_value,
                    "reference_number": reference_number or translations["not_provided"],
                    "is_status_check": "Yes" if is_status_check else "No",
                    "language": st.session_state.language
                })
                
                # Add bot response to display
                st.session_state.messages.append({"role": "assistant", "content": response.content})
            else:
                # Fallback response if API not configured
                fallback_msg = "मुझे खेद है, मुझे अपने ज्ञान आधार से कनेक्ट करने में समस्या हो रही है। कृपया सुनिश्चित करें कि GROQ API की सही तरह से कॉन्फ़िगर की गई है।" if st.session_state.language == "hi" else "I'm sorry, I'm having trouble connecting to my knowledge base. Please make sure the GROQ API key is properly configured."
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": fallback_msg
                })
        except Exception as e:
            # Fallback response if API fails
            fallback_msg = "मुझे खेद है, मैं आपके अनुरोध को संसाधित करने में समस्या हो रही है। कृपया पुन: प्रयास करें या अपने ऋण आवश्यकताओं के बारे में अधिक जानकारी प्रदान करें।" if st.session_state.language == "hi" else "I'm sorry, I'm having trouble processing your request. Please try again or provide more information about your loan requirements."
            st.session_state.messages.append({
                "role": "assistant", 
                "content": fallback_msg
            })
            st.error(f"Error: {str(e)}")
        
        # Rerun to update the chat display
        st.rerun()
    
    # Display additional details in the sidebar
    with st.sidebar:
        st.header(translations["application_details"])
        st.write(f"{translations['aadhar_details']}: {aadhar_details or translations['not_provided']}")
        st.write(f"{translations['pan_details']}: {pan_details or translations['not_provided']}")
        st.write(f"{translations['annual_income']}: {income or translations['not_provided']}")
        st.write(f"{translations['employment_type']}: {employment_type}")
        
        if not is_status_check:
            st.write(f"{translations['loan_type_label'] if st.session_state.language == 'hi' else 'Loan Type'}: {loan_type_value}")
        else:
            st.write(f"{translations['reference_number']}: {reference_number or translations['not_provided']}")
        
        # Application status section
        st.header(translations["loan_status"])
        
        # Determine status based on provided information
        missing_fields = []
        if not aadhar_details:
            missing_fields.append(translations["aadhar_details"])
        if not pan_details:
            missing_fields.append(translations["pan_details"])
        if not income:
            missing_fields.append(translations["annual_income"])
        
        if missing_fields:
            status = translations["status_incomplete"]
            status_color = "🔴"
            missing_text = ", ".join(missing_fields)
            st.write(f"{status_color} {translations['loan_status']}: {status} ({translations['missing_fields']}: {missing_text})")
        else:
            status = translations["status_ready"]
            status_color = "🟡"
            st.write(f"{status_color} {translations['loan_status']}: {status}")
            st.button(translations["submit_button"], type="primary")
        
        # Add a section for loan options
        st.header(translations["available_loans"])
        for product in translations["loan_products"]:
            st.write(f"- {product}")
        
        # Help section
        st.header(translations["need_help"])
        for contact in translations["help_contact"]:
            st.write(contact)
    
    # Button to go back to journey
    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button(translations["back_button"], use_container_width=True):
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