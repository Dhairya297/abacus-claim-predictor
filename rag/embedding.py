from sentence_transformers import (SentenceTransformer)
from utils.logger import logger
from config.settings import (EMBEDDING_MODEL)
from config.error_codes import ErrorCode

class EmbeddingGenerator:
    _model = None
    def __init__(self):
        try:
            if EmbeddingGenerator._model is None:
                logger.info("Loading embedding model.")

                EmbeddingGenerator._model = (
                    SentenceTransformer(
                        EMBEDDING_MODEL
                    )
                )

                logger.info("Embedding model loaded.")

            self.model = EmbeddingGenerator._model

        except Exception as e:

            logger.exception("Embedding model loading failed.")

            raise RuntimeError(ErrorCode.EMBEDDING_ERROR) from e

    def generate_embeddings(self,texts):
        try:
            embeddings = self.model.encode(
                texts,
                show_progress_bar=False
            )
            return embeddings
        
        except Exception as e:

            logger.exception("Embedding generation failed.")

            raise RuntimeError(ErrorCode.EMBEDDING_ERROR) from e