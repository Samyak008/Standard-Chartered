import logging
import sys
import os
from pathlib import Path

# Add the parent directory to sys.path to allow absolute imports
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import controllers - use absolute imports instead of relative
from backend.controllers import user_controller, webrtc_controller

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(title="Virtual Branch Manager API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_controller.router, prefix="/api/users", tags=["users"])
app.include_router(webrtc_controller.router, prefix="/api/webrtc", tags=["webrtc"])

@app.get("/")
async def root():
    return {"message": "Virtual Branch Manager API is running"}

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run("app:app", host=host, port=port, reload=debug)