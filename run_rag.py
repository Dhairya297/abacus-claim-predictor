import os

# ==========================================
# OPENAI API KEY
# ==========================================

os.environ["OPENAI_API_KEY"] = ""

# ==========================================
# IMPORTS
# ==========================================

from rag_folder.rag_pipeline import (
    RAGPipeline
)

from config.settings import (
    POLICY_DOC_PATH
)

# ==========================================
# INITIALIZE PIPELINE
# ==========================================

pipeline = RAGPipeline()

# ==========================================
# BUILD VECTOR DATABASE
# ==========================================

print("Building RAG pipeline...")

pipeline.build_pipeline(
    POLICY_DOC_PATH
)

print("Pipeline build complete.")

# ==========================================
# LOAD VECTOR DATABASE
# ==========================================

print("Loading vector database...")

pipeline.load_pipeline()

print("Vector database loaded.")

# ==========================================
# QUERY LOOP
# ==========================================

while True:

    question = input(
        "\nEnter Question "
        "(or type exit): "
    )

    if question.lower() == "exit":

        print("Exiting RAG system.")

        break

    response = pipeline.ask(
        question
    )

    print("\n===================")
    print("RAG RESPONSE")
    print("===================\n")

    print(response)