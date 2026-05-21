# api/routes/history_routes.py
import json
import boto3
from fastapi import APIRouter, Depends, HTTPException
from api.auth.dependencies import require_billing_analyst

router = APIRouter(prefix="/history", tags=["history"])

S3_BUCKET = "abacus-claim-predictor"
LOG_PREFIX = "logs/predictions/"

def get_s3_client():
    return boto3.client("s3", region_name="us-east-1")

@router.get("")
def get_history(user: dict = Depends(require_billing_analyst)):
    """List all prediction logs from S3, newest first."""
    try:
        s3 = get_s3_client()

        # List all objects under logs/predictions/
        paginator = s3.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=S3_BUCKET, Prefix=LOG_PREFIX)

        keys = []
        for page in pages:
            for obj in page.get("Contents", []):
                keys.append(obj["Key"])

        if not keys:
            return []

        # Sort newest first (keys are YYYY/MM/DD/claimid.json)
        keys.sort(reverse=True)

        # Read each file (cap at 100 most recent)
        records = []
        for key in keys[:100]:
            try:
                obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
                data = json.loads(obj["Body"].read())
                records.append(data)
            except Exception:
                continue

        return records

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load history: {str(e)}")