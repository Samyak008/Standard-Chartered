from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, List, Optional
import uvicorn
import json
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from crew_api import process_loan_application
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoanRequest(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        extra='forbid'
    )
    
    loan_purpose: str = Field(default="personal")
    loan_amount: float = Field(gt=0)
    loan_term: str = Field(default="12 months")
    credit_score: int = Field(ge=300, le=850)
    income: float = Field(gt=0)
    employment_length: str
    debt_to_income_ratio: float = Field(ge=0, le=1)
    has_coi: bool = Field(default=False)
    has_collateral: bool = Field(default=False)
    has_employment_guarantee: bool = Field(default=False)

# Dummy loan products database
LOAN_PRODUCTS = {
    "personal": {
        "name": "Personal Loan",
        "interest_rate": 10.5,
        "min_amount": 10000,
        "max_amount": 500000,
        "terms": ["12 months", "24 months", "36 months"]
    },
    "business": {
        "name": "Business Loan",
        "interest_rate": 12.0,
        "min_amount": 100000,
        "max_amount": 5000000,
        "terms": ["24 months", "36 months", "48 months"]
    },
    "home": {
        "name": "Home Loan",
        "interest_rate": 8.5,
        "min_amount": 500000,
        "max_amount": 10000000,
        "terms": ["60 months", "120 months", "180 months"]
    }
}

# Add this after LOAN_PRODUCTS dictionary
DUMMY_LOAN_REQUEST = {
    "loan_purpose": "personal",
    "loan_amount": 300000,
    "loan_term": "24 months",
    "credit_score": 750,
    "income": 800000,
    "employment_length": "5 years",
    "debt_to_income_ratio": 0.3,
    "has_coi": True,
    "has_collateral": False,
    "has_employment_guarantee": True
}

def generate_dummy_report(loan_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a dummy loan analysis report"""
    
    # Calculate basic metrics
    monthly_income = loan_data["income"] / 12
    monthly_payment = loan_data["loan_amount"] / float(loan_data["loan_term"].split()[0])
    payment_to_income = monthly_payment / monthly_income
    
    # Risk scoring
    risk_score = 0
    risk_score += min(loan_data["credit_score"] / 850 * 40, 40)  # Max 40 points for credit score
    risk_score += 20 if loan_data["has_coi"] else 0  # 20 points for certificate of income
    risk_score += 25 if loan_data["has_collateral"] else 0  # 25 points for collateral
    risk_score += 15 if loan_data["has_employment_guarantee"] else 0  # 15 points for employment
    
    # Determine suitable loan products
    suitable_products = []
    for product_id, product in LOAN_PRODUCTS.items():
        if (product["min_amount"] <= loan_data["loan_amount"] <= product["max_amount"] and
            loan_data["loan_term"] in product["terms"]):
            suitable_products.append({
                "product_name": product["name"],
                "interest_rate": product["interest_rate"],
                "monthly_payment": monthly_payment * (1 + product["interest_rate"]/100),
                "total_repayment": monthly_payment * (1 + product["interest_rate"]/100) * float(loan_data["loan_term"].split()[0])
            })
    
    return {
        "loan_options": {
            "suitable_products": suitable_products,
            "recommended_product": suitable_products[0] if suitable_products else None,
            "alternative_terms": LOAN_PRODUCTS.get(loan_data["loan_purpose"].lower(), {}).get("terms", [])
        },
        "risk_analysis": {
            "risk_score": risk_score,
            "risk_level": "Low" if risk_score >= 80 else "Medium" if risk_score >= 60 else "High",
            "monthly_metrics": {
                "income": monthly_income,
                "payment": monthly_payment,
                "payment_to_income_ratio": payment_to_income
            },
            "approval_likelihood": "Approved" if risk_score >= 70 else "Under Review" if risk_score >= 50 else "Likely Declined",
            "recommendations": [
                "Consider adding collateral to improve terms" if not loan_data["has_collateral"] else None,
                "Providing employment guarantee may help" if not loan_data["has_employment_guarantee"] else None,
                "Credit score improvement recommended" if loan_data["credit_score"] < 700 else None
            ]
        }
    }

class LoanOptionsResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    raw_text: str
    recommendations: List[str] = []
    products: List[Dict[str, Any]] = []
    terms: List[str] = []

class RiskAnalysisResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    raw_text: str
    summary: str = ""
    risk_score: float = 0
    risk_level: str = "Medium"
    recommendations: List[str] = []

class LoanResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    success: bool
    timestamp: str
    loan_options: LoanOptionsResponse
    risk_analysis: RiskAnalysisResponse

# Modify the process_loan endpoint
@app.post("/process-loan", response_model=LoanResponse)
async def process_loan(request: LoanRequest):
    try:
        result = await process_loan_application(request.model_dump())
        
        return LoanResponse(
            success=True,
            timestamp=datetime.now().isoformat(),
            loan_options=LoanOptionsResponse(**result["loan_options"]),
            risk_analysis=RiskAnalysisResponse(**result["risk_analysis"])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def main():
    """Main function to run the FastAPI application"""
    try:
        uvicorn.run(
            "loan_api:app",
            host="127.0.0.1",
            port=5000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"Failed to start server: {e}")

if __name__ == "__main__":
    main()