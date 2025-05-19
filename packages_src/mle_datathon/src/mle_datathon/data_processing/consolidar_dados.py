import pandas as pd
from mle_datathon.utils import (
    get_abs_path, 
    load_config, 
    set_log
)
import os

logger = set_log("consolidar_dados")

local_path = os.getcwd()
config = load_config(local_path)

paths = config["paths"]

def load_datasets():
    #PATH_APPLICANTS = get_abs_path(local_path,paths["applicants_silver"])
    PATH_VAGAS = get_abs_path(local_path,paths["vagas_silver"])
    PATH_PROSPECTS = get_abs_path(local_path,paths["prospects_silver"])

    #applicants = pd.read_parquet(PATH_APPLICANTS)
    df_vagas = pd.read_parquet(PATH_VAGAS)
    df_prospects = pd.read_parquet(PATH_PROSPECTS)

    return df_vagas, df_prospects

# Merge dos datasets
# prospects contém cod_vaga
# vagas contém cod_vaga

def consolidar_dados():

    # Carregar os datasets
    df_vagas, df_prospects = load_datasets()

    # Merge com vagas (via cod_vaga)
    df = df_prospects.merge(df_vagas, on="cod_vaga", how="left", suffixes=("", "_vaga"))

    missing = df.isnull().mean().sort_values(ascending=False)
    logger.info("Colunas com maior proporção de valores ausentes:")
    logger.info(missing[missing > 0.3])

    # precisa melhorar o preenchimento de valores ausentes
    colunas_cat = df.select_dtypes(include="object").columns
    for col in colunas_cat:
        df[col] = df[col].fillna("desconhecido")

    # Precisa melhorar a padronização de datas
    df["data_candidatura"] = pd.to_datetime(df["data_candidatura"], errors="coerce")

    output_path = get_abs_path(local_path,paths["dataset_consolidado"])
    df.to_parquet(output_path, index=False)
    logger.info(f"Dataset consolidado salvo em: {output_path}")