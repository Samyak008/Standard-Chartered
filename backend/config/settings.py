DATABASE_URL = "sqlite:///./database.db"
SECRET_KEY = "your_secret_key"
DEBUG = True

# OCR Configuration
OCR_TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Update this path as necessary
OCR_LANG = "eng"

# AI Service Configuration
AI_MODEL_PATH = "./models/ai_model.h5"  # Path to your AI model

# CORS Configuration
CORS_ORIGINS = [
    "http://localhost:3000",  # React app URL
]