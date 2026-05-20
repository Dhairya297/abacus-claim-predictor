import mlflow
import mlflow.xgboost

import shap
import pandas as pd

from xgboost import XGBClassifier

from sklearn.model_selection import (
    train_test_split,
    RandomizedSearchCV,
    StratifiedKFold
)

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)

from sklearn.inspection import (
    permutation_importance
)

from utils.logger import logger

from config.error_codes import (
    ErrorCode
)


class MLPipeline:

    def __init__(
        self,
        df,
        feature_columns,
        target_column,
        random_state
    ):

        self.df = df

        self.feature_columns = (
            feature_columns
        )

        self.target_column = (
            target_column
        )

        self.random_state = (
            random_state
        )

    def run_pipeline(self,threshold):
        try:
            logger.info("Preparing data.")
            X = self.df[ self.feature_columns].copy()
            y = self.df[self.target_column].copy()

            for col in X.columns:
                dtype_str = str(X[col].dtype)

                if dtype_str in (
                    "Int8","Int16","Int32","Int64",
                    "UInt8","UInt16","UInt32","UInt64",
                    "boolean","bool"
                ):

                    X[col] = X[col].astype("float64")

            y = y.astype(
                "int32"
            )

            logger.info("Train test split.")

            X_train, X_test, y_train, y_test = (
                train_test_split(
                    X, y,
                    test_size=0.30,
                    random_state=(self.random_state),
                    stratify=y,
                )
            )

            # LEAKAGE FIX
            train_meta = self.df.loc[X_train.index,["provider_id"]].copy()

            train_meta["denial_flag"] = y_train.values

            train_rate_map = (
                train_meta
                .groupby(
                    "provider_id"
                )[
                    "denial_flag"
                ].mean().to_dict()
            )

            train_mean_rate = float(
                y_train.mean()
            )

            prov_train = self.df.loc[
                X_train.index,
                "provider_id"
            ]

            prov_test = self.df.loc[
                X_test.index,
                "provider_id"
            ]

            X_train[
                "provider_denial_rate"
            ] = (prov_train.map(train_rate_map).fillna(train_mean_rate).values
            )

            X_test["provider_denial_rate"] = (prov_test.map(train_rate_map).fillna(train_mean_rate).values)

            logger.info("Leakage fix applied.")
            
            # CLASS IMBALANCE
            n_pos = int(y_train.sum())

            n_neg = int(len(y_train) - n_pos)

            scale_pos_weight = round(n_neg / n_pos,4)
            
            # MODEL
            base_model = XGBClassifier(

                objective="binary:logistic",
                eval_metric="auc",
                tree_method="hist",
                random_state=(
                    self.random_state
                ),
                scale_pos_weight=(
                    scale_pos_weight
                ),
                verbosity=0,
                n_jobs=1,
            )

            param_grid = {

                "n_estimators": [
                    200,
                    300,
                    400,
                    500
                ],

                "learning_rate": [
                    0.01,
                    0.03,
                    0.05,
                    0.07
                ],

                "max_depth": [
                    3,
                    4,
                    5,
                    7
                ],
            }

            cv = StratifiedKFold(
                n_splits=2,
                shuffle=True,
                random_state=(
                    self.random_state
                )
            )

            random_search = RandomizedSearchCV(
                estimator=base_model,
                param_distributions=(
                    param_grid
                ),
                n_iter=5,
                scoring="roc_auc",
                cv=cv,
                verbose=1,
                random_state=(
                    self.random_state
                ),
                n_jobs=1,
                refit=True,
            )

            logger.info(
                "Running hyperparameter tuning."
            )

            random_search.fit(
                X_train,
                y_train
            )

            model = (
                random_search
                .best_estimator_
            )

            y_prob = (
                model
                .predict_proba(
                    X_test
                )[:, 1]
            )

            y_pred = (
                y_prob >= threshold
            ).astype(int)

            accuracy = accuracy_score(
                y_test,
                y_pred
            )

            precision = precision_score(
                y_test,
                y_pred
            )

            recall = recall_score(
                y_test,
                y_pred
            )

            f1 = f1_score(
                y_test,
                y_pred
            )

            roc_auc = roc_auc_score(
                y_test,
                y_prob
            )

            feature_importance = (
                pd.DataFrame({
                    "feature": self.feature_columns,
                    "importance":model.feature_importances_
                }).sort_values(
                    by="importance",
                    ascending=False
                )
            )
            explainer = (shap.TreeExplainer(model))
            
            sample_data = X_test.sample(
                min(
                    1000,
                    len(X_test)
                ),
                random_state=42
            )

            shap_values = (explainer.shap_values(sample_data))

            shap_importance = pd.DataFrame({
                "feature":
                    self.feature_columns,
                "importance":
                    abs(
                        shap_values
                    ).mean(axis=0)
            })

            return {
                "model": model,
                "explainer": explainer,
                "X_test": X_test,
                "y_test": y_test,
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "roc_auc":roc_auc,
                "feature_importance":feature_importance,
                "shap_importance": shap_importance,
                "best_parameters": random_search.best_params_
            }

        except Exception as e:
            logger.exception(
                "ML pipeline failed."
            )
            raise RuntimeError(
                ErrorCode
                .MODEL_TRAINING_ERROR
            ) from e