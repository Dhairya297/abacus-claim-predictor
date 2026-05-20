import os
from pathlib import Path
import boto3
import json

# ── PROJECT ROOT ──────────────────────────────────────────────
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)

# ── ENVIRONMENT DETECTION ─────────────────────────────────────
IS_DATABRICKS = os.path.exists(
    "/Workspace/Users/dhairyashimpi@gmail.com/Abacus Intern Project"
)
IS_AWS = os.environ.get("DEPLOYMENT_ENV") == "aws"
IS_LOCAL = not IS_DATABRICKS and not IS_AWS

# ── OPENAI ────────────────────────────────────────────────────
def get_secret(secret_name: str) -> dict:
    """Fetch secrets from AWS Secrets Manager — only called on AWS."""
    client = boto3.client("secretsmanager", region_name="us-east-1")
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])

if IS_AWS:
    # Production — fetch from Secrets Manager
    _secrets       = get_secret("abacus/openai")
    OPENAI_API_KEY = _secrets["OPENAI_API_KEY"]
else:
    # Local — fetch from .env file (never committed to git)
    from dotenv import load_dotenv
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY not found. "
            "Create a .env file in project root with: OPENAI_API_KEY=sk-..."
        )

OPENAI_MODEL = "gpt-4o-mini"

# ── EMBEDDING MODEL ───────────────────────────────────────────
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ── CHUNKING ──────────────────────────────────────────────────
CHUNK_SIZE    = 500
CHUNK_OVERLAP = 100

# ── RETRIEVAL ─────────────────────────────────────────────────
TOP_K = 5

# ── PATHS ─────────────────────────────────────────────────────
POLICY_DOC_PATH  = os.path.join(PROJECT_ROOT, "data", "policy_documents.txt")
FAISS_INDEX_PATH = os.path.join(PROJECT_ROOT, "artifacts", "rag", "faiss.index")
METADATA_PATH    = os.path.join(PROJECT_ROOT, "artifacts", "rag", "metadata.pkl")

# ── LOGGING ───────────────────────────────────────────────────
LOG_DIR  = os.path.join(PROJECT_ROOT, "logs")
LOG_FILE = os.path.join(LOG_DIR, "rag_pipeline.log")
os.makedirs(LOG_DIR, exist_ok=True)