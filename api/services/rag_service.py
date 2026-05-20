# rag_service.py
import os
import sys
from pathlib import Path

PROJECT_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from rag.rag_pipeline import RAGPipeline
from utils.logger import logger

class RAGService:

    def __init__(self):
        logger.info("Loading RAG pipeline.")
        self.rag_pipeline = RAGPipeline()
        logger.info("RAG pipeline loaded successfully.")

    def retrieve_policy_context(self, question, top_k=3):
        retrieved_chunks = self.rag_pipeline.retrieve_policies(
            question=question,
            top_k=top_k
        )

        formatted_chunks = []
        for chunk in retrieved_chunks:
            formatted_chunks.append({
                "section_title": chunk.get("section_title", "UNKNOWN"),
                "source_file":   chunk.get("source_file", "UNKNOWN"),
                "policy_text":   chunk.get("chunk_text", "")
            })
        return formatted_chunks