from fastapi import HTTPException
from typing import Dict, Any

def verify_face(image: Any) -> bool:
    # Placeholder function for face verification logic
    # Implement face recognition logic here
    return True

def check_eligibility(user_data: Dict[str, Any]) -> bool:
    # Placeholder function for eligibility check logic
    # Implement eligibility criteria based on user data here
    return user_data.get("income", 0) > 30000  # Example condition based on income

def process_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
    if not check_eligibility(user_data):
        raise HTTPException(status_code=400, detail="User is not eligible for the loan.")
    
    # Further processing of user data can be done here
    return {"status": "success", "message": "User data processed successfully."}