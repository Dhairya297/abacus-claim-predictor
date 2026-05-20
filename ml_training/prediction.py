import pandas as pd

from ml_training.explanation_mapper import FEATURE_EXPLANATION_MAP

class PredictionEngine:

    @staticmethod
    def predict_claim(
        model,
        explainer,
        claim_input_df,
        threshold,
        shap,
        feature_columns
    ):

        probability = model.predict_proba(claim_input_df)[0][1]

        risk_score = round(probability * 100,2)

        prediction = (
            "DENIED"
            if probability >= threshold
            else "APPROVED"
        )

        shap_values = explainer.shap_values(
            claim_input_df
        )

        shap_row = shap_values[0]

        shap_importance = pd.DataFrame({

            "feature": feature_columns,

            "shap_value": shap_row,

            "feature_value": (
                claim_input_df.iloc[0]
                .values
            )
        })

        shap_importance["abs_shap"] = shap_importance["shap_value"].abs()

        shap_importance = shap_importance.sort_values(by="abs_shap",ascending=False)
        
        top_reasons = shap_importance.head(3).copy()

        top_reasons["business_reason"] = top_reasons["feature"].map(FEATURE_EXPLANATION_MAP).fillna("Feature impacted denial risk.")

        return {

            "prediction": prediction,

            "risk_score": risk_score,

            "top_reasons": top_reasons[
                [
                    "business_reason",
                    "shap_value",
                    "feature_value"
                ]
            ]
        }