import faiss
import pickle
import numpy as np

from utils.logger import logger
from config.settings import FAISS_INDEX_PATH,METADATA_PATH
from config.error_codes import ErrorCode


class VectorStore:

    def __init__(self):
        self.index = None
        self.metadata = None

    def create_vector_store(
        self,
        embeddings,
        metadata
    ):

        try:
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)

            self.index.add(np.array(embeddings,dtype=np.float32))

            faiss.write_index(
                self.index,
                FAISS_INDEX_PATH
            )

            with open(
                METADATA_PATH,
                "wb"
            ) as file:
                pickle.dump(
                    metadata,
                    file
                )

            logger.info("Vector store created successfully.")

        except Exception as e:
            logger.exception("Vector store creation failed.")

            raise RuntimeError(ErrorCode.VECTOR_STORE_ERROR) from e

    def load_vector_store(self):

        try:
            self.index = faiss.read_index(
                FAISS_INDEX_PATH
            )
            with open(
                METADATA_PATH,
                "rb"
            ) as file:

                self.metadata = pickle.load(
                    file
                )

            logger.info("Vector store loaded.")

        except Exception as e:
            logger.exception("Vector store loading failed.")
            raise RuntimeError(ErrorCode.VECTOR_STORE_ERROR) from e

    def search(
        self,
        query_embedding,
        top_k=5
    ):

        try:

            distances, indices = (
                self.index.search(
                    np.array(
                        [query_embedding],
                        dtype=np.float32
                    ),
                    top_k
                )
            )

            results = []

            for rank, idx in enumerate(indices[0]):

                chunk = self.metadata[idx]
                results.append({
                    "rank": rank + 1,
                    "distance": float(distances[0][rank]),
                    "chunk_text": chunk["chunk_text"],
                    "section_title": chunk["section_title"],
                    "parent_id": chunk["parent_id"],
                    "child_id": chunk["child_id"]
                })

            return results

        except Exception as e:

            logger.exception("Vector search failed.")

            raise RuntimeError(ErrorCode.VECTOR_STORE_ERROR) from e