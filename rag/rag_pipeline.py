from rag.data_loader import DataLoader
from rag.chunking import HierarchicalChunker
from rag.embedding import EmbeddingGenerator
from rag.vector_store import VectorStore
from rag.rag_retriever import RAGRetriever
from utils.logger import logger

class RAGPipeline:

    def __init__(self):
        logger.info("Initializing RAG pipeline.")
        self.embedding_model = EmbeddingGenerator()
        self.vector_store = VectorStore()
        self.load_pipeline()        
        
    def build_pipeline(self,file_path):
        try:
            logger.info("Building RAG pipeline.")
            text = DataLoader.load_document(file_path)
            chunks = HierarchicalChunker.chunk_text(text=text,source_file=file_path)
            chunk_texts = [chunk["chunk_text"] for chunk in chunks]

            embeddings = self.embedding_model.generate_embeddings(chunk_texts)

            self.vector_store.create_vector_store(
                embeddings=embeddings,
                metadata=chunks
            )
            logger.info("RAG pipeline build completed.")

        except Exception as e:
            logger.exception("Pipeline build failed.")
            raise e

    def load_pipeline(self):
        try:
            logger.info("Loading RAG pipeline.")
            self.vector_store.load_vector_store()
            self.retriever = (
                RAGRetriever(
                    embedding_model=self.embedding_model,
                    vector_store=self.vector_store
                )
            )

            logger.info("Pipeline loaded successfully.")

        except Exception as e:
            logger.exception("Pipeline loading failed.")
            raise e

    def retrieve_policies(self,question,top_k=3):
        try:
            return self.retriever.retrieve(
                question=question,
                top_k=top_k
            )

        except Exception as e:
            logger.exception("Policy retrieval failed.")
            raise e