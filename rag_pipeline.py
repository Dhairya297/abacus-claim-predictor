
# =============================================================================
# IMPORTS
# =============================================================================

import os
import re
import json
import faiss
import fitz
import torch
import numpy as np
import pandas as pd

from typing import List, Dict

from openai import OpenAI

from sentence_transformers import CrossEncoder

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

# COMMAND ----------

# =============================================================================
# CONFIGURATION
# =============================================================================

# =============================================================================
# PATHS
# =============================================================================

POLICY_PDF_FOLDER = "/Volumes/abacus_project_data/policy_docs/raw_policy_docs"

VECTOR_DB_FOLDER = (
    "/Volumes/abacus_project_data/"
    "vector_search/faiss_index"
)

# =============================================================================
# MODELS
# =============================================================================

EMBEDDING_MODEL = "text-embedding-3-small"

GPT_MODEL = "gpt-4o-mini"

RERANKER_MODEL = "BAAI/bge-reranker-large"

TOP_K_RETRIEVAL = 15

TOP_K_RERANK = 5

# COMMAND ----------

# =============================================================================
# ERROR CODES
# =============================================================================

ERROR_CODES = {

    "RAG001": "Policy folder missing",

    "RAG002": "PDF parsing failed",

    "RAG003": "Chunking failed",

    "RAG004": "Metadata extraction failed",

    "RAG005": "Embedding generation failed",

    "RAG006": "Vector database creation failed",

    "RAG007": "Vector retrieval failed",

    "RAG008": "Reranking failed",

    "RAG009": "LLM reasoning failed"
}

# COMMAND ----------

# =============================================================================
# LOGGER
# =============================================================================

def log_info(message):

    print(f"[INFO] {message}")


def log_error(code, error):

    print(
        f"[ERROR] {code} | "
        f"{ERROR_CODES.get(code)}"
    )

    print(str(error))

# COMMAND ----------

# =============================================================================
# OPENAI CLIENT
# =============================================================================


embedding_model = OpenAIEmbeddings(
    model=EMBEDDING_MODEL
)

# COMMAND ----------

# =============================================================================
# LOAD POLICY PDF DOCUMENTS
# =============================================================================

def load_policy_documents():

    try:

        if not os.path.exists(POLICY_PDF_FOLDER):

            raise Exception(
                f"Folder not found: {POLICY_PDF_FOLDER}"
            )

        documents = []

        pdf_files = [

            f for f in os.listdir(POLICY_PDF_FOLDER)

            if f.endswith(".pdf")
        ]

        log_info(
            f"PDF files found: {len(pdf_files)}"
        )

        for pdf_file in pdf_files:

            file_path = os.path.join(
                POLICY_PDF_FOLDER,
                pdf_file
            )

            pdf_document = fitz.open(file_path)

            full_text = ""

            for page in pdf_document:

                full_text += page.get_text()

            documents.append({

                "document_name": pdf_file,

                "document_text": full_text
            })

        log_info(
            f"Documents loaded successfully"
        )

        return documents

    except Exception as e:

        log_error("RAG002", e)

        raise

# COMMAND ----------

# =============================================================================
# HIERARCHICAL CHUNKING
# =============================================================================

def hierarchical_chunking(documents):

    try:

        parent_splitter = RecursiveCharacterTextSplitter(

            chunk_size=2500,

            chunk_overlap=300
        )

        child_splitter = RecursiveCharacterTextSplitter(

            chunk_size=500,

            chunk_overlap=100
        )

        all_chunks = []

        for doc in documents:

            parent_chunks = parent_splitter.split_text(

                doc["document_text"]
            )

            for parent_id, parent_chunk in enumerate(parent_chunks):

                child_chunks = child_splitter.split_text(
                    parent_chunk
                )

                for child_id, child_chunk in enumerate(child_chunks):

                    all_chunks.append({

                        "document_name":
                            doc["document_name"],

                        "parent_chunk_id":
                            parent_id,

                        "child_chunk_id":
                            child_id,

                        "parent_text":
                            parent_chunk,

                        "chunk_text":
                            child_chunk
                    })

        chunk_df = pd.DataFrame(all_chunks)

        log_info(
            f"Hierarchical chunks created: {len(chunk_df)}"
        )

        return chunk_df

    except Exception as e:

        log_error("RAG003", e)

        raise

# COMMAND ----------

# =============================================================================
# METADATA EXTRACTION
# =============================================================================

ICD_PATTERN = r"\b[A-TV-Z][0-9][A-Z0-9.]{0,6}\b"

CPT_PATTERN = r"\b\d{5}\b"


def extract_metadata(chunk_df):

    try:

        icd_codes = []

        cpt_codes = []

        for text in chunk_df["chunk_text"]:

            icd_found = re.findall(
                ICD_PATTERN,
                text
            )

            cpt_found = re.findall(
                CPT_PATTERN,
                text
            )

            icd_codes.append(
                list(set(icd_found))
            )

            cpt_codes.append(
                list(set(cpt_found))
            )

        chunk_df["icd_codes"] = icd_codes

        chunk_df["cpt_codes"] = cpt_codes

        log_info(
            "Metadata extraction complete"
        )

        return chunk_df

    except Exception as e:

        log_error("RAG004", e)

        raise

# COMMAND ----------

# =============================================================================
# GENERATE EMBEDDINGS
# =============================================================================

def generate_embeddings(chunk_df):

    try:

        embeddings = embedding_model.embed_documents(

            chunk_df["chunk_text"].tolist()
        )

        chunk_df["embedding"] = embeddings

        log_info(
            "Embeddings generated"
        )

        return chunk_df

    except Exception as e:

        log_error("RAG005", e)

        raise

# COMMAND ----------

# =============================================================================
# CREATE VECTOR DATABASE
# =============================================================================

def create_vector_database(chunk_df):

    try:

        embedding_matrix = np.array(

            chunk_df["embedding"].tolist()

        ).astype("float32")

        dimension = embedding_matrix.shape[1]

        index = faiss.IndexFlatL2(dimension)

        index.add(embedding_matrix)

        faiss.write_index(

            index,

            f"{VECTOR_DB_FOLDER}/policy_index.faiss"
        )

        chunk_df.to_pickle(

            f"{VECTOR_DB_FOLDER}/policy_metadata.pkl"
        )

        log_info(
            "Vector database created"
        )

        return index

    except Exception as e:

        log_error("RAG006", e)

        raise

# COMMAND ----------

# =============================================================================
# BUILD COMPLETE VECTOR DATABASE
# =============================================================================

documents = load_policy_documents()

chunk_df = hierarchical_chunking(documents)

chunk_df = extract_metadata(chunk_df)

chunk_df = generate_embeddings(chunk_df)

vector_index = create_vector_database(chunk_df)

# COMMAND ----------

# =============================================================================
# LOAD VECTOR DATABASE
# =============================================================================

index = faiss.read_index(

    f"{VECTOR_DB_FOLDER}/policy_index.faiss"
)

metadata_df = pd.read_pickle(

    f"{VECTOR_DB_FOLDER}/policy_metadata.pkl"
)

log_info(
    "Vector DB loaded"
)

# COMMAND ----------

# =============================================================================
# LOAD RERANKER MODEL
# =============================================================================

reranker = CrossEncoder(
    RERANKER_MODEL
)

log_info(
    "Reranker loaded"
)

# COMMAND ----------

# =============================================================================
# BUILD CLAIM QUERY
# =============================================================================

def build_claim_query(

    icd_code=None,
    cpt_code=None,
    provider_id=None,
    claim_text=None
):

    query_parts = []

    if icd_code:

        query_parts.append(
            f"ICD code {icd_code}"
        )

    if cpt_code:

        query_parts.append(
            f"CPT procedure {cpt_code}"
        )

    if provider_id:

        query_parts.append(
            f"provider {provider_id}"
        )

    if claim_text:

        query_parts.append(
            claim_text
        )

    query_parts.append(
        "medical necessity coverage denial reimbursement policy"
    )

    return " ".join(query_parts)

# COMMAND ----------

# =============================================================================
# HYBRID RETRIEVAL
# =============================================================================

def retrieve_policy_chunks(

    icd_code=None,
    cpt_code=None,
    provider_id=None,
    claim_text=None
):

    try:

        query = build_claim_query(

            icd_code,
            cpt_code,
            provider_id,
            claim_text
        )

        query_embedding = embedding_model.embed_query(
            query
        )

        query_embedding = np.array(

            [query_embedding]

        ).astype("float32")

        distances, indices = index.search(

            query_embedding,

            TOP_K_RETRIEVAL
        )

        retrieved_df = metadata_df.iloc[
            indices[0]
        ].copy()

        # ============================================================
        # METADATA FILTERING
        # ============================================================

        if icd_code:

            metadata_match = retrieved_df[
                retrieved_df["icd_codes"]
                .apply(lambda x: icd_code in x)
            ]

            if len(metadata_match) > 0:

                retrieved_df = metadata_match

        if cpt_code:

            metadata_match = retrieved_df[
                retrieved_df["cpt_codes"]
                .apply(lambda x: cpt_code in x)
            ]

            if len(metadata_match) > 0:

                retrieved_df = metadata_match

        log_info(
            f"Retrieved chunks: {len(retrieved_df)}"
        )

        return retrieved_df

    except Exception as e:

        log_error("RAG007", e)

        raise

# COMMAND ----------

# =============================================================================
# RERANK POLICY CHUNKS
# =============================================================================

def rerank_results(query, retrieved_df):

    try:

        pairs = [

            [query, text]

            for text in retrieved_df["chunk_text"]
        ]

        scores = reranker.predict(pairs)

        retrieved_df["rerank_score"] = scores

        retrieved_df = retrieved_df.sort_values(

            by="rerank_score",

            ascending=False
        )

        top_results = retrieved_df.head(
            TOP_K_RERANK
        )

        log_info(
            "Reranking complete"
        )

        return top_results

    except Exception as e:

        log_error("RAG008", e)

        raise

# COMMAND ----------

# =============================================================================
# FINAL BUSINESS REASONING
# =============================================================================

def generate_final_reasoning(

    icd_code=None,
    cpt_code=None,
    provider_id=None,
    claim_text=None
):

    try:

        # ============================================================
        # QUERY
        # ============================================================

        query = build_claim_query(

            icd_code,
            cpt_code,
            provider_id,
            claim_text
        )

        # ============================================================
        # RETRIEVE
        # ============================================================

        retrieved_df = retrieve_policy_chunks(

            icd_code,
            cpt_code,
            provider_id,
            claim_text
        )

        # ============================================================
        # RERANK
        # ============================================================

        reranked_df = rerank_results(

            query,
            retrieved_df
        )

        # ============================================================
        # POLICY TEXT
        # ============================================================

        policy_text = "\n\n".join(

            reranked_df["chunk_text"].tolist()
        )

        # ============================================================
        # PROMPT
        # ============================================================

        prompt = f"""
You are a healthcare insurance policy expert.

Claim Information:

ICD Code:
{icd_code}

CPT Code:
{cpt_code}

Provider:
{provider_id}

Claim Notes:
{claim_text}

Retrieved Policies:
{policy_text}

Tasks:
1. Explain whether claim may be approved or denied
2. Explain the relevant policy
3. Explain medical necessity reasoning
4. Explain documentation requirements
5. Explain possible denial reasons
6. Give recommended action

Keep response concise, structured, and business friendly.
"""

        # ============================================================
        # GPT RESPONSE
        # ============================================================

        response = client.chat.completions.create(

            model=GPT_MODEL,

            messages=[

                {
                    "role": "system",

                    "content":
                        "You are an expert healthcare policy analyst."
                },

                {
                    "role": "user",

                    "content": prompt
                }
            ],

            temperature=0.2
        )

        final_output = (

            response
            .choices[0]
            .message
            .content
        )

        return {

            "query": query,

            "retrieved_policies": reranked_df,

            "final_explanation": final_output
        }

    except Exception as e:

        log_error("RAG009", e)

        raise

# COMMAND ----------

# =============================================================================
# TEST HEALTHCARE POLICY RAG
# =============================================================================

result = generate_final_reasoning(

    icd_code="E11.9",

    cpt_code="83036",

    provider_id="PR1023",

    claim_text="""
    Diabetes patient requiring HbA1c testing
    for ongoing monitoring.
    """
)

# COMMAND ----------

# =============================================================================
# FINAL OUTPUT
# =============================================================================

print("\n==============================")
print("FINAL HEALTHCARE POLICY OUTPUT")
print("==============================\n")

print(result["final_explanation"])

# COMMAND ----------

# =============================================================================
# VIEW RETRIEVED POLICIES
# =============================================================================

display(

    result["retrieved_policies"][[

        "document_name",

        "chunk_text",

        "rerank_score"
    ]]
)