from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crew_api import process_loan_application
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoanRequest(BaseModel):
    loan_purpose: str
    loan_amount: float
    loan_term: str
    credit_score: int
    income: float
    employment_length: str
    debt_to_income_ratio: float
    has_coi: bool
    has_collateral: bool
    has_employment_guarantee: bool

@app.post("/process-loan")
async def process_loan(request: LoanRequest):
    try:
        result = await process_loan_application(request.dict())
        return {
            "success": True,
            "loan_options": result.loan_options,
            "risk_analysis": result.risk_analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))