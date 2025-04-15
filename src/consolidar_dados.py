import pandas as pd

PATH_APPLICANTS = "../Datathon Decision/3_silver/applicants.parquet"
PATH_VAGAS = "../Datathon Decision/3_silver/vagas.parquet"
PATH_PROSPECTS = "../Datathon Decision/3_silver/prospects.parquet"

applicants = pd.read_parquet(PATH_APPLICANTS)
vagas = pd.read_parquet(PATH_VAGAS)
prospects = pd.read_parquet(PATH_PROSPECTS)

# Merge dos datasets
# prospects contém cod_vaga e nome do candidato (nome)
# applicants contém nome e cod_applicant
# vagas contém cod_vaga

# Merge prospects + applicants (via nome)
df = prospects.merge(applicants, on="nome", how="left", suffixes=("", "_app"))
# Merge com vagas (via cod_vaga)
df = df.merge(vagas, on="cod_vaga", how="left", suffixes=("", "_vaga"))

print(f"DataFrame consolidado: {df.shape}")
df.head()

missing = df.isnull().mean().sort_values(ascending=False)
print("Colunas com maior proporção de valores ausentes:")
print(missing[missing > 0.3])

# precisa melhorar o preenchimento de valores ausentes
colunas_cat = df.select_dtypes(include="object").columns
for col in colunas_cat:
    df[col] = df[col].fillna("desconhecido")

# Precisa melhorar a padronização de datas
df["data_candidatura"] = pd.to_datetime(df["data_candidatura"], errors="coerce")

output_path = "../Datathon Decision/3_silver/dataset_consolidado.parquet"
df.to_parquet(output_path, index=False)
print(f"Dataset consolidado salvo em: {output_path}")
