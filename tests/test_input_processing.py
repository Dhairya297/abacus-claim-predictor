import os
import sys
import joblib
import shap
import numpy as np
import pandas as pd

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
# IMPORT FEATURE PIPELINE
# =============================================================================

from feature_pipeline.input_processing import (
    RealtimeFeaturePipeline
)

from ml_training.explanation_mapper import (
    FEATURE_EXPLANATION_MAP
)

# =============================================================================
# MODEL + EXPLAINER PATHS
# =============================================================================

MODEL_PATH = (
    f"{project_root}/artifacts/models/"
    "claim_denial_xgboost_model.pkl"
)

EXPLAINER_PATH = (
    f"{project_root}/artifacts/models/"
    "claim_denial_shap_explainer.pkl"
)

THRESHOLD_CONFIG_PATH = (
    f"{project_root}/artifacts/models/"
    "claim_denial_thresholds.pkl"
)

# =============================================================================
# LOAD TRAINED MODEL
# =============================================================================

print("\n===================================================")
print("LOADING TRAINED MODEL")
print("===================================================\n")

model = joblib.load(
    MODEL_PATH
)

print("Model loaded successfully.")

# =============================================================================
# LOAD SHAP EXPLAINER
# =============================================================================

print("\n===================================================")
print("LOADING SHAP EXPLAINER")
print("===================================================\n")

explainer = joblib.load(
    EXPLAINER_PATH
)

print("SHAP explainer loaded successfully.")

# =============================================================================
# LOAD THRESHOLD CONFIGURATION
# =============================================================================

print("\n===================================================")
print("LOADING THRESHOLD CONFIGURATION")
print("===================================================\n")

threshold_config = joblib.load(
    THRESHOLD_CONFIG_PATH
)

APPROVE_THRESHOLD = threshold_config[
    "approve_threshold"
]

DENY_THRESHOLD = threshold_config[
    "deny_threshold"
]

BASE_DENIAL_THRESHOLD = threshold_config[
    "base_denial_threshold"
]

REVIEW_MARGIN = threshold_config[
    "review_margin"
]

print(
    f"Approve Threshold : "
    f"{APPROVE_THRESHOLD:.4f}"
)

print(
    f"Deny Threshold    : "
    f"{DENY_THRESHOLD:.4f}"
)

print(
    f"Review Margin     : "
    f"{REVIEW_MARGIN:.4f}"
)

# =============================================================================
# LOAD REFERENCE DATASETS
# =============================================================================

print("\n===================================================")
print("LOADING REFERENCE DATASETS")
print("===================================================\n")

diagnosis_df = pd.read_csv(
    f"{project_root}/data/diagnosis.csv"
)

providers_df = pd.read_csv(
    f"{project_root}/data/providers_1000.csv"
)

cost_df = pd.read_csv(
    f"{project_root}/data/cost.csv"
)

historical_claims_df = pd.read_csv(
    f"{project_root}/data/claims_1000.csv"
)

print("Reference datasets loaded successfully.")

# =============================================================================
# INITIALIZE REALTIME FEATURE PIPELINE
# =============================================================================

print("\n===================================================")
print("INITIALIZING REALTIME FEATURE PIPELINE")
print("===================================================\n")

pipeline = RealtimeFeaturePipeline(

    diagnosis_df=diagnosis_df,

    providers_df=providers_df,

    cost_df=cost_df,

    historical_claims_df=historical_claims_df,
)

print("Realtime feature pipeline initialized.")

# =============================================================================
# SAMPLE UI INPUT
# =============================================================================

sample_claim = {

    "claim_id": "CLM1001",

    "provider_id": "PR101",

    "diagnosis_code": "D10",

    "procedure_code": "PROC1",

    "billed_amount": 12000,

    "date": "2026-05-15"
}

# =============================================================================
# DISPLAY RAW INPUT
# =============================================================================

print("\n===================================================")
print("RAW UI INPUT")
print("===================================================\n")

for k, v in sample_claim.items():

    print(f"{k:<20}: {v}")

# =============================================================================
# FEATURE ENGINEERING
# =============================================================================

print("\n===================================================")
print("RUNNING FEATURE ENGINEERING")
print("===================================================\n")

feature_df = pipeline.transform_single_claim(
    sample_claim
)

print("Feature engineering successful.")

# =============================================================================
# DISPLAY FEATURE VECTOR
# =============================================================================

print("\n===================================================")
print("ML READY FEATURE VECTOR")
print("===================================================\n")

pd.set_option(
    "display.max_columns",
    None
)

print(feature_df)

# =============================================================================
# FEATURE VALIDATION
# =============================================================================

print("\n===================================================")
print("FEATURE VALIDATION")
print("===================================================\n")

expected_feature_count = 30

actual_feature_count = len(
    feature_df.columns
)

print(
    f"Expected Features : "
    f"{expected_feature_count}"
)

print(
    f"Actual Features   : "
    f"{actual_feature_count}"
)

if actual_feature_count != expected_feature_count:

    raise ValueError(
        "Feature count mismatch."
    )

print("\nSUCCESS: Feature validation passed.")

# =============================================================================
# MODEL PREDICTION
# =============================================================================

print("\n===================================================")
print("RUNNING MODEL PREDICTION")
print("===================================================\n")

denial_probability = float(

    model.predict_proba(
        feature_df
    )[0][1]
)

print(
    f"Predicted Denial Probability : "
    f"{denial_probability:.4f}"
)

# =============================================================================
# BUSINESS DECISION LOGIC
# =============================================================================

print("\n===================================================")
print("BUSINESS DECISION LOGIC")
print("===================================================\n")

if denial_probability < APPROVE_THRESHOLD:

    final_decision = "APPROVED"

elif denial_probability > DENY_THRESHOLD:

    final_decision = "DENIED"

else:

    final_decision = "MANUAL_REVIEW"

print(
    f"Final Decision : "
    f"{final_decision}"
)

# =============================================================================
# RISK SCORE
# =============================================================================

risk_score = round(
    denial_probability * 100,
    2
)

print(
    f"Risk Score : "
    f"{risk_score}%"
)

# =============================================================================
# SHAP EXPLANATION
# =============================================================================

print("\n===================================================")
print("GENERATING SHAP EXPLANATIONS")
print("===================================================\n")

shap_values = explainer.shap_values(
    feature_df
)

# =============================================================================
# HANDLE BINARY CLASSIFICATION FORMAT
# =============================================================================

if isinstance(shap_values, list):

    shap_values = shap_values[1]

# =============================================================================
# CREATE SHAP DATAFRAME
# =============================================================================

shap_df = pd.DataFrame({

    "feature": feature_df.columns,

    "feature_value": feature_df.iloc[0].values,

    "shap_value": shap_values[0]
})

# =============================================================================
# ABSOLUTE IMPACT
# =============================================================================

shap_df["abs_shap"] = np.abs(
    shap_df["shap_value"]
)

# =============================================================================
# SORT BY IMPORTANCE
# =============================================================================

shap_df = shap_df.sort_values(

    by="abs_shap",

    ascending=False
)

# =============================================================================
# TOP 3 REASONS
# =============================================================================

top_reasons = []

top_features = shap_df.head(3)

for _, row in top_features.iterrows():

    feature_name = row["feature"]

    reason = FEATURE_EXPLANATION_MAP.get(

        feature_name,

        feature_name
    )

    impact = round(
        abs(row["shap_value"]),
        4
    )

    top_reasons.append({

        "feature": feature_name,

        "reason": reason,

        "impact_score": impact
    })

# =============================================================================
# FINAL AI OUTPUT
# =============================================================================

print("\n===================================================")
print("FINAL AI OUTPUT")
print("===================================================\n")

print(
    f"Claim ID            : "
    f"{sample_claim['claim_id']}"
)

print(
    f"Denial Probability  : "
    f"{risk_score}%"
)

print(
    f"Approve Threshold   : "
    f"{round(APPROVE_THRESHOLD * 100, 2)}%"
)

print(
    f"Deny Threshold      : "
    f"{round(DENY_THRESHOLD * 100, 2)}%"
)

print(
    f"Final Decision      : "
    f"{final_decision}"
)

# =============================================================================
# DISPLAY TOP REASONS
# =============================================================================

print("\n===================================================")
print("TOP 3 EXPLANATIONS")
print("===================================================\n")

for idx, item in enumerate(top_reasons):

    print(
        f"{idx+1}. "
        f"{item['reason']}"
    )

    print(
        f"   Feature      : "
        f"{item['feature']}"
    )

    print(
        f"   Impact Score : "
        f"{item['impact_score']}"
    )

    print()

# =============================================================================
# SAVE FEATURE VECTOR
# =============================================================================

output_dir = (
    f"{project_root}/outputs"
)

os.makedirs(
    output_dir,
    exist_ok=True
)

feature_output_file = (
    f"{output_dir}/"
    "sample_feature_vector.csv"
)

feature_df.to_csv(

    feature_output_file,

    index=False
)

# =============================================================================
# SAVE SHAP EXPLANATIONS
# =============================================================================

shap_output_file = (
    f"{output_dir}/"
    "sample_shap_explanations.csv"
)

shap_df.to_csv(

    shap_output_file,

    index=False
)

# =============================================================================
# OUTPUT PATHS
# =============================================================================

print("\n===================================================")
print("OUTPUT FILES SAVED")
print("===================================================\n")

print(
    f"Feature Vector File : "
    f"{feature_output_file}"
)

print(
    f"SHAP Explanation File : "
    f"{shap_output_file}"
)

# =============================================================================
# SUCCESS MESSAGE
# =============================================================================

print("\n===================================================")
print("END TO END TEST SUCCESSFUL")
print("===================================================\n")

print(
    "UI Input -> Feature Engineering -> "
    "ML Model -> Dynamic Threshold Logic -> "
    "SHAP Explainability flow executed successfully."
)