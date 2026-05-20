from openai import OpenAI
from utils.logger import logger
from config.error_codes import ErrorCode
from config.settings import EMBEDDING_MODEL
import boto3
import json


class EmbeddingGenerator:
    _client = None

    def __init__(self):
        try:
            if EmbeddingGenerator._client is None:
                logger.info("Loading OpenAI embedding client.")

                # Fetch API key from AWS Secrets Manager
                secret_name = "openai_api_key"  # change if needed
                region_name = "us-east-1"       # change if needed

                session = boto3.session.Session()
                client = session.client(service_name="secretsmanager", region_name=region_name)

                secret_value = client.get_secret_value(SecretId=secret_name)
                secret = json.loads(secret_value["SecretString"])
                api_key = secret["api_key"]

                EmbeddingGenerator._client = OpenAI(api_key=api_key)

                logger.info("OpenAI client initialized.")

            self.client = EmbeddingGenerator._client

        except Exception as e:
            logger.exception("Embedding client loading failed.")
            raise RuntimeError(ErrorCode.EMBEDDING_ERROR) from e

    def generate_embeddings(self, texts):
        try:
            # OpenAI expects list or string
            if isinstance(texts, str):
                texts = [texts]

            response = self.client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=texts
            )

            embeddings = [item.embedding for item in response.data]
            return embeddings

        except Exception as e:
            logger.exception("Embedding generation failed.")
            raise RuntimeError(ErrorCode.EMBEDDING_ERROR) from e