import os
import sys
from pathlib import Path

PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from feature_pipeline.input_processing import RealtimeFeaturePipeline
from api.services.prediction_service import PredictionService
from api.services.rag_service import RAGService
from api.services.recommendation_service import RecommendationService
from utils.logger import logger


class ClaimOrchestrator:

    def __init__(self, diagnosis_df, providers_df, cost_df, historical_claims_df):
        self.feature_pipeline = RealtimeFeaturePipeline(
            diagnosis_df=diagnosis_df,
            providers_df=providers_df,
            cost_df=cost_df,
            historical_claims_df=historical_claims_df
        )
        self.prediction_service = PredictionService()
        self.rag_service        = RAGService()

    def process_claim(self, claim_payload: dict) -> dict:

        # STEP 1: FEATURE ENGINEERING ──────────────────────────────
        feature_df = self.feature_pipeline.transform_single_claim(claim_payload)

        # STEP 2: ML PREDICTION ─────────────────────────────────────
        prediction_result = self.prediction_service.predict(feature_df)

        risk_level = prediction_result["risk_level"]              # "LOW" / "MEDIUM" / "HIGH"
        logger.info("Claim %s → risk_level=%s, risk_score=%.1f",
                    claim_payload.get("claim_id"), risk_level,
                    prediction_result["risk_score"])

        # ── STEP 3: APPROVED → return immediately, skip RAG + LLM ─────
        if risk_level == "LOW":
            return {
                "claim_id":          claim_payload["claim_id"],
                "prediction":        prediction_result["prediction"],
                "risk_level":        risk_level,
                "risk_score":        prediction_result["risk_score"],
                "approve_threshold": prediction_result["approve_threshold"],
                "deny_threshold":    prediction_result["deny_threshold"],
                "top_reasons":       [],
                "policy_summary":    None,
                "recommendations":   [],
                "next_action":       None,
            }

        # ── STEP 4: DENIED / MEDIUM → RAG retrieval
        rag_query = f"""
        Healthcare claim denial review.
        Prediction: {prediction_result['prediction']}
        Denial reasons: {[r['business_reason'] for r in prediction_result['top_reasons']]}
        Diagnosis: {claim_payload.get('diagnosis_code')}
        Procedure: {claim_payload.get('procedure_code')}
        """
        policy_context = self.rag_service.retrieve_policy_context(rag_query)
        logger.info("RAG retrieved %d policy chunks.", len(policy_context))

        # ── STEP 5: LLM RECOMMENDATION + POLICY SUMMARY ───────────────
        llm_result = RecommendationService().generate_recommendation(
            prediction     = prediction_result["prediction"],
            risk_score     = prediction_result["risk_score"],
            top_reasons    = prediction_result["top_reasons"],
            retrieved_policies = policy_context
        )

        # ── STEP 6: EXTRACT FIELDS EXPLICITLY ────────────────────────
        policy_summary  = llm_result.get("policy_summary",  None)
        recommendations = llm_result.get("recommendations", [])
        next_action     = llm_result.get("next_action",     None)

        return {
            "claim_id":          claim_payload["claim_id"],
            "prediction":        prediction_result["prediction"],
            "risk_level":        risk_level,
            "risk_score":        prediction_result["risk_score"],
            "approve_threshold": prediction_result["approve_threshold"],
            "deny_threshold":    prediction_result["deny_threshold"],
            "top_reasons":       prediction_result["top_reasons"],  # SHAP-driven list
            "policy_summary":    policy_summary,                    # LLM paragraph
            "recommendations":   recommendations,                   # list of {reason, action}
            "next_action":       next_action,                       # single urgent string
        }