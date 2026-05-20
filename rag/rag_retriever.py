from utils.logger import logger
from config.error_codes import ErrorCode

class RAGRetriever:

    def __init__(self,embedding_model,vector_store):
        self.embedding_model = embedding_model
        self.vector_store = vector_store

    def retrieve(self,question,top_k=5):
        try:
            logger.info(f"Retrieving policies for: {question}")

            query_embedding = (
                self.embedding_model
                .generate_embeddings(
                    [question]
                )[0]
            )

            results = (
                self.vector_store
                .search(
                    query_embedding=query_embedding,
                    top_k=top_k
                )
            )
            return results

        except Exception as e:
            logger.exception("Policy retrieval failed.")

            raise RuntimeError(ErrorCode.RAG_PIPELINE_ERROR) from e