# api/routes/predict.py
import os
import sys
import pandas as pd
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from utils.s3_loader import load_csv_from_s3, log_prediction, log_error
from api.auth.dependencies import require_billing_analyst

PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from api.schemas.request_schema import ClaimRequest
from api.schemas.response_schema import ClaimResponse
from api.services.orchestration_service import ClaimOrchestrator

router = APIRouter()

diagnosis_df         = load_csv_from_s3("data/diagnosis.csv")
providers_df         = load_csv_from_s3("data/providers_1000.csv")
cost_df              = load_csv_from_s3("data/cost.csv")
historical_claims_df = load_csv_from_s3("data/claims_1000.csv")

orchestrator = ClaimOrchestrator(
    diagnosis_df=diagnosis_df,
    providers_df=providers_df,
    cost_df=cost_df,
    historical_claims_df=historical_claims_df
)

@router.post("/predict-claim", response_model=ClaimResponse)
async def predict_claim(
    request: ClaimRequest,
    user: dict = Depends(require_billing_analyst)
):
    try:
        payload = request.model_dump() if hasattr(request, "model_dump") else request.dict()
        result  = orchestrator.process_claim(payload)

        if result is None:
            raise ValueError("process_claim returned None")

        # Pass username so S3 log records who ran it
        result_dict = result if isinstance(result, dict) else result.dict()
        log_prediction(payload["claim_id"], payload, result_dict, username=user.get("sub", "unknown"))

        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        log_error(request.claim_id, str(e), username=user.get("sub", "unknown"))
        raise HTTPException(status_code=500, detail=str(e))