# prediction_service.py

import os
import sys
import pickle
import pandas as pd
from pathlib import Path

PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml_training.prediction import PredictionEngine
from utils.logger import logger
from utils.s3_loader import load_pickle_from_s3

class PredictionService:

    def __init__(self):
        logger.info("Loading ML artifacts.")
        self.model           = load_pickle_from_s3("artifacts/models/claim_denial_xgboost_model.pkl")
        self.explainer       = load_pickle_from_s3("artifacts/models/claim_denial_shap_explainer.pkl")
        self.thresholds      = load_pickle_from_s3("artifacts/models/claim_denial_thresholds.pkl")
        self.feature_columns = load_pickle_from_s3("artifacts/models/feature_columns.pkl")
        logger.info("ML artifacts loaded successfully.")

    def predict(self, feature_df):
        prediction_result = PredictionEngine.predict_claim(
            model=self.model,
            explainer=self.explainer,
            claim_input_df=feature_df,
            threshold=self.thresholds["base_denial_threshold"],
            shap=__import__("shap"),
            feature_columns=self.feature_columns
        )

        probability = prediction_result["risk_score"] / 100
        approve_threshold = self.thresholds["approve_threshold"]
        deny_threshold = self.thresholds["deny_threshold"]

        if probability < approve_threshold:
            risk_level = "LOW"          
            prediction = "APPROVED"
            risk_level_label = "LOW RISK — Claim is likely to be approved."
        elif probability > deny_threshold:
            risk_level = "HIGH"
            prediction = "DENIED"
            risk_level_label = "HIGH RISK — Claim is likely to be denied."
        else:
            risk_level = "MEDIUM"
            prediction = "NEED TO BE REVIEWED"
            risk_level_label = "MEDIUM RISK — Claim needs to be reviewed."

        return {
            "prediction":        prediction,
            "risk_score":        prediction_result["risk_score"],
            "risk_level":        risk_level,            
            "risk_level_label":  risk_level_label,
            "top_reasons":       prediction_result["top_reasons"].to_dict(orient="records"),
            "approve_threshold": approve_threshold,
            "deny_threshold":    deny_threshold,
        }