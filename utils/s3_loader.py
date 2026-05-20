import boto3
import io
import pickle
import pandas as pd

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