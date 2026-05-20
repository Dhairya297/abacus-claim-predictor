from openai import OpenAI
from config.settings import OPENAI_API_KEY
from utils.logger import logger
from config.error_codes import ErrorCode
from config.settings import EMBEDDING_MODEL
from config.settings import OPENAI_API_KEY
api_key = OPENAI_API_KEY

class EmbeddingGenerator:
    _client = None

    def __init__(self):
        try:
            if EmbeddingGenerator._client is None:
                logger.info("Loading OpenAI embedding client.")

                # Fetch API key from AWS Secrets Manager
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