import os
import sys

# =============================================================================
# PROJECT ROOT
# =============================================================================

project_root = (
    "/Workspace/Users/dhairyashimpi@gmail.com/"
    "Abacus Intern Project"
)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# =============================================================================
# IMPORTS
# =============================================================================
import joblib
import pandas as pd
import numpy as np
import shap

from pyspark.sql import SparkSession

from sklearn.metrics import (
    precision_recall_curve
)

from ml_training.ml_pipeline import (
    MLPipeline
)

from ml_training.prediction import (
    PredictionEngine
)

from utils.logger import logger

from config.error_codes import (
    ErrorCode
)

# =============================================================================
# SPARK SESSION
# =============================================================================

try:

    logger.info(
        "Creating Spark session."
    )

    spark = (
        SparkSession.builder
        .appName("ClaimDenialMLPipeline")
        .getOrCreate()
    )

    logger.info(
        "Spark session created successfully."
    )

except Exception as e:

    logger.exception(
        "Spark session creation failed."
    )

    raise RuntimeError(
        "SPARK_SESSION_ERROR"
    ) from e

# =============================================================================
# CONFIGURATION
# =============================================================================

GOLD_TABLE_NAME = (
    "workspace.default.gold_ml_encoded"
)

RANDOM_STATE = 42

TARGET_COLUMN = (
    "denial_flag"
)

# =============================================================================
# FEATURES
# =============================================================================

ML_FEATURE_COLUMNS = [

    # ==========================================================
    # COST FEATURES
    # ==========================================================

    "billed_amount",

    "amount_to_expected_ratio",

    "amount_to_average_ratio",

    "high_cost_flag",

    # ==========================================================
    # PROVIDER FEATURES
    # ==========================================================

    "provider_claim_count",

    "provider_denial_rate",

    "provider_high_risk",

    # ==========================================================
    # DIAGNOSIS FEATURES
    # ==========================================================

    "severity_score",

    "diagnosis_claim_count",

    "rare_diagnosis_flag",

    # ==========================================================
    # MISSING VALUE FLAGS
    # ==========================================================

    "is_diagnosis_missing",

    "is_procedure_missing",

    "is_amount_missing",

    "diag_proc_both_missing",

    # ==========================================================
    # TEMPORAL FEATURES
    # ==========================================================

    "claim_year",

    "claim_month",

    "claim_weekday",

    "is_weekend_claim",

    # ==========================================================
    # SPECIALTY FEATURES
    # ==========================================================

    "specialty_cardiology",

    "specialty_neurology",

    "specialty_orthopedic",

    "specialty_general",

    "specialty_unknown",

    # ==========================================================
    # DIAGNOSIS CATEGORY FEATURES
    # ==========================================================

    "category_heart",

    "category_bone",

    "category_fever",

    "category_skin",

    "category_diabetes",

    "category_cold",

    # ==========================================================
    # LOCATION FEATURE
    # ==========================================================

    "location_encoded",
]

# =============================================================================
# LOAD DATA
# =============================================================================

try:

    logger.info(
        "Loading dataset from Unity Catalog."
    )

    spark_df = spark.table(
        GOLD_TABLE_NAME
    )

    required_columns = (

        ML_FEATURE_COLUMNS +

        [
            TARGET_COLUMN,
            "provider_id"
        ]
    )

    spark_df = spark_df.select(
        required_columns
    )

    spark_df = spark_df.limit(
        10000
    )

    logger.info(
        "Converting Spark DataFrame to pandas."
    )

    df = spark_df.toPandas()

    logger.info(
        f"Dataset loaded successfully. "
        f"Shape: {df.shape}"
    )

except Exception as e:

    logger.exception(
        "Dataset loading failed."
    )

    raise RuntimeError(
        ErrorCode.DATA_LOADING_ERROR
    ) from e

# =============================================================================
# VALIDATE FEATURES
# =============================================================================

try:

    logger.info(
        "Validating features."
    )

    missing = [

        c

        for c in ML_FEATURE_COLUMNS

        if c not in df.columns
    ]

    if missing:

        raise ValueError(

            f"Missing columns: "
            f"{missing}"
        )

    logger.info(
        "All required columns found."
    )

except Exception as e:

    logger.exception(
        "Feature validation failed."
    )

    raise RuntimeError(
        ErrorCode.FEATURE_SELECTION_ERROR
    ) from e

# =============================================================================
# INITIALIZE PIPELINE
# =============================================================================

try:

    logger.info(
        "Initializing ML pipeline."
    )

    pipeline = MLPipeline(

        df=df,

        feature_columns=(
            ML_FEATURE_COLUMNS
        ),

        target_column=(
            TARGET_COLUMN
        ),

        random_state=(
            RANDOM_STATE
        )
    )

    logger.info(
        "Pipeline initialized."
    )

except Exception as e:

    logger.exception(
        "Pipeline initialization failed."
    )

    raise RuntimeError(
        ErrorCode.PIPELINE_INITIALIZATION_ERROR
    ) from e

# =============================================================================
# RUN PIPELINE
# =============================================================================

try:

    logger.info(
        "Running ML pipeline."
    )

    # Initial threshold only for pipeline execution
    # Final threshold will be learned dynamically

    results = pipeline.run_pipeline(
        threshold=0.50
    )

    logger.info(
        "ML pipeline completed."
    )

except Exception as e:

    logger.exception(
        "Pipeline execution failed."
    )

    raise RuntimeError(
        ErrorCode.MODEL_TRAINING_ERROR
    ) from e

# =============================================================================
# MODEL PERFORMANCE
# =============================================================================

print("\n==============================")
print("MODEL PERFORMANCE")
print("==============================\n")

print(
    f"Accuracy : "
    f"{round(results['accuracy'], 4)}"
)

print(
    f"Precision : "
    f"{round(results['precision'], 4)}"
)

print(
    f"Recall : "
    f"{round(results['recall'], 4)}"
)

print(
    f"F1 Score : "
    f"{round(results['f1_score'], 4)}"
)

print(
    f"ROC AUC : "
    f"{round(results['roc_auc'], 4)}"
)

# =============================================================================
# BEST PARAMETERS
# =============================================================================

print("\n==============================")
print("BEST PARAMETERS")
print("==============================\n")

print(
    results[
        "best_parameters"
    ]
)

# =============================================================================
# FEATURE IMPORTANCE
# =============================================================================

print("\n==============================")
print("TOP FEATURE IMPORTANCE")
print("==============================\n")

print(

    results[
        "feature_importance"
    ].head(10)
)

# =============================================================================
# SHAP IMPORTANCE
# =============================================================================

print("\n==============================")
print("TOP SHAP FEATURES")
print("==============================\n")

print(

    results[
        "shap_importance"
    ].head(10)
)

# =============================================================================
# DYNAMIC THRESHOLD DISCOVERY
# =============================================================================

try:

    logger.info(
        "Learning optimal denial thresholds."
    )

    print("\n==============================")
    print("GENERATING VALIDATION PROBABILITIES")
    print("==============================\n")

    y_prob_val = (

        results["model"]

        .predict_proba(
            results["X_test"]
        )[:, 1]
    )

    print(
        f"Generated probabilities for "
        f"{len(y_prob_val)} claims."
    )

    # ==============================================================
    # PRECISION RECALL CURVE
    # ==============================================================

    precisions, recalls, thresholds = (

        precision_recall_curve(

            results["y_test"],

            y_prob_val
        )
    )

    # ==============================================================
    # F2 SCORE = (5 * P * R) / (4P + R)
    # ==============================================================

    eps = 1e-12

    f2_scores = (5 *precisions[:-1] * recalls[:-1]) / (4 * precisions[:-1]+recalls[:-1]+eps)

    # ==============================================================
    # BEST THRESHOLD
    # ==============================================================

    best_idx = int(
        np.argmax(f2_scores)
    )

    BASE_DENIAL_THRESHOLD = float(
        thresholds[best_idx]
    )

    # ==============================================================
    # REVIEW MARGIN
    #
    # Adaptive uncertainty band
    #
    # If model probability distribution is wide:
    # larger review margin
    #
    # If model is confident:
    # smaller review margin
    # ==============================================================

    REVIEW_MARGIN = float(

        np.clip(

            np.std(y_prob_val) * 0.25,

            0.05,

            0.10
        )
    )

    APPROVE_THRESHOLD = max(

        0.0,

        BASE_DENIAL_THRESHOLD
        -
        REVIEW_MARGIN
    )

    DENY_THRESHOLD = min(

        1.0,

        BASE_DENIAL_THRESHOLD
        +
        REVIEW_MARGIN
    )

    logger.info(
        "Dynamic threshold learning completed."
    )

except Exception as e:

    logger.exception(
        "Threshold learning failed."
    )

    raise RuntimeError(
        ErrorCode.MODEL_TRAINING_ERROR
    ) from e

# =============================================================================
# DISPLAY THRESHOLDS
# =============================================================================

print("\n==============================")
print("DYNAMIC THRESHOLD ANALYSIS")
print("==============================\n")

print(
    f"Base Denial Threshold : "
    f"{BASE_DENIAL_THRESHOLD:.4f}"
)

print(
    f"Review Margin         : "
    f"{REVIEW_MARGIN:.4f}"
)

print(
    f"Approve Below         : "
    f"{APPROVE_THRESHOLD:.4f}"
)

print(
    f"Review Band           : "
    f"{APPROVE_THRESHOLD:.4f}"
    f" to "
    f"{DENY_THRESHOLD:.4f}"
)

print(
    f"Deny Above            : "
    f"{DENY_THRESHOLD:.4f}"
)

# =============================================================================
# TEST SAMPLE CLAIM
# =============================================================================

try:

    logger.info(
        "Testing sample claim."
    )

    sample_claim = (

        results[
            "X_test"
        ]

        .iloc[[0]]
    )

    # ==============================================================
    # PREDICTION PROBABILITY
    # ==============================================================

    denial_probability = float(

        results["model"]

        .predict_proba(
            sample_claim
        )[0][1]
    )

    # ==============================================================
    # BUSINESS DECISION LOGIC
    # ==============================================================

    if denial_probability < APPROVE_THRESHOLD:

        final_decision = "APPROVED"

    elif denial_probability > DENY_THRESHOLD:

        final_decision = "DENIED"

    else:

        final_decision = "MANUAL_REVIEW"

    # ==============================================================
    # SHAP EXPLANATION
    # ==============================================================

    prediction_result = (

        PredictionEngine
        .predict_claim(

            model=results["model"],

            explainer=results[
                "explainer"
            ],

            claim_input_df=(
                sample_claim
            ),

            threshold=(
                BASE_DENIAL_THRESHOLD
            ),

            shap=shap,

            feature_columns=(
                ML_FEATURE_COLUMNS
            )
        )
    )

    # ==============================================================
    # OUTPUT
    # ==============================================================

    print("\n==============================")
    print("SAMPLE CLAIM RESULT")
    print("==============================\n")

    print(
        f"Denial Probability : "
        f"{round(denial_probability * 100, 2)}%"
    )

    print(
        f"Final Decision     : "
        f"{final_decision}"
    )

    print("\nTop Reasons:\n")

    print(
        prediction_result[
            "top_reasons"
        ]
    )

    logger.info(
        "Sample prediction completed."
    )

except Exception as e:

    logger.exception(
        "Sample prediction failed."
    )

    raise RuntimeError(
        ErrorCode.PREDICTION_ERROR
    ) from e

# =============================================================================
# PIPELINE COMPLETE
# =============================================================================

logger.info(
    "Complete ML workflow finished."
)

print("\n==============================")
print("PIPELINE COMPLETED")
print("==============================\n")

# =============================================================================
# SAVE TRAINED MODEL + THRESHOLDS + EXPLAINER
# =============================================================================

print("\n==============================")
print("SAVING MODEL ARTIFACTS")
print("==============================\n")

model_dir = (
    f"{project_root}/artifacts/models"
)

os.makedirs(
    model_dir,
    exist_ok=True
)

print(
    f"Model directory ready:\n"
    f"{model_dir}"
)

# =============================================================================
# FILE PATHS
# =============================================================================

model_path = (
    f"{model_dir}/claim_denial_xgboost_model.pkl"
)

explainer_path = (
    f"{model_dir}/claim_denial_shap_explainer.pkl"
)

thresholds_path = (
    f"{model_dir}/claim_denial_thresholds.pkl"
)

feature_columns_path = (
    f"{model_dir}/feature_columns.pkl"
)

# =============================================================================
# SAVE MODEL
# =============================================================================

joblib.dump(

    results["model"],

    model_path
)

print(
    "Model saved successfully."
)

# =============================================================================
# SAVE SHAP EXPLAINER
# =============================================================================

joblib.dump(

    results["explainer"],

    explainer_path
)

print(
    "SHAP explainer saved successfully."
)

# =============================================================================
# SAVE THRESHOLD CONFIGURATION
# =============================================================================

threshold_config = {

    "base_denial_threshold":
        BASE_DENIAL_THRESHOLD,

    "review_margin":
        REVIEW_MARGIN,

    "approve_threshold":
        APPROVE_THRESHOLD,

    "deny_threshold":
        DENY_THRESHOLD,
}

joblib.dump(

    threshold_config,

    thresholds_path
)

print(
    "Threshold configuration saved successfully."
)

# =============================================================================
# SAVE FEATURE COLUMNS
# =============================================================================

joblib.dump(

    ML_FEATURE_COLUMNS,

    feature_columns_path
)

print(
    "Feature column list saved successfully."
)

# =============================================================================
# DISPLAY SAVED FILES
# =============================================================================

print("\n==============================")
print("SAVED ARTIFACT FILES")
print("==============================\n")

print(f"Model File        : {model_path}")

print(f"Explainer File    : {explainer_path}")

print(f"Threshold File    : {thresholds_path}")

print(f"Feature List File : {feature_columns_path}")

# =============================================================================
# OPTIONAL: DBFS COPY FOR DOWNLOAD
# =============================================================================

try:

    dbfs_model_dir = (
        "/dbfs/FileStore/abacus_models"
    )

    os.makedirs(
        dbfs_model_dir,
        exist_ok=True
    )

    import shutil

    shutil.copy2(
        model_path,
        f"{dbfs_model_dir}/claim_denial_xgboost_model.pkl"
    )

    shutil.copy2(
        explainer_path,
        f"{dbfs_model_dir}/claim_denial_shap_explainer.pkl"
    )

    shutil.copy2(
        thresholds_path,
        f"{dbfs_model_dir}/claim_denial_thresholds.pkl"
    )

    shutil.copy2(
        feature_columns_path,
        f"{dbfs_model_dir}/feature_columns.pkl"
    )

    print("\n==============================")
    print("DBFS DOWNLOAD LINKS")
    print("==============================\n")

    print(
        "Model:\n"
        "https://dbc-65256cec-1eb4.cloud.databricks.com/"
        "files/abacus_models/"
        "claim_denial_xgboost_model.pkl"
    )

    print()

    print(
        "Explainer:\n"
        "https://dbc-65256cec-1eb4.cloud.databricks.com/"
        "files/abacus_models/"
        "claim_denial_shap_explainer.pkl"
    )

    print()

    print(
        "Thresholds:\n"
        "https://dbc-65256cec-1eb4.cloud.databricks.com/"
        "files/abacus_models/"
        "claim_denial_thresholds.pkl"
    )

    print()

    print(
        "Feature Columns:\n"
        "https://dbc-65256cec-1eb4.cloud.databricks.com/"
        "files/abacus_models/"
        "feature_columns.pkl"
    )

except Exception as e:

    print(
        f"DBFS copy skipped: {e}"
    )

# =============================================================================
# SUCCESS
# =============================================================================

print("\n==============================")
print("MODEL ARTIFACT EXPORT COMPLETE")
print("==============================\n")