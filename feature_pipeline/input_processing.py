import os
import sys
import pandas as pd
import numpy as np

from datetime import datetime

from config.settings import PROJECT_ROOT
import sys
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# =============================================================================
# IMPORTS
# =============================================================================

from utils.logger import logger
from config.error_codes import ErrorCode

# =============================================================================
# REALTIME FEATURE PIPELINE
# =============================================================================


class RealtimeFeaturePipeline:

    # =========================================================================
    # INIT
    # =========================================================================

    def __init__(

        self,

        diagnosis_df: pd.DataFrame,

        providers_df: pd.DataFrame,

        cost_df: pd.DataFrame,

        historical_claims_df: pd.DataFrame,
    ):

        try:

            logger.info(
                "Initializing realtime feature pipeline."
            )

            # ================================================================
            # COPY INPUT DATAFRAMES
            # ================================================================

            self.diagnosis_df = diagnosis_df.copy()

            self.providers_df = providers_df.copy()

            self.cost_df = cost_df.copy()

            self.historical_claims_df = (
                historical_claims_df.copy()
            )

            # ================================================================
            # STANDARDIZATION
            # ================================================================

            self.diagnosis_df.columns = (
                self.diagnosis_df.columns
                .str.lower()
                .str.strip()
            )

            self.providers_df.columns = (
                self.providers_df.columns
                .str.lower()
                .str.strip()
            )

            self.cost_df.columns = (
                self.cost_df.columns
                .str.lower()
                .str.strip()
            )

            self.historical_claims_df.columns = (
                self.historical_claims_df.columns
                .str.lower()
                .str.strip()
            )

            logger.info(
                "Realtime feature pipeline initialized successfully."
            )

        except Exception as e:

            logger.exception(
                "Realtime feature pipeline initialization failed."
            )

            raise RuntimeError(
                ErrorCode.PIPELINE_INITIALIZATION_ERROR
            ) from e

    # =========================================================================
    # TRANSFORM SINGLE CLAIM
    # =========================================================================

    def transform_single_claim(

        self,

        claim_payload: dict
    ) -> pd.DataFrame:

        try:

            logger.info(
                "Starting realtime feature engineering."
            )

            # ================================================================
            # CREATE CLAIM DATAFRAME
            # ================================================================

            claim_df = pd.DataFrame(
                [claim_payload]
            )

            claim_df.columns = (
                claim_df.columns
                .str.lower()
                .str.strip()
            )

            # ================================================================
            # STANDARDIZATION
            # ================================================================

            claim_df["diagnosis_code"] = (

                claim_df["diagnosis_code"]

                .fillna("UNKNOWN_DIAG")

                .astype(str)

                .str.upper()

                .str.strip()
            )

            claim_df["procedure_code"] = (

                claim_df["procedure_code"]

                .fillna("UNKNOWN_PROC")

                .astype(str)

                .str.upper()

                .str.strip()
            )

            claim_df["provider_id"] = (

                claim_df["provider_id"]

                .fillna("UNKNOWN_PROVIDER")

                .astype(str)

                .str.upper()

                .str.strip()
            )

            claim_df["billed_amount"] = pd.to_numeric(

                claim_df["billed_amount"],

                errors="coerce"
            )

            # ================================================================
            # MISSING FLAGS
            # ================================================================

            claim_df["is_diagnosis_missing"] = np.where(

                claim_df["diagnosis_code"].isin(
                    ["UNKNOWN_DIAG", "", "NULL"]
                ),

                1,

                0
            )

            claim_df["is_procedure_missing"] = np.where(

                claim_df["procedure_code"].isin(
                    ["UNKNOWN_PROC", "", "NULL"]
                ),1,0
            )

            claim_df["is_amount_missing"] = np.where(

                claim_df["billed_amount"].isna(),
                1,0
            )

            claim_df["diag_proc_both_missing"] = np.where(

                (
                    claim_df["is_diagnosis_missing"] == 1
                )
                &
                (
                    claim_df["is_procedure_missing"] == 1
                ),

                1,
                0
            )

            # ================================================================
            # BILLING NULL HANDLING
            # ================================================================

            claim_df["billed_amount"] = (

                claim_df["billed_amount"]

                .fillna(0.0)
            )

            # ================================================================
            # PREPARE DIAGNOSIS TABLE
            # ================================================================

            diagnosis_df = self.diagnosis_df.copy()

            diagnosis_df["diagnosis_code"] = (

                diagnosis_df["diagnosis_code"]

                .astype(str)

                .str.upper()

                .str.strip()
            )

            # ================================================================
            # MERGE DIAGNOSIS
            # ================================================================

            claim_df = claim_df.merge(

                diagnosis_df,

                on="diagnosis_code",

                how="left"
            )

            # ================================================================
            # PREPARE PROVIDERS TABLE
            # ================================================================

            providers_df = self.providers_df.copy()

            providers_df["provider_id"] = (

                providers_df["provider_id"]

                .astype(str)

                .str.upper()

                .str.strip()
            )

            # ================================================================
            # MERGE PROVIDERS
            # ================================================================

            claim_df = claim_df.merge(

                providers_df,

                on="provider_id",

                how="left"
            )

            # ================================================================
            # PREPARE COST TABLE
            # IMPORTANT:
            # REMOVE DUPLICATE PROCEDURE CODES
            # ================================================================

            cost_df = self.cost_df.copy()

            cost_df["procedure_code"] = (

                cost_df["procedure_code"]

                .astype(str)

                .str.upper()

                .str.strip()
            )

            # ================================================================
            # AGGREGATE DUPLICATES
            # ================================================================

            cost_df = (

                cost_df

                .groupby(
                    "procedure_code",
                    as_index=False
                )

                .agg({

                    "average_cost": "mean",

                    "expected_cost": "mean"
                })
            )

            # ================================================================
            # MERGE COST
            # ================================================================

            claim_df = claim_df.merge(

                cost_df,

                on="procedure_code",

                how="left"
            )

            # ================================================================
            # NULL HANDLING
            # ================================================================

            claim_df["severity"] = (

                claim_df["severity"]

                .fillna("UNKNOWN")
            )

            claim_df["category"] = (

                claim_df["category"]

                .fillna("UNKNOWN")
            )

            claim_df["specialty"] = (

                claim_df["specialty"]

                .fillna("UNKNOWN")
            )

            claim_df["location"] = (

                claim_df["location"]

                .fillna("UNKNOWN")
            )

            claim_df["expected_cost"] = (

                claim_df["expected_cost"]

                .fillna(1.0)
            )

            claim_df["average_cost"] = (

                claim_df["average_cost"]

                .fillna(1.0)
            )

            # ================================================================
            # COST FEATURES
            # ================================================================

            claim_df[
                "amount_to_expected_ratio"
            ] = np.where(

                claim_df["expected_cost"] > 0,

                (
                    claim_df["billed_amount"]
                    /
                    claim_df["expected_cost"]
                ),

                0.0
            )

            claim_df[
                "amount_to_average_ratio"
            ] = np.where(

                claim_df["average_cost"] > 0,

                (
                    claim_df["billed_amount"]
                    /
                    claim_df["average_cost"]
                ),

                0.0
            )

            claim_df["high_cost_flag"] = np.where(

                (
                    claim_df[
                        "amount_to_expected_ratio"
                    ] >= 2.5
                )
                |
                (
                    claim_df[
                        "amount_to_average_ratio"
                    ] >= 2.5
                ),

                1,

                0
            )

            # ================================================================
            # HISTORICAL CLAIMS
            # ================================================================

            hist_df = (
                self.historical_claims_df.copy()
            )

            hist_df["provider_id"] = (

                hist_df["provider_id"]

                .astype(str)

                .str.upper()

                .str.strip()
            )

            hist_df["diagnosis_code"] = (

                hist_df["diagnosis_code"]

                .astype(str)

                .str.upper()

                .str.strip()
            )

            # ================================================================
            # PROVIDER FEATURES
            # ================================================================

            provider_counts = (

                hist_df

                .groupby("provider_id")

                .size()

                .to_dict()
            )

            provider_denial_rate = (

                hist_df

                .groupby("provider_id")[
                    "denial_flag"
                ]

                .mean()

                .to_dict()
            )

            global_denial_rate = float(

                hist_df["denial_flag"].mean()
            )

            claim_df[
                "provider_claim_count"
            ] = (

                claim_df["provider_id"]

                .map(provider_counts)

                .fillna(0)
            )

            claim_df[
                "provider_denial_rate"
            ] = (

                claim_df["provider_id"]

                .map(provider_denial_rate)

                .fillna(global_denial_rate)
            )

            claim_df["provider_high_risk"] = np.where(

                (
                    claim_df[
                        "provider_denial_rate"
                    ] >= 0.50
                )
                |
                (
                    claim_df[
                        "provider_claim_count"
                    ] >= 20
                ),

                1,

                0
            )

            # ================================================================
            # DIAGNOSIS FEATURES
            # ================================================================

            severity_map = {

                "HIGH": 3,

                "MEDIUM": 2,

                "LOW": 1
            }

            claim_df["severity_score"] = (

                claim_df["severity"]

                .astype(str)

                .str.upper()

                .map(severity_map)

                .fillna(0)
            )

            diagnosis_counts = (

                hist_df

                .groupby("diagnosis_code")

                .size()

                .to_dict()
            )

            claim_df[
                "diagnosis_claim_count"
            ] = (

                claim_df["diagnosis_code"]

                .map(diagnosis_counts)

                .fillna(0)
            )

            claim_df["rare_diagnosis_flag"] = np.where(

                claim_df[
                    "diagnosis_claim_count"
                ] <= 3,

                1,

                0
            )

            # ================================================================
            # TEMPORAL FEATURES
            # ================================================================

            claim_df["date"] = pd.to_datetime(

                claim_df["date"],

                errors="coerce"
            )

            claim_df["claim_year"] = (
                claim_df["date"].dt.year
            )

            claim_df["claim_month"] = (
                claim_df["date"].dt.month
            )

            claim_df["claim_weekday"] = (
                claim_df["date"].dt.dayofweek + 1
            )

            claim_df["is_weekend_claim"] = np.where(

                claim_df["claim_weekday"].isin(
                    [6, 7]
                ),

                1,

                0
            )

            # ================================================================
            # SPECIALTY ONE HOT
            # ================================================================

            specialty = (

                claim_df["specialty"]

                .astype(str)

                .str.lower()
            )

            claim_df["specialty_cardiology"] = np.where(
                specialty == "cardiology",
                1,
                0
            )

            claim_df["specialty_neurology"] = np.where(
                specialty == "neurology",
                1,
                0
            )

            claim_df["specialty_orthopedic"] = np.where(
                specialty == "orthopedic",
                1,
                0
            )

            claim_df["specialty_general"] = np.where(
                specialty == "general",
                1,
                0
            )

            claim_df["specialty_unknown"] = np.where(
                specialty == "unknown",
                1,
                0
            )

            # ================================================================
            # CATEGORY ONE HOT
            # ================================================================

            category = (

                claim_df["category"]

                .astype(str)

                .str.lower()
            )

            claim_df["category_heart"] = np.where(
                category == "heart",
                1,
                0
            )

            claim_df["category_bone"] = np.where(
                category == "bone",
                1,
                0
            )

            claim_df["category_fever"] = np.where(
                category == "fever",
                1,
                0
            )

            claim_df["category_skin"] = np.where(
                category == "skin",
                1,
                0
            )

            claim_df["category_diabetes"] = np.where(
                category == "diabetes",
                1,
                0
            )

            claim_df["category_cold"] = np.where(
                category == "cold",
                1,
                0
            )

            # ================================================================
            # LOCATION ENCODING
            # BASED ON YOUR ACTUAL DATA
            # ================================================================

            location = (
                claim_df["location"]
                .astype(str)
                .str.lower()
                .str.strip()
            )

            location_mapping = {
                "mumbai": 5,
                "delhi": 4,
                "bangalore": 3,
                "chennai": 2,
                "hyderabad": 1
            }

            claim_df["location_encoded"] = (location.map(location_mapping).fillna(0))

            # ================================================================
            # FINAL FEATURE ORDER
            # ================================================================

            final_columns = [
                "billed_amount",
                "amount_to_expected_ratio",
                "amount_to_average_ratio",
                "high_cost_flag",
                "provider_claim_count",
                "provider_denial_rate",
                "provider_high_risk",
                "severity_score",
                "diagnosis_claim_count",
                "rare_diagnosis_flag",
                "is_diagnosis_missing",
                "is_procedure_missing",
                "is_amount_missing",
                "diag_proc_both_missing",
                "claim_year",
                "claim_month",
                "claim_weekday",
                "is_weekend_claim",
                "specialty_cardiology",
                "specialty_neurology",
                "specialty_orthopedic",
                "specialty_general",
                "specialty_unknown",
                "category_heart",
                "category_bone",
                "category_fever",
                "category_skin",
                "category_diabetes",
                "category_cold",
                "location_encoded",
            ]

            # ================================================================
            # FINAL FEATURE DATAFRAME
            # ================================================================

            feature_df = claim_df[
                final_columns
            ].copy()

            # ================================================================
            # FINAL NULL HANDLING
            # ================================================================

            feature_df = feature_df.fillna(0)

            # ================================================================
            # TYPE CASTING
            # ================================================================

            int_columns = [
                "high_cost_flag",
                "provider_high_risk",
                "severity_score",
                "rare_diagnosis_flag",
                "is_diagnosis_missing",
                "is_procedure_missing",
                "is_amount_missing",
                "diag_proc_both_missing",
                "claim_year",
                "claim_month",
                "claim_weekday",
                "is_weekend_claim",
                "specialty_cardiology",
                "specialty_neurology",
                "specialty_orthopedic",
                "specialty_general",
                "specialty_unknown",
                "category_heart",
                "category_bone",
                "category_fever",
                "category_skin",
                "category_diabetes",
                "category_cold",
                "location_encoded"
            ]

            for col_name in int_columns:

                feature_df[col_name] = (
                    feature_df[col_name]
                    .astype(int)
                )

            logger.info(
                "Realtime feature engineering completed successfully."
            )

            return feature_df

        except Exception as e:

            logger.exception(
                "Realtime feature engineering failed."
            )

            raise RuntimeError(
                ErrorCode.FEATURE_ENGINEERING_ERROR
            ) from e