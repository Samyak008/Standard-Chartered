import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .controllers import user_controller, webrtc_controller

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
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)