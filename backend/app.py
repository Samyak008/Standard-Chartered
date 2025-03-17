from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers.user_controller import UserController

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize UserController
user_controller = UserController()

# API routes
@app.post("/register")
async def register_user(user_data: dict):
    return await user_controller.register_user(user_data)

@app.post("/login")
async def login_user(credentials: dict):
    return await user_controller.login_user(credentials)

@app.post("/upload")
async def upload_document(document: dict):
    return await user_controller.upload_document(document)

# Add more routes as needed

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)