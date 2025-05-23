"""
Hyperparameter tuning script for model optimization.
Performs grid search with cross-validation and saves best parameters to config.
"""

from sklearn.model_selection import GridSearchCV
from sklearn.metrics import (
    make_scorer,
    roc_auc_score,
    f1_score,
    precision_score,
    recall_score,
)
import mlflow
import yaml
from datetime import datetime

# from train_model import load_config, get_abs_path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

# import lightgbm as lgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

# from mle_utils.logger import set_log
import os

from mle_datathon.utils import get_abs_path, load_config, set_log

logger = set_log("tune_model")


def tune_models(X_train, y_train, config, cv=5):
    """Perform hyperparameter tuning for all models."""

    param_grids = {
        "RandomForest": {
            "n_estimators": [100, 200, 300],
            "max_depth": [None, 10, 20, 30],
            "min_samples_split": [2, 5, 10],
            "min_samples_leaf": [1, 2, 4],
        },
        "LogisticRegression": {
            "C": [0.001, 0.01, 0.1, 1, 10],
            "penalty": ["l1", "l2"],
            "solver": ["liblinear", "saga"],
        },
        "XGBoost": {
            "learning_rate": [0.01, 0.1],
            "max_depth": [3, 5, 7],
            "n_estimators": [100, 200],
            "subsample": [0.8, 0.9],
            "colsample_bytree": [0.8, 0.9],
        },
        # "LightGBM": {
        #     'learning_rate': [0.01, 0.1],
        #     'max_depth': [3, 5, 7],
        #     'n_estimators': [100, 200],
        #     'subsample': [0.8, 0.9],
        #     'colsample_bytree': [0.8, 0.9]
        # }
    }

    models = {
        "RandomForest": RandomForestClassifier(
            random_state=config["model"]["random_state"]
        ),
        "LogisticRegression": LogisticRegression(
            random_state=config["model"]["random_state"]
        ),
        "XGBoost": xgb.XGBClassifier(random_state=config["model"]["random_state"]),
        # "LightGBM": lgb.LGBMClassifier(random_state=config["model"]["random_state"])
    }

    scoring = {
        "auc": make_scorer(roc_auc_score),
        "f1": make_scorer(f1_score),
        "precision": make_scorer(precision_score),
        "recall": make_scorer(recall_score),
    }

    best_params = {}

    for name, model in models.items():
        with mlflow.start_run(
            run_name=f"tuning_{name}_{datetime.now().strftime('%Y-%m-%d_%H_%M_%S')}"
        ):
            logger.info(f"\nTuning {name}...")

            grid_search = GridSearchCV(
                estimator=model,
                param_grid=param_grids[name],
                cv=cv,
                scoring=scoring,
                refit="auc",
                n_jobs=-1,
                verbose=2,
            )

            logger.debug("Starting grid search...")
            grid_search.fit(X_train, y_train)

            # Log results
            mlflow.log_params(grid_search.best_params_)
            mlflow.log_metric("best_cv_score", grid_search.best_score_)

            best_params[name] = grid_search.best_params_

            logger.info(f"Best parameters for {name}:")
            logger.info(grid_search.best_params_)
            logger.info(f"Best CV score: {grid_search.best_score_:.4f}")

    return best_params


def update_config_file(config):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_config = f"config_{timestamp}.yaml"

    """Update the config file with the best parameters."""
    with open(save_config, "w") as f:
        yaml.dump(config, f)
    logger.info("Config file updated with best parameters.")


def tune():
    local_path = os.getcwd()

    config = load_config(local_path)
    paths = config["paths"]

    for k in paths:
        paths[k] = get_abs_path(local_path, paths[k])

    # Load and prepare data
    df = pd.read_parquet(paths["dataset_features"])
    features = [
        col
        for col in df.columns
        if col != "target" and pd.api.types.is_numeric_dtype(df[col])
    ]

    X = df[features]
    y = df["target"]

    X_train, _, y_train, _ = train_test_split(
        X,
        y,
        test_size=config["model"]["test_size"],
        random_state=config["model"]["random_state"],
        stratify=y,
    )

    # Preprocess
    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    X_train_imp = imputer.fit_transform(X_train)
    X_train_scaled = scaler.fit_transform(X_train_imp)

    # Tune models
    best_params = tune_models(X_train_scaled, y_train, config)

    # Update config with best parameters
    config["model"]["tuned_params"] = best_params

    update_config_file(config)
