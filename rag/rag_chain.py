import numpy as np

from openai import OpenAI

from utils.logger import logger

from config.settings import (

    OPENAI_API_KEY,

    OPENAI_MODEL,

    TOP_K
)

from config.error_codes import ErrorCode


class RAGChain:

    def __init__(

        self,

        embedding_model,

        index,

        metadata
    ):

        self.embedding_model = (
            embedding_model
        )

        self.index = index

        self.metadata = metadata

        self.client = OpenAI(
            api_key=OPENAI_API_KEY
        )

    def query(
        self,
        question
    ):

        try:

            logger.info(
                f"Query received: {question}"
            )

            query_embedding = (

                self.embedding_model
                .generate_embeddings(
                    [question]
                )[0]
            )

            distances, indices = (
                self.index.search(

                    np.array(
                        [query_embedding],
                        dtype=np.float32
                    ),

                    TOP_K
                )
            )

            retrieved_chunks = [

                self.metadata[i][
                    "chunk_text"
                ]

                for i in indices[0]
            ]

            context = "\n\n".join(
                retrieved_chunks
            )

            prompt = f"""
You are a healthcare claim adjudication assistant.

Use ONLY the provided context.

If answer is unavailable in context,
say:
"Insufficient policy information."

Context:
{context}

Question:
{question}

Provide:
1. Decision reasoning
2. Policy explanation
3. Supporting evidence
4. Final recommendation
"""

            response = (

                self.client.chat.completions.create(

                    model=OPENAI_MODEL,

                    messages=[

                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],

                    temperature=0.2
                )
            )

            final_response = (
                response
                .choices[0]
                .message.content
            )

            logger.info(
                "LLM response generated."
            )

            return final_response

        except Exception as e:

            logger.exception(
                "RAG query failed."
            )

            raise RuntimeError(
                ErrorCode.PIPELINE_ERROR
            ) from e