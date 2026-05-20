import os
import sys
import pandas as pd
from pathlib import Path
from fastapi import APIRouter, HTTPException
from utils.s3_loader import log_prediction, log_error
import boto3
import io

PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from api.schemas.request_schema import ClaimRequest
from api.schemas.response_schema import ClaimResponse
from api.services.orchestration_service import ClaimOrchestrator
from utils.s3_loader import load_csv_from_s3

router = APIRouter()

S3_BUCKET = "abacus-claim-predictor"
def load_csv_from_s3(key: str) -> pd.DataFrame:
    """Download a CSV from S3 and return as DataFrame."""
    try:
        s3 = boto3.client("s3", region_name="us-east-1")
        obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
        return pd.read_csv(io.BytesIO(obj["Body"].read()))
    except Exception as e:
        # Fallback to local path for development
        local_path = os.path.join(PROJECT_ROOT, key)
        if os.path.exists(local_path):
            return pd.read_csv(local_path)
        raise FileNotFoundError(f"Could not load {key} from S3 or locally: {e}")

diagnosis_df = load_csv_from_s3("data/diagnosis.csv")
providers_df = load_csv_from_s3("data/providers_1000.csv")
cost_df = load_csv_from_s3("data/cost.csv")
historical_claims_df = load_csv_from_s3("data/claims_1000.csv")

orchestrator = ClaimOrchestrator(
    diagnosis_df=diagnosis_df,
    providers_df=providers_df,
    cost_df=cost_df,
    historical_claims_df=historical_claims_df
)

@router.post("/predict-claim", response_model=ClaimResponse)
async def predict_claim(request: ClaimRequest):
    try:
        payload = request.model_dump() if hasattr(request, "model_dump") else request.dict()
        result = orchestrator.process_claim(payload)
        log_prediction(payload["claim_id"], payload, result)
        if result is None:
            raise ValueError("process_claim returned None")

        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))