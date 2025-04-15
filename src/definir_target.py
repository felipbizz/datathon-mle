import pandas as pd

df = pd.read_parquet("../Datathon Decision/3_silver/dataset_consolidado.parquet")

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

df["situacao_candidado"] = df["situacao_candidado"].replace(
    situacao_candidado_nao_aprovado, "nao_aprovado"
)
df["situacao_candidado"] = df["situacao_candidado"].replace(
    situacao_candidado_aprovado, "aprovado"
)
df["situacao_candidado"] = df["situacao_candidado"].replace(
    situacao_candidado_desistente, "desistente"
)
df["situacao_candidado"] = df["situacao_candidado"].replace(
    situacao_candidato_inicial, "inicial"
)

# Definindo a target
df["target"] = (df["situacao_candidado"] == "aprovado").astype(int)

# Remover colunas que não podem ser usadas como preditoras
colunas_remover = ["situacao_candidado", "cod_applicant", "cod_vaga", "nome"]
df_model = df.drop(columns=[col for col in colunas_remover if col in df.columns])

df_model.to_parquet(
    "../Datathon Decision/3_silver/dataset_modelagem.parquet", index=False
)
print(
    "Dataset para modelagem salvo em ../Datathon Decision/3_silver/dataset_modelagem.parquet"
)
print("Distribuição da variável-alvo:")
print(df["target"].value_counts())
print("Distribuição das categorias de situação do candidato:")
print(df["situacao_candidado"].value_counts())
