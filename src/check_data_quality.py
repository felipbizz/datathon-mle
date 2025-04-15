from src.log_config import logging
import pandas as pd

input_path = "../Datathon Decision/3_silver/dataset_modelagem.parquet"
df = pd.read_parquet(input_path)

dependencias = {
    "tempo_processo_dias": ["data_candidatura", "data_status_final"],
    "match_area_atuacao": ["area_atuacao", "areas_atuacao"],
    "idade": ["data_nascimento"],
    "indicacao": ["fonte_indicacao"],
}
logging.info("--- Checagem de colunas necessárias para features ---")
for feat, cols in dependencias.items():
    for col in cols:
        if col not in df.columns:
            logging.warning(f'[ALERTA] Coluna ausente para feature "{feat}": {col}')

logging.info("\n--- Proporção de missing e dominância de valores ---")
for col in df.columns:
    missing = df[col].isnull().mean()
    if missing > 0.3:
        logging.warning(f'[ALERTA] Coluna "{col}" com {missing:.0%} de missing')
    vc = df[col].value_counts(normalize=True, dropna=True)
    if not vc.empty and vc.iloc[0] > 0.9:
        logging.warning(
            f'[ALERTA] Coluna "{col}" com valor dominante ({vc.index[0]}) em {vc.iloc[0]:.0%}'
        )

total_missing = df.isnull().mean().sort_values(ascending=False)
logging.info("\n--- Top 10 colunas com mais missing ---")
logging.info(total_missing.head(10))

logging.info("\n[INFO] Checagem de qualidade dos dados concluída.")
