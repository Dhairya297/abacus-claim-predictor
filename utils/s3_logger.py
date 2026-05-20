# utils/s3_logger.py
import boto3, json
from datetime import datetime

s3 = boto3.client("s3", region_name="us-east-1")

def log_prediction(claim_id: str, payload: dict, result: dict):
    key = f"logs/predictions/{datetime.utcnow().strftime('%Y/%m/%d')}/{claim_id}.json"
    body = json.dumps({"payload": payload, "result": result, "timestamp": datetime.utcnow().isoformat()})
    s3.put_object(Bucket="abacus-claim-predictor", Key=key, Body=body, ContentType="application/json")

def log_error(claim_id: str, error: str):
    key = f"logs/errors/{datetime.utcnow().strftime('%Y/%m/%d')}/{claim_id}.json"
    body = json.dumps({"claim_id": claim_id, "error": error, "timestamp": datetime.utcnow().isoformat()})
    s3.put_object(Bucket="abacus-claim-predictor", Key=key, Body=body, ContentType="application/json")