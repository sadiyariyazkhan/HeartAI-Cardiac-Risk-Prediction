import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI(title="HeartAI Engine")

BASE_DIR = Path(r"C:\Heart disease project ML")
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR))

# Load model and scaler
model = joblib.load(BASE_DIR / "model.pkl")
scaler = joblib.load(BASE_DIR / "scaler.pkl")

# Pydantic model matching JavaScript payload
class PatientData(BaseModel):
    Age: int
    Sex: int
    ChestPainType: int
    RestingBP: int
    Cholesterol: int
    FastingBS: int
    RestingECG: int
    MaxHR: int
    ExerciseAngina: int
    Oldpeak: float
    ST_Slope: int

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict")
async def predict(data: PatientData):
    # Construct input dataframe matching model features
    feature_dict = {
        'Age': [data.Age],
        'Sex': [data.Sex],
        'ChestPainType': [data.ChestPainType],
        'RestingBP': [data.RestingBP],
        'Cholesterol': [data.Cholesterol],
        'FastingBS': [data.FastingBS],
        'RestingECG': [data.RestingECG],
        'MaxHR': [data.MaxHR],
        'ExerciseAngina': [data.ExerciseAngina],
        'Oldpeak': [data.Oldpeak],
        'ST_Slope': [data.ST_Slope]
    }
    
    features_df = pd.DataFrame(feature_dict)
    scaled_features = scaler.transform(features_df)
    
    # Get probability for heart disease (class 1)
    if hasattr(model, "predict_proba"):
        risk_probability = float(model.predict_proba(scaled_features)[0][1]) * 100
    else:
        pred = int(model.predict(scaled_features)[0])
        risk_probability = 85.0 if pred == 1 else 15.0

    # Categorize into High, Medium, or Low Risk
    if risk_probability >= 65.0:
        risk_level = "High Risk"
        recommendation = "Immediate clinical evaluation and further diagnostic workup recommended."
    elif risk_probability >= 35.0:
        risk_level = "Medium Risk"
        recommendation = "Moderate risk factors detected. Lifestyle modifications and routine follow-up suggested."
    else:
        risk_level = "Low Risk"
        recommendation = "Biomarkers are within healthy ranges. Maintain regular health monitoring."

    return {
        "risk_score": round(risk_probability, 1),
        "risk_level": risk_level,
        "recommendation": recommendation
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)