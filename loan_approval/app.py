from fastapi import FastAPI
import joblib
import pandas as pd


app = FastAPI()


model = joblib.load(r"C:\Users\Tamanna Grover\Loan-Approval-Predictor\best_model.pkl")  # Make sure your .pkl file is in the same folder

@app.post("/predict/")
async def predict(input_data: dict):
    
    df = pd.DataFrame([input_data])
    
    prediction = model.predict(df)
    return {"loan_approval": bool(prediction[0])}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Loan Approval API!"}
