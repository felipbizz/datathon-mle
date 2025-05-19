"""
1. Criar a matriz USERxITEM <- (VAGAxCANDIDATO)
    - Índices = ids das vagas
    - Colunas = ids dos candidatos
    - Valores = nulo se não tem interação, 1 se teve interação
2. Processar os dados, criando os recursos necessários para a criação do modelo
"""

import pandas as pd
from config import load_config
import pickle
from typing import Dict, Any
import json
from functools import reduce
from logger_config import configure_logging
from pathlib import Path
from sklearn.model_selection import train_test_split
from time import time
from tqdm import tqdm
from loguru import logger


config = load_config()
paths = config["paths"]

app_root_dir = Path(paths.get("logger_sink"))
configure_logging(sink_root_dir=app_root_dir, log_to_file=True, log_level="DEBUG")


def cria_matriz_vaga_candidato() -> pd.DataFrame:
    with open(paths.get("prospects_json"), "r", encoding="utf-8") as json_f:
        prospects_json = json.load(json_f)

    interacoes: Dict[str, Any] = {}
    f_reduce = lambda old, new: old | {new["codigo"]: 1}

    for id_vaga, infos in prospects_json.items():
        prospects = infos.get("prospects")
        if prospects:
            interacoes[id_vaga] = reduce(f_reduce, prospects, {})

    matriz_vaga_x_candidato = pd.DataFrame.from_dict(data=interacoes, orient="index")
    matriz_vaga_x_candidato.to_parquet(paths.get("matriz_vaga_candidato"))

    return matriz_vaga_x_candidato


def preprocess_data(jobs_candidates_matrix: pd.DataFrame) -> None:
    """Carrega o arquivo Parquet e o pré-processa para o TorchRec"""

    logger.debug(
        f"Shape do DataFrame Vagas x Candidatos: {jobs_candidates_matrix.shape}"
    )

    # Converte IDs de vagas (índice) e IDs de candidatos (colunas) para inteiros para uso em embeddings
    job_id_mapping = {
        job_id: idx for idx, job_id in enumerate(jobs_candidates_matrix.index)
    }
    candidate_id_mapping = {
        candidate_id: idx
        for idx, candidate_id in enumerate(jobs_candidates_matrix.columns)
    }
    logger.debug(f"Mapeamento de IDs de vagas criado com {len(job_id_mapping)} vagas.")
    logger.debug(
        f"Mapeamento de IDs de candidatos criado com {len(candidate_id_mapping)} candidatos."
    )

    # Cria mapeamentos reversos para converter de volta aos IDs originais
    job_idx_to_id = {idx: job_id for job_id, idx in job_id_mapping.items()}
    candidate_idx_to_id = {
        idx: candidate_id for candidate_id, idx in candidate_id_mapping.items()
    }

    # Cria um dataset de tuplas (job_id, candidate_id, interviewed)
    dataset = []
    logger.debug("Iniciando criação do dataset a partir do DataFrame.")
    # Adicionado tqdm para criação do dataset
    for job_id in tqdm(
        jobs_candidates_matrix.index, desc="Processando interações de vagas"
    ):
        for candidate_id in jobs_candidates_matrix.columns:
            value = jobs_candidates_matrix.loc[job_id, candidate_id]
            # Inclui apenas entradas onde houve entrevista (valor = 1)
            if pd.notna(value) and value == 1:
                dataset.append(
                    {
                        "job_idx": job_id_mapping[job_id],
                        "candidate_idx": candidate_id_mapping[candidate_id],
                        "job_id": job_id,
                        "candidate_id": candidate_id,
                        "interviewed": 1.0,
                    }
                )
    logger.info(f"Dataset criado com {len(dataset)} interações.")
    df = pd.DataFrame(dataset)

    # Divide em conjuntos de treino e teste
    logger.debug("Dividindo os dados em conjuntos de treino e teste.")
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

    print(
        f"Dados carregados: {len(df)} interações, {len(job_id_mapping)} vagas, {len(candidate_id_mapping)} candidatos"
    )
    print(
        f"Conjunto de treino: {len(train_df)} amostras, Conjunto de teste: {len(test_df)} amostras"
    )
    logger.info(
        f"Carregamento e pré-processamento finalizados. Tamanho do treino: {len(train_df)}, Tamanho do teste: {len(test_df)}"
    )

    # ----------- Salvar arquivos pickle -----------
    output_dir = Path(paths.get("torchrec_resources"))
    output_dir.mkdir(parents=True, exist_ok=True)

    save_objects = {
        "train_df.pkl": train_df,
        "test_df.pkl": test_df,
        "job_id_mapping.pkl": job_id_mapping,
        "candidate_id_mapping.pkl": candidate_id_mapping,
        "job_idx_to_id.pkl": job_idx_to_id,
        "candidate_idx_to_id.pkl": candidate_idx_to_id,
    }

    for filename, obj in save_objects.items():
        file_path = output_dir / filename
        with open(file_path, "wb") as f:
            pickle.dump(obj, f)
        logger.info(f"{filename} salvo em {file_path}")
    # ----------------------------------------------

    return None


def main() -> None:

    logger.info("INÍCIO CÓDIGO")
    t0 = time()

    path_matriz_vaga_x_candidato = Path(paths.get("matriz_vaga_candidato"))
    if path_matriz_vaga_x_candidato.exists():
        logger.info("Carregando a matriz de interação entre vagas e candidatos.")
        matriz_vaga_x_candidato = pd.read_parquet(path_matriz_vaga_x_candidato)
    else:
        logger.info("Criando a matriz de interação entre vagas e candidatos.")
        matriz_vaga_x_candidato = cria_matriz_vaga_candidato()

    logger.info("Matriz de interação entre vagas e candidatos está pronta.")

    logger.info("Processando a matriz de interação entre vagas e candidatos.")
    preprocess_data(matriz_vaga_x_candidato)

    logger.info(f"FIM CÓDIGO (t = {time() - t0:.4f} s)")

    return None


if __name__ == "__main__":
    main()
