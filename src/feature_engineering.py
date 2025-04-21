"""
Feature engineering pipeline for datathon-mle.
Loads all paths and parameters from config.yaml for reproducibility.
"""

import pandas as pd
from datetime import datetime
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from nltk.corpus import stopwords
from log_config import logging
from config import load_config, get_abs_path
from typing import Any, List
from tqdm import tqdm
from sentence_transformers import SentenceTransformer, util
from rapidfuzz import fuzz
import numpy as np

def coluna_valida(df: pd.DataFrame, col: str) -> bool:
    """Check if a column is valid for feature creation."""
    if col not in df.columns:
        return False
    missing = df[col].isnull().mean()
    if missing > 0.5:
        logging.info(
            f'[SKIP] Coluna "{col}" com {missing:.0%} missing, feature não criada.'
        )
        return False
    vc = df[col].value_counts(normalize=True, dropna=True)
    if not vc.empty and vc.iloc[0] > 0.9:
        logging.info(
            f'[SKIP] Coluna "{col}" com valor dominante ({vc.index[0]}) em {vc.iloc[0]:.0%}, feature não criada.'
        )
        return False
    return True


def tamanho_texto(texto: Any) -> int:
    if pd.isnull(texto):
        return 0
    return len(str(texto))


def n_palavras(texto: Any) -> int:
    if pd.isnull(texto):
        return 0
    return len(str(texto).split())


def conta_palavras_chave(texto: Any, palavras) -> int:
    if pd.isnull(texto):
        return 0
    texto = str(texto).lower()
    return sum(1 for p in palavras if p in texto)


def conta_cursos(texto: Any) -> int:
    if pd.isnull(texto):
        return 0
    return len([c for c in re.split(r"[;,\n]", str(texto)) if c.strip()])

class TextFeatureGenerator:
    def __init__(self):
        logging.info("[Init] Carregando modelo de embeddings...")
        self.embedding_model = SentenceTransformer(
            "paraphrase-multilingual-MiniLM-L12-v2"
        )

    def tamanho_texto(self, texto: Any) -> int:
        if pd.isnull(texto):
            return 0
        return len(str(texto))

    def n_palavras(self, texto: Any) -> int:
        if pd.isnull(texto):
            return 0
        return len(str(texto).split())

    def gerar_embeddings_agregados(self, textos: List[str], batch_size: int = 128) -> pd.DataFrame:
        logging.info(f"[Embeddings] Iniciando geração para {len(textos)} textos...")
        
        embeddings = self.embedding_model.encode(
            textos,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
        logging.info("[Embeddings] Geração finalizada. Criando features agregadas...")
        df_emb = pd.DataFrame({
            "emb_mean": embeddings.mean(axis=1),
            "emb_std": embeddings.std(axis=1),
            "emb_min": embeddings.min(axis=1),
            "emb_max": embeddings.max(axis=1),
        })
        
        return df_emb

    def transform(self, df: pd.DataFrame, campos_texto: List[str]) -> pd.DataFrame:
        for campo in campos_texto:
            if campo in df.columns:
                logging.info(f"[{campo}] Criando features de tamanho e palavras...")
                df[f"{campo}_nchar"] = df[campo].apply(self.tamanho_texto)
                df[f"{campo}_nwords"] = df[campo].apply(self.n_palavras)

                logging.info(f"[{campo}] Criando embeddings agregados...")
                textos = df[campo].fillna("").astype(str).tolist()
                df_emb = self.gerar_embeddings_agregados(textos)
                df_emb.columns = [f"{campo}_{col}" for col in df_emb.columns]

                df = pd.concat([df, df_emb], axis=1)
                logging.info(f"[{campo}] Features de embeddings agregados adicionadas.")

        return df

    def gerar_embeddings(self, textos: pd.Series):
        textos = textos.fillna("").astype(str).tolist()
        return self.embedding_model.encode(textos, convert_to_tensor=True, normalize_embeddings=True)

    def similaridade_string(self, t1, t2):
        if pd.isnull(t1) or pd.isnull(t2):
            return 0
        return fuzz.token_sort_ratio(str(t1), str(t2)) / 100


    def adicionar_similaridade_titulo_vaga(self, df: pd.DataFrame, col1="titulo", col2="titulo_vaga") -> pd.DataFrame:
        if col1 in df.columns and col2 in df.columns:
            tqdm.pandas(desc="[String Similarity]")
            df["titulo_sim_ratio"] = df.progress_apply(lambda row: self.similaridade_string(row[col1], row[col2]), axis=1)

            # Similaridade semântica com embeddings
            tqdm.write("[Embeddings] Gerando embeddings dos títulos...")
            emb1 = self.gerar_embeddings(df[col1].fillna("").astype(str))
            emb2 = self.gerar_embeddings(df[col2].fillna("").astype(str))

            tqdm.write("[Embeddings] Calculando similaridade de cosseno...")
            similarities = util.cos_sim(emb1, emb2).diagonal().cpu().numpy()
            df["sim_titulo_vs_vaga"] = similarities

        return df


def main() -> None:
    config = load_config()
    paths = config["paths"]
    for k in paths:
        paths[k] = get_abs_path(paths[k])
    stop_words = set(stopwords.words("portuguese"))

    df = pd.read_parquet(paths["dataset_modelagem"])

    # 1. Nível acadêmico do candidato (one-hot encoding)
    if coluna_valida(df, "nivel_academico"):
        df = pd.get_dummies(
            df, columns=["nivel_academico"], prefix="nivel_acad", dummy_na=True
        )
        logging.info("[OK] One-hot de nivel_academico criado.")
    else:
        logging.info("[SKIP] One-hot de nivel_academico não criado.")

    # 2. Tipo de contratação da vaga (one-hot encoding)
    if coluna_valida(df, "tipo_contratacao"):
        df = pd.get_dummies(
            df, columns=["tipo_contratacao"], prefix="tipo_contr", dummy_na=True
        )
        logging.info("[OK] One-hot de tipo_contratacao criado.")
    else:
        logging.info("[SKIP] One-hot de tipo_contratacao não criado.")  

    campos_texto = [
        "principais_atividades",
        "competencia_tecnicas_e_comportamentais",
        "demais_observacoes",
        "comentario",
    ]

    feature_generator = TextFeatureGenerator()
    df = feature_generator.transform(df, campos_texto)

    df = feature_generator.adicionar_similaridade_titulo_vaga(df)
    
    df = df.drop(columns=['titulo', 'comentario', 'titulo_vaga', 'prazo_contratacao','prioridade_vaga', 'nivel profissional', 'nivel_ingles',
                            'nivel_espanhol', 'areas_atuacao', 'principais_atividades','competencia_tecnicas_e_comportamentais', 'demais_observacoes',
                            'equipamentos_necessarios', 'habilidades_comportamentais_necessarias', 'valor_venda','valor_compra_1',] )

    df.to_parquet(paths["dataset_features"], index=False)
    logging.info(f"Dataset com features salvos em {paths['dataset_features']}")


if __name__ == "__main__":
    main()
