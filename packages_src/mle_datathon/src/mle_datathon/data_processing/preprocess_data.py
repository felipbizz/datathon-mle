import pandas as pd
import numpy as np
import nltk
import re
import os

from nltk.corpus import stopwords
from unidecode import unidecode
from mle_datathon.utils import get_abs_path, load_config, set_log

logger = set_log("preprocess_data")

try:
    nltk.data.find("corpora/stopwords")
    logger.info("NLTK stopwords already downloaded.")
except LookupError:
    logger.info("NLTK stopwords not found. Downloading...")
    nltk.download("stopwords")
    logger.info("NLTK stopwords downloaded successfully.")

stop_words = set(stopwords.words("portuguese"))

local_path = os.getcwd()
config = load_config(local_path)


def remove_colunas_dominantes(df: pd.DataFrame, limite_dominancia: float = 0.9) -> set:
    colunas_remover = set()
    for col in df.columns:
        valor_mais_frequente = df[col].value_counts(normalize=True, dropna=True).max()
        if valor_mais_frequente > limite_dominancia:
            colunas_remover.add(col)
    df.drop(columns=colunas_remover, inplace=True)
    return df


def convert_json_to_df(
    path: str, index_col: str, cols_normalize: list = None, explode_col: str = None
) -> pd.DataFrame:
    df = (
        pd.read_json(path)
        .T.reset_index(drop=False)
        .rename(columns={"index": index_col})
    )

    if cols_normalize:
        for col in cols_normalize:
            df[pd.json_normalize(df[col]).columns] = pd.json_normalize(df[col])
            df = df.drop(columns=col)

    if explode_col:
        df = df.explode(column=explode_col)
        df = pd.concat(
            [
                df.reset_index(drop=True),
                pd.json_normalize(df[explode_col]).reset_index(drop=True),
            ],
            axis=1,
        )
        df.drop(columns=explode_col, inplace=True)
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].replace("", pd.NA)
    return df


def remove_colunas_irrelevantes(
    df: pd.DataFrame, limite_dominancia: float = 0.9
) -> pd.DataFrame:
    # Remove colunas que não possuem dados relevantes, onde mais de 90% dos valores são NaN
    df.dropna(thresh=len(df) * 0.1, axis=1, inplace=True)
    return df


def limpar_texto(texto):
    if isinstance(texto, str):
        texto = unidecode(texto)  # Remove acentos
        texto = texto.lower()
        texto = texto.replace("/", " ")
        texto = re.sub(r"[^\w\s]", "", texto)
        palavras = texto.split()
        palavras = [palavra for palavra in palavras if palavra not in stop_words]
        texto_limpo = " ".join(palavras).strip()
        texto_limpo = re.sub(r"\s+", " ", texto_limpo)
        return texto_limpo
    return None


def limpar_numeros_strings(valor):
    if isinstance(valor, str):
        return valor.replace("0", "").strip()
    return valor


def limpar_numeros(valor):
    if pd.isna(valor):
        return np.nan
    try:
        if isinstance(valor, (int, float)):
            return float(valor)
        if isinstance(valor, str):
            valor = valor.strip()
            # Case 1: US format (1,234.56)
            if "," in valor and "." in valor:
                if valor.find(",") < valor.find("."):
                    return float(valor.replace(",", ""))
            # Case 2: Brazilian format (2.000,00)
            if "." in valor and "," in valor:
                if valor.find(".") < valor.find(","):
                    cleaned = valor.replace(".", "").replace(",", ".")
                    return float(cleaned)
            # Case 3: Simple comma as decimal
            if "," in valor and "." not in valor:
                return float(valor.replace(",", "."))
            # Case 4: Plain number
            return float(valor)
        return np.nan
    except (ValueError, TypeError):
        return np.nan


def limpar_datas(valor):
    if pd.isna(valor):
        return None
    if isinstance(valor, str):
        valor = valor.strip()
        if valor in ("0000-00-00", "0000", "0"):
            return None
    try:
        data = pd.to_datetime(valor, errors="coerce", dayfirst=True)
        if pd.isna(data):
            return None
        if data.year < 1930 or data.year > 2030:
            return None
        return data
    except:
        return None


def limpar_anos(valor):
    if pd.isna(valor):
        return np.nan
    try:
        if isinstance(valor, str):
            valor = valor.strip()
            if valor in ("0000", "0"):
                return np.nan
        ano = float(valor)  # Changed from int to float
        if 1900 <= ano <= 2025:
            return ano
        return np.nan
    except (ValueError, TypeError):
        return np.nan


def clean_data(
    df, colunas_texto=None, colunas_data=None, colunas_anos=None, colunas_numeros=None
):
    df = df.copy()  # Create a copy to avoid modifying original
    df = remove_colunas_dominantes(df)
    df = remove_colunas_irrelevantes(df)

    if colunas_texto:
        for col in colunas_texto:
            df[col] = df[col].apply(limpar_texto)
    if colunas_data:
        for col in colunas_data:
            df[col] = df[col].apply(limpar_datas)
    if colunas_anos:
        for col in colunas_anos:
            df[col] = pd.to_numeric(df[col].apply(limpar_anos), errors="coerce")
    if colunas_numeros:
        for col in colunas_numeros:
            df[col] = pd.to_numeric(df[col].apply(limpar_numeros), errors="coerce")

    # precisa melhorar o preenchimento de valores ausentes
    colunas_cat = df.select_dtypes(include="object").columns
    for col in colunas_cat:
        df[col] = df[col].fillna("desconhecido")

    return df


situacao_candidado_nao_aprovado = [
    "nao aprovado rh",
    "nao aprovado cliente",
    "nao aprovado requisitante",
    "recusado",
]
situacao_candidado_aprovado = [
    "contratado decision",
    "prospect",
    "entrevista tecnica",
    "proposta aceita",
    "contratado hunting",
    "entrevista cliente",
    "documentacao clt",
    "documentacao pj",
    "documentacao cooperado",
    "encaminhar proposta",
]
situacao_candidado_desistente = ["desistiu", "desistiu contratacao", "avaliacao rh"]
situacao_candidato_inicial = [
    "encaminhado requisitante",
    "interesse nesta vaga",
    "inscrito",
]

mapping = {}
for s in situacao_candidado_nao_aprovado:
    mapping[s] = "nao_aprovado"
for s in situacao_candidado_aprovado:
    mapping[s] = "aprovado"
for s in situacao_candidado_desistente:
    mapping[s] = "desistente"
for s in situacao_candidato_inicial:
    mapping[s] = "inicial"


def execute_preprocess():
    paths = config["paths"]
    # df_applicants
    path_applicants = get_abs_path(local_path, paths["applicants_json"])
    cols_applicants = [
        "infos_basicas",
        "informacoes_pessoais",
        "informacoes_profissionais",
        "formacao_e_idiomas",
    ]
    df_applicants = convert_json_to_df(
        path=path_applicants, index_col="cod_applicant", cols_normalize=cols_applicants
    )
    df_applicants.to_parquet(
        get_abs_path(local_path, paths["applicants_bronze"]), index=False
    )
    logger.info("df_applicants %s", df_applicants.shape)

    # df_prospects
    path_prospects = get_abs_path(local_path, paths["prospects_json"])
    df_prospects = convert_json_to_df(
        path=path_prospects, index_col="cod_vaga", explode_col="prospects"
    )
    df_prospects.to_parquet(
        get_abs_path(local_path, paths["prospects_bronze"]), index=False
    )
    logger.info("df_prospects %s", df_prospects.shape)

    # df_vagas
    path_vagas = get_abs_path(local_path, paths["vagas_json"])
    cols_vagas = ["informacoes_basicas", "perfil_vaga", "beneficios"]
    df_vagas = convert_json_to_df(
        path=path_vagas, index_col="cod_vaga", cols_normalize=cols_vagas
    )
    df_vagas.to_parquet(get_abs_path(local_path, paths["vagas_bronze"]), index=False)
    logger.info("df_vagas %s", df_vagas.shape)

    logger.info("# --- TRATANDO COLUNAS TABELA APPLICANTS ---")

    colunas_texto_applicants = [
        "cv_pt",
        "objetivo_profissional",
        "fonte_indicacao",
        "titulo_profissional",
        "area_atuacao",
        "nivel_academico",
        "cursos",
    ]
    colunas_datas_applicants = ["data_criacao", "data_atualizacao", "data_nascimento"]
    df_applicants = clean_data(
        df_applicants,
        colunas_texto_applicants,
        colunas_datas_applicants,
        ["ano_conclusao"],
        ["remuneracao"],
    )
    df_applicants.to_parquet(
        get_abs_path(local_path, paths["applicants_silver"]), index=False
    )

    logger.info("# --- TRATANDO COLUNAS TABELA VAGAS ---  ")
    colunas_texto_vagas = [
        "titulo_vaga",
        "tipo_contratacao",
        "nivel_academico",
        "areas_atuacao",
        "principais_atividades",
        "competencia_tecnicas_e_comportamentais",
        "demais_observacoes",
        "equipamentos_necessarios",
        "habilidades_comportamentais_necessarias",
    ]
    colunas_datas_vagas = [
        "limite_esperado_para_contratacao",
        "data_inicial",
        "data_final",
    ]

    df_vagas = clean_data(df_vagas, colunas_texto_vagas, colunas_datas_vagas)
    df_vagas.to_parquet(get_abs_path(local_path, paths["vagas_silver"]), index=False)

    logger.info("# --- TRATANDO COLUNAS TABELA PROSPECTS ---")

    colunas_texto_prospects = ["titulo", "situacao_candidado", "comentario"]
    colunas_datas_prospects = ["data_candidatura"]
    df_prospects = clean_data(
        df_prospects, colunas_texto_prospects, colunas_datas_prospects
    )
    df_prospects.to_parquet(
        get_abs_path(local_path, paths["prospects_silver"]), index=False
    )
    logger.info("Data preprocessing completed.")

    df = df_prospects.merge(df_vagas, on="cod_vaga", how="left", suffixes=("", "_vaga"))

    output_path = get_abs_path(local_path, paths["dataset_consolidado"])
    df.to_parquet(output_path, index=False)
    logger.info(f"Dataset consolidado salvo em: {output_path}")

    df = pd.read_parquet(get_abs_path(local_path, paths["dataset_consolidado"]))
    df["situacao_candidado"] = df["situacao_candidado"].replace(mapping)

    # Definindo a target
    df["target"] = (df["situacao_candidado"] == "aprovado").astype(int)

    # Remover colunas que não podem ser usadas como preditoras
    colunas_remover = [
        "analista_responsavel",
        "cidade",
        "cliente",
        "cod_vaga",
        "codigo",
        "data_candidatura",
        "data_final",
        "data_inicial",
        "data_requicisao",
        "empresa_divisao",
        "estado",
        "limite_esperado_para_contratacao",
        "local_trabalho",
        "nome",
        "recrutador",
        "regiao",
        "requisitante",
        "situacao_candidado",
        "solicitante_cliente",
        "ultima_atualizacao",
    ]
    df_model = df.drop(columns=[col for col in colunas_remover if col in df.columns])

    # Salva o dataset de modelagem usando caminho absoluto
    df_model.to_parquet(
        get_abs_path(local_path, paths["dataset_modelagem"]), index=False
    )
    logger.info(f"Dataset para modelagem salvo em {paths['dataset_modelagem']}")
    logger.info("Distribuição da variável-alvo:")
    logger.info(df["target"].value_counts())
    logger.info("Distribuição das categorias de situação do candidato:")
    logger.info(df["situacao_candidado"].value_counts())
