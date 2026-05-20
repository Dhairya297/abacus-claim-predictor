class ErrorCode:

    FILE_NOT_FOUND = {
        "code": "E101",
        "message": "Input file not found."
    }

    FILE_READ_ERROR = {
        "code": "E102",
        "message": "File reading failed."
    }

    CHUNKING_ERROR = {
        "code": "E103",
        "message": "Hierarchical chunking failed."
    }

    VECTOR_STORE_ERROR = {
        "code": "E104",
        "message": "Vector store operation failed."
    }

    EMBEDDING_ERROR = {
        "code": "E105",
        "message": "Embedding generation failed."
    }

    RAG_PIPELINE_ERROR = {
        "code": "E106",
        "message": "RAG pipeline failed."
    }

    MODEL_TRAINING_ERROR = {
        "code": "E801",
        "message": "Model training failed."
    }

    MODEL_EVALUATION_ERROR = {
        "code": "E802",
        "message": "Model evaluation failed."
    }

    PREPROCESSING_ERROR = {
        "code": "E803",
        "message": "Data preprocessing failed."
    }

    PREDICTION_ERROR = {
        "code": "E804",
        "message": "Prediction failed."
    }

    MLFLOW_ERROR = {
        "code": "E805",
        "message": "MLflow tracking failed."
    }

    DATA_LOADING_ERROR = {
        "code": "E806",
        "message": "Training data loading failed."
    }

    HYPERPARAMETER_TUNING_ERROR = {
        "code": "E807",
        "message": "Hyperparameter tuning failed."
    }

    SHAP_ERROR = {
        "code": "E808",
        "message": "SHAP explainability generation failed."
    }

    SPARK_SESSION_ERROR = (
        "Spark session creation failed."
    )

    DATA_LOADING_ERROR = (
        "Dataset loading failed."
    )

    FEATURE_SELECTION_ERROR = (
        "Feature validation failed."
    )

    PIPELINE_INITIALIZATION_ERROR = (
        "Pipeline initialization failed."
    )

    MODEL_TRAINING_ERROR = (
        "Model training failed."
    )

    PREDICTION_ERROR = (
        "Prediction failed."
    )