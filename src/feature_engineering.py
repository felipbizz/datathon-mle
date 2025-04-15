import pandas as pd
from datetime import datetime
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from nltk.corpus import stopwords
from src.log_config import logging

stop_words = set(stopwords.words("portuguese"))

input_path = "../Datathon Decision/3_silver/dataset_modelagem.parquet"
df = pd.read_parquet(input_path)


# Função auxiliar para checar se uma coluna pode ser usada para feature
# Critérios: existe, menos de 50% missing, não é valor dominante (>90%)
def coluna_valida(df, col):
    if col not in df.columns:
        return False
    missing = df[col].isnull().mean()
    if missing > 0.5:
        logging.info(f'[SKIP] Coluna "{col}" com {missing:.0%} missing, feature não criada.')
        return False
    vc = df[col].value_counts(normalize=True, dropna=True)
    if not vc.empty and vc.iloc[0] > 0.9:
        logging.info(
            f'[SKIP] Coluna "{col}" com valor dominante ({vc.index[0]}) em {vc.iloc[0]:.0%}, feature não criada.'
        )
        return False
    return True


# precisa melhorar essa lista de palavras chave, isso é só um exemplo pra iniciar o processo
PALAVRAS_CHAVE = [
    "python",
    "gestao",
    "sênior",
    "senior",
    "lideranca",
    "liderança",
    "java",
    "sql",
    "analista",
    "projeto",
]


def tamanho_texto(texto):
    if pd.isnull(texto):
        return 0
    return len(str(texto))


def n_palavras(texto):
    if pd.isnull(texto):
        return 0
    return len(str(texto).split())


def conta_palavras_chave(texto, palavras=PALAVRAS_CHAVE):
    if pd.isnull(texto):
        return 0
    texto = str(texto).lower()
    return sum(1 for p in palavras if p in texto)


def conta_cursos(texto):
    if pd.isnull(texto):
        return 0
    return len([c for c in re.split(r"[;,\n]", str(texto)) if c.strip()])


# 1. Tempo entre inscrição e status final
if coluna_valida(df, "data_candidatura") and coluna_valida(df, "data_status_final"):
    df["tempo_processo_dias"] = (
        df["data_status_final"] - df["data_candidatura"]
    ).dt.days
    logging.info("[OK] Feature tempo_processo_dias criada.")
else:
    logging.info("[SKIP] Feature tempo_processo_dias não criada.")

# 2. Similaridade entre área de atuação do candidato e da vaga
if coluna_valida(df, "area_atuacao") and coluna_valida(df, "areas_atuacao"):
    df["match_area_atuacao"] = df.apply(
        lambda x: int(str(x["area_atuacao"]) in str(x["areas_atuacao"])), axis=1
    )
    logging.info("[OK] Feature match_area_atuacao criada.")
else:
    logging.info("[SKIP] Feature match_area_atuacao não criada.")

# 3. Nível acadêmico do candidato (one-hot encoding)
if coluna_valida(df, "nivel_academico"):
    df = pd.get_dummies(
        df, columns=["nivel_academico"], prefix="nivel_acad", dummy_na=True
    )
    logging.info("[OK] One-hot de nivel_academico criado.")
else:
    logging.info("[SKIP] One-hot de nivel_academico não criado.")

# 4. Tipo de contratação da vaga (one-hot encoding)
if coluna_valida(df, "tipo_contratacao"):
    df = pd.get_dummies(
        df, columns=["tipo_contratacao"], prefix="tipo_contr", dummy_na=True
    )
    logging.info("[OK] One-hot de tipo_contratacao criado.")
else:
    logging.info("[SKIP] One-hot de tipo_contratacao não criado.")

# 5. Remuneração do candidato e da vaga
if coluna_valida(df, "remuneracao"):
    df["remuneracao"] = pd.to_numeric(df["remuneracao"], errors="coerce")
    logging.info("[OK] Feature remuneracao criada.")
if coluna_valida(df, "remuneracao_vaga"):
    df["remuneracao_vaga"] = pd.to_numeric(df["remuneracao_vaga"], errors="coerce")
    logging.info("[OK] Feature remuneracao_vaga criada.")

# 6. Quantidade de etapas avançadas (exemplo: histórico de status)
if coluna_valida(df, "historico_status"):
    df["qtd_etapas"] = df["historico_status"].apply(
        lambda x: len(x) if isinstance(x, list) else 1
    )
    logging.info("[OK] Feature qtd_etapas criada.")

# 7. Idade do candidato
if coluna_valida(df, "data_nascimento"):
    df["idade"] = df["data_nascimento"].apply(
        lambda x: (datetime.now().year - x.year) if pd.notnull(x) else None
    )
    logging.info("[OK] Feature idade criada.")
else:
    logging.info("[SKIP] Feature idade não criada.")

# 8. Fonte de indicação (binária)
if coluna_valida(df, "fonte_indicacao"):
    df["indicacao"] = df["fonte_indicacao"].apply(
        lambda x: int(pd.notnull(x) and x != "desconhecido")
    )
    logging.info("[OK] Feature indicacao criada.")
else:
    logging.info("[SKIP] Feature indicacao não criada.")

campos_texto = [
    "cv_pt",
    "objetivo_profissional",
    "titulo_profissional",
    "cursos",
    "titulo_vaga",
    "principais_atividades",
    "competencia_tecnicas_e_comportamentais",
    "demais_observacoes",
    "comentario",
]
for campo in campos_texto:
    if campo in df.columns:
        df[f"{campo}_nchar"] = df[campo].apply(tamanho_texto)
        df[f"{campo}_nwords"] = df[campo].apply(n_palavras)
        logging.info(f"[OK] Features de tamanho para {campo} criadas.")

# Features de palavras-chave
campos_palavras_chave = [
    "cv_pt",
    "objetivo_profissional",
    "principais_atividades",
    "competencia_tecnicas_e_comportamentais",
    "comentario",
]
for campo in campos_palavras_chave:
    if campo in df.columns:
        df[f"{campo}_n_keywords"] = df[campo].apply(conta_palavras_chave)
        logging.info(f"[OK] Feature de palavras-chave para {campo} criada.")

# Feature de quantidade de cursos
if "cursos" in df.columns:
    df["cursos_n"] = df["cursos"].apply(conta_cursos)
    logging.info("[OK] Feature cursos_n criada.")

# Clusterização de perfis de currículo (cv_pt)
if "cv_pt" in df.columns:
    logging.info("[INFO] Iniciando clusterização de perfis de currículo...")
    textos_cv = df["cv_pt"].fillna("")
    vectorizer = TfidfVectorizer(max_features=300, stop_words=list(stop_words))
    X_cv = vectorizer.fit_transform(textos_cv)
    n_clusters = 7  # vamos utilizar uma forma de clusterização melhor depois, comecei com kmeans só pra iniciar
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_cv)
    df["cv_cluster"] = clusters
    logging.info(f"[OK] Feature cv_cluster criada com {n_clusters} clusters.")


df.to_parquet("../Datathon Decision/3_silver/dataset_features.parquet", index=False)
logging.info(
    "Dataset com features salvos em ../Datathon Decision/3_silver/dataset_features.parquet"
)
