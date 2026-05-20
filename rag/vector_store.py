import faiss
import pickle
import numpy as np
import boto3
import tempfile
import pickle
import io

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
            logger.info("Downloading FAISS index and metadata from S3.")
            s3 = boto3.client("s3", region_name="us-east-1")
            S3_BUCKET = "abacus-claim-predictor"
            
            faiss_obj = s3.get_object(Bucket=S3_BUCKET, Key="artifacts/rag/faiss.index")
            with tempfile.NamedTemporaryFile(suffix=".index", delete=False) as tmp:
                tmp.write(faiss_obj["Body"].read())
                tmp_path = tmp.name

            self.index = faiss.read_index(tmp_path)
            logger.info("FAISS index loaded from S3.")

            meta_obj = s3.get_object(Bucket=S3_BUCKET, Key="artifacts/rag/metadata.pkl")
            self.metadata = pickle.load(io.BytesIO(meta_obj["Body"].read()))
            logger.info("Metadata loaded from S3.")

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