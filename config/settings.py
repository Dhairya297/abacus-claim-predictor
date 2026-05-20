import os
from pathlib import Path
import json
import boto3
from dotenv import load_dotenv

# ─────────────────────────────────────────────
# PROJECT ROOT
# ─────────────────────────────────────────────
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)

# ─────────────────────────────────────────────
# ENVIRONMENT DETECTION
# ─────────────────────────────────────────────
IS_DATABRICKS = os.path.exists(
    "/Workspace/Users/dhairyashimpi@gmail.com/Abacus Intern Project"
)

IS_AWS = os.environ.get("DEPLOYMENT_ENV") == "aws"
IS_LOCAL = not IS_DATABRICKS and not IS_AWS

# ─────────────────────────────────────────────
# LOAD .ENV EARLY (SAFE FOR LOCAL + EC2)
# ─────────────────────────────────────────────
if IS_LOCAL or IS_DATABRICKS:
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

# ─────────────────────────────────────────────
# AWS SECRETS HELPER
# ─────────────────────────────────────────────
def get_secret(secret_name: str) -> dict:
    client = boto3.client("secretsmanager", region_name="us-east-1")
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])

# ─────────────────────────────────────────────
# OPENAI KEY LOADING (ROBUST)
# ─────────────────────────────────────────────
def get_openai_key():
    # 1. AWS production
    if IS_AWS:
        secrets = get_secret("abacus/openai")
        return secrets["OPENAI_API_KEY"]

    # 2. Local / Databricks
    key = os.getenv("OPENAI_API_KEY")

    if not key:
        raise ValueError(
            "OPENAI_API_KEY not found.\n"
            "Fix options:\n"
            "1. Create .env file in project root\n"
            "2. OR set environment variable OPENAI_API_KEY\n"
        )

    return key


OPENAI_API_KEY = get_openai_key()

# ─────────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────────
OPENAI_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"

# ─────────────────────────────────────────────
# CHUNKING
# ─────────────────────────────────────────────
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# ─────────────────────────────────────────────
# RETRIEVAL
# ─────────────────────────────────────────────
TOP_K = 5

# S3
S3_BUCKET = "abacus-claim-predictor"

# ─────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────
POLICY_DOC_PATH = os.path.join(PROJECT_ROOT, "data", "policy_documents.txt")
FAISS_INDEX_PATH = os.path.join(PROJECT_ROOT, "artifacts", "rag", "faiss.index")
METADATA_PATH = os.path.join(PROJECT_ROOT, "artifacts", "rag", "metadata.pkl")

# ─────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
LOG_FILE = os.path.join(LOG_DIR, "rag_pipeline.log")

os.makedirs(LOG_DIR, exist_ok=True)