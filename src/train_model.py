"""
Train and evaluate classification models for the datathon pipeline.
Loads all paths and parameters from config.yaml for reproducibility.
"""

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score,
    f1_score,
    precision_score,
    recall_score,
    classification_report,
)
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from config import load_config, get_abs_path
from mlflow.models import infer_signature
from datetime import datetime
import pandas as pd
import mlflow
import mlflow.sklearn
import platform
import psutil
import pickle
import xgboost as xgb
import lightgbm as lgb


def log_system_info():
    mlflow.log_param("system", platform.system())
    mlflow.log_param("release", platform.release())
    mlflow.log_param("version", platform.version())
    mlflow.log_param("machine", platform.machine())
    mlflow.log_param("processor", platform.processor())
    mlflow.log_param("cpu_count", psutil.cpu_count())
    mlflow.log_param("memory", psutil.virtual_memory().total / (1024**3))


def main() -> None:
    config = load_config()
    paths = config["paths"]
    model_cfg = config["model"]
    for k in paths:
        paths[k] = get_abs_path(paths[k])

    df = pd.read_parquet(paths["dataset_features"])
    if "target" in df.columns:
        y = df["target"]
    else:
        raise ValueError(
            "Coluna target não encontrada no dataset de features. Execute a etapa de definição do target."
        )

    features = [
        col
        for col in df.columns
        if col != "target" and pd.api.types.is_numeric_dtype(df[col])
    ]
    X = df[features]
    print(f"Features usadas no treino: {features}")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=model_cfg["test_size"],
        random_state=model_cfg["random_state"],
        stratify=y,
    )

    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    X_train_imp = imputer.fit_transform(X_train)
    X_test_imp = imputer.transform(X_test)
    X_train_scaled = scaler.fit_transform(X_train_imp)
    X_test_scaled = scaler.transform(X_test_imp)

    models = {
        "RandomForest": RandomForestClassifier(
            n_estimators=model_cfg["n_estimators"],
            random_state=model_cfg["random_state"],
        ),
        "LogisticRegression": LogisticRegression(
            max_iter=model_cfg["lr_max_iter"],
            random_state=model_cfg["random_state"]
        ),
        "XGBoost": xgb.XGBClassifier(random_state=model_cfg["random_state"],
                                     learning_rate=model_cfg["learning_rate"],
                                     n_estimators=model_cfg["n_estimators"],
                                     max_depth=model_cfg["max_depth"],
                                     subsample=model_cfg["subsample"],
                                     colsample_bytree=model_cfg["colsample_bytree"]
                                     ),
        "LightGBM": lgb.LGBMClassifier(random_state=model_cfg["random_state"],
                                       learning_rate=model_cfg["learning_rate"],
                                       n_estimators=model_cfg["n_estimators"],
                                       max_depth=model_cfg["max_depth"],
                                       subsample=model_cfg["subsample"],
                                       colsample_bytree=model_cfg["colsample_bytree"]
                                       ),
    }

    results = {}
    for name, model in models.items():
        current_datetime = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
        run_name = f'train_model_{name}_{current_datetime}'
        
        with mlflow.start_run(run_name=run_name) as run:
            log_system_info()
            
            print(f"\nTreinando modelo {name}...")
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            signature = infer_signature(X_test_scaled, y_pred)
            
            mlflow.sklearn.log_model(sk_model=model, artifact_path=name, signature=signature)
            mlflow.log_param("model_type", name)
            mlflow.log_metric("test_size", model_cfg["test_size"])
            mlflow.log_metric("random_state", model_cfg["random_state"])
            
            y_proba = (
                model.predict_proba(X_test_scaled)[:, 1]
                if hasattr(model, "predict_proba")
                else y_pred
            )
            
            auc = roc_auc_score(y_test, y_proba)
            f1 = f1_score(y_test, y_pred)
            prec = precision_score(y_test, y_pred)
            rec = recall_score(y_test, y_pred)
            
            mlflow.log_metric("auc", auc)
            mlflow.log_metric("f1", f1)
            mlflow.log_metric("precision", prec)
            mlflow.log_metric("recall", rec)
            mlflow.log_artifact(paths["dataset_features"])
            
            results[name] = {"auc": auc, "f1": f1, "precision": prec, "recall": rec}
            results[name].update({ "run_id": run.info.run_id })
            print(f"\nRun ID: {run.info.run_id}")
            print(f"\nModelo: {name}")
            print(
                f"AUC: {auc:.3f} | F1: {f1:.3f} | Precision: {prec:.3f} | Recall: {rec:.3f}"
            )
            print(classification_report(y_test, y_pred))

    best_model_name = max(results, key=lambda k: results[k]["auc"])
    best_run_id = results[best_model_name]["run_id"]
    best_model = models[best_model_name]

    result = mlflow.register_model(f"runs:/{best_run_id}/{best_model_name}", f"{best_model_name}")
    print(f"Modelo registrado: {result.name} (AUC={results[best_model_name]['auc']:.3f}, RunID: {best_run_id})")

    with open(paths["modelo_treinado"], "wb") as f:
        pickle.dump(
            {
                "model": best_model,
                "imputer": imputer,
                "scaler": scaler,
                "features": features,
            },
            f,
        )
    print(
        f"\nMelhor modelo salvo: {best_model_name} (AUC={results[best_model_name]['auc']:.3f})"
    )
    print(f"Arquivo: {paths['modelo_treinado']}")

    # Feature importance logging
    with mlflow.start_run(run_id=best_run_id):
        if hasattr(best_model, 'feature_importances_'):
            importances = best_model.feature_importances_
            feature_importance = pd.Series(importances, index=features).sort_values(
                ascending=False
            )
            importance_path = paths.get(f"feature_importance_{best_model_name.lower()}")
            if importance_path:
                feature_importance.to_csv(importance_path)
                mlflow.log_artifact(importance_path)
        elif isinstance(best_model, LogisticRegression):
            coefs = best_model.coef_[0]
            coef_importance = pd.Series(coefs, index=features).sort_values(
                key=abs, ascending=False
            )
            coef_importance.to_csv(paths["feature_importance_lr"])
            mlflow.log_artifact(paths["feature_importance_lr"])
            
        mlflow.log_artifact(paths["modelo_treinado"])


if __name__ == "__main__":
    main()
