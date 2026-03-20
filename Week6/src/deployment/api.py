from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
import uuid
from datetime import datetime
import json
import os

MODEL_PATH  = "src/models/tuned_model.pkl"
SCALER_PATH = "src/models/scaler.pkl"        
FEATURE_PATH     = "src/features/feature_list.json"
NUMERIC_COLS_PATH = "src/features/numeric_cols.json"
LOG_PATH    = "src/prediction_logs.csv"

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)           

with open(FEATURE_PATH, "r") as f:
    feature_list = json.load(f)

with open(NUMERIC_COLS_PATH, "r") as f:
    numeric_cols = json.load(f)

app = FastAPI()


class Passenger(BaseModel):
    Pclass: int
    Age: float
    SibSp: int
    Parch: int
    Fare: float
    Sex: str
    Embarked: str
    Name: str
    Ticket: str


def preprocess_input(data):
    df = pd.DataFrame([data])

    # Feature engineering — same as build_features.py
    df["FamilySize"]   = df["SibSp"] + df["Parch"] + 1
    df["IsAlone"]      = (df["FamilySize"] == 1).astype(int)
    df["FarePerPerson"] = df["Fare"] / df["FamilySize"]
    df["TicketLength"] = df["Ticket"].astype(str).apply(len)
    df["FareLog"]      = df["Fare"].apply(lambda x: 0 if x <= 0 else np.log1p(x))
    df["AgeSquared"]   = df["Age"] ** 2
    df["FamilyFare"]   = df["FamilySize"] * df["Fare"]
    df["AgeClass"]     = df["Age"] * df["Pclass"]

    df["AgeGroup"] = pd.cut(
        df["Age"],
        bins=[0, 12, 18, 35, 60, 100],
        labels=["Child", "Teen", "YoungAdult", "Adult", "Senior"]
    )

    df["Title"] = df["Name"].str.extract(r" ([A-Za-z]+)\.", expand=False)

    # Drop text columns BEFORE encoding — otherwise get_dummies
    #    encodes Name and Ticket creating garbage columns
    df = df.drop(columns=["Name", "Ticket"])

    # Encode only the specific categorical columns, not everything
    df = pd.get_dummies(df, columns=["Sex", "Embarked", "Title", "AgeGroup"])

    # Apply the same scaler used during training
    #    Only scale columns that exist in both the input and the fitted list
    cols_to_scale = [c for c in numeric_cols if c in df.columns]
    df[cols_to_scale] = scaler.transform(df[cols_to_scale])

    # Align columns with training features (add missing as 0, drop extras)
    for col in feature_list:
        if col not in df.columns:
            df[col] = 0

    df = df[feature_list]

    return df

# -------------------------
# Logging
# -------------------------
def log_prediction(request_id, input_data, prediction, confidence):

    log_entry = {
        "request_id": request_id,
        "timestamp": str(datetime.now()),
        "input": json.dumps(input_data),   # serialize dict → JSON string, safe for CSV
        "prediction": int(prediction),
        "confidence": float(confidence)
    }

    df = pd.DataFrame([log_entry])

    if not os.path.exists(LOG_PATH):
        df.to_csv(LOG_PATH, index=False)
    else:
        df.to_csv(LOG_PATH, mode="a", header=False, index=False)


# -------------------------
# API endpoint
# -------------------------
@app.post("/predict")
def predict(passenger: Passenger):

    try:
        request_id = str(uuid.uuid4())

        input_data = passenger.dict()

        processed = preprocess_input(input_data)

        pred = model.predict(processed)[0]

        proba = model.predict_proba(processed)[0][1]

        log_prediction(request_id, input_data, pred, proba)

        return {
            "request_id": request_id,
            "prediction": int(pred),
            "confidence": float(proba),
            "status": "success"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))