import pandas as pd
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
import pickle

input_path = "../Datathon Decision/3_silver/dataset_features.parquet"
df = pd.read_parquet(input_path)

if "target" in df.columns:
    y = df["target"]
else:
    raise ValueError(
        "Coluna target não encontrada no dataset de features. Execute a etapa de definição do target."
    )

# Estamos pegando todas as features numéricas por enquanto, vamos melhorar isso depois removendo as de menor relevância (exceto target)
features = [
    col
    for col in df.columns
    if col != "target" and pd.api.types.is_numeric_dtype(df[col])
]
X = df[features]

print(f"Features usadas no treino: {features}")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

imputer = SimpleImputer(strategy="median")
scaler = StandardScaler()
X_train_imp = imputer.fit_transform(X_train)
X_test_imp = imputer.transform(X_test)
X_train_scaled = scaler.fit_transform(X_train_imp)
X_test_scaled = scaler.transform(X_test_imp)

models = {
    "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
    "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
}
results = {}
for name, model in models.items():
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    y_proba = (
        model.predict_proba(X_test_scaled)[:, 1]
        if hasattr(model, "predict_proba")
        else y_pred
    )
    auc = roc_auc_score(y_test, y_proba)
    f1 = f1_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    results[name] = {"auc": auc, "f1": f1, "precision": prec, "recall": rec}
    print(f"\nModelo: {name}")
    print(f"AUC: {auc:.3f} | F1: {f1:.3f} | Precision: {prec:.3f} | Recall: {rec:.3f}")
    print(classification_report(y_test, y_pred))

best_model_name = max(results, key=lambda k: results[k]["auc"])
best_model = models[best_model_name]
with open("../Datathon Decision/3_silver/modelo_treinado.pkl", "wb") as f:
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
print("Arquivo: ../Datathon Decision/3_silver/modelo_treinado.pkl")


# Verificando importância das features. Vamos utilizar isso para filtrar as features posteriormente
importances = models["RandomForest"].feature_importances_
feature_importance = pd.Series(importances, index=features).sort_values(ascending=False)
print("\nImportância das features (RandomForest):")
print(feature_importance.head(20))
feature_importance.to_csv("../Datathon Decision/3_silver/feature_importance_rf.csv")

coefs = models["LogisticRegression"].coef_[0]
coef_importance = pd.Series(coefs, index=features).sort_values(key=abs, ascending=False)
print("\nCoeficientes das features (LogisticRegression):")
print(coef_importance.head(20))
coef_importance.to_csv("../Datathon Decision/3_silver/feature_importance_lr.csv")
