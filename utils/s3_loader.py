import boto3
import io
import json
import pickle
import pandas as pd
from datetime import datetime

S3_BUCKET = "abacus-claim-predictor"

def get_s3_client():
    return boto3.client("s3", region_name="us-east-1")

def load_pickle_from_s3(key: str):
    """Download a .pkl file from S3 and unpickle it."""
    s3 = get_s3_client()
    obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
    return pickle.load(io.BytesIO(obj["Body"].read()))

def load_csv_from_s3(key: str) -> pd.DataFrame:
    """Download a CSV from S3 and return as DataFrame."""
    s3 = get_s3_client()
    obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
    return pd.read_csv(io.BytesIO(obj["Body"].read()))

def load_faiss_index_from_s3(key: str):
    """Download FAISS index from S3 to a temp file and load it."""
    import faiss
    import tempfile
    s3 = get_s3_client()
    obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
    with tempfile.NamedTemporaryFile(suffix=".index", delete=False) as tmp:
        tmp.write(obj["Body"].read())
        tmp_path = tmp.name
    return faiss.read_index(tmp_path)

def log_prediction(claim_id: str, payload: dict, result: dict, username: str = "unknown"):
    """Log a prediction result to S3."""
    try:
        s3 = get_s3_client()
        key = f"logs/predictions/{datetime.utcnow().strftime('%Y/%m/%d')}/{claim_id}_{datetime.utcnow().strftime('%H%M%S')}.json"
        body = json.dumps({
            "claim_id":  claim_id,
            "user":      username,
            "payload":   payload,
            "result":    result,
            "timestamp": datetime.utcnow().isoformat()
        }, default=str)
        s3.put_object(Bucket=S3_BUCKET, Key=key, Body=body, ContentType="application/json")
    except Exception as e:
        print(f"Warning: could not log prediction to S3: {e}")

def log_error(claim_id: str, error: str, username: str = "unknown"):
    """Log an error to S3."""
    try:
        s3 = get_s3_client()
        key = f"logs/errors/{datetime.utcnow().strftime('%Y/%m/%d')}/{claim_id}_{datetime.utcnow().strftime('%H%M%S')}.json"
        body = json.dumps({
            "claim_id":  claim_id,
            "user":      username,
            "error":     error,
            "timestamp": datetime.utcnow().isoformat()
        })
        s3.put_object(Bucket=S3_BUCKET, Key=key, Body=body, ContentType="application/json")
    except Exception as e:
        print(f"Warning: could not log error to S3: {e}")