import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

PATH_APPLICANTS = "../Datathon Decision/3_silver/applicants.parquet"
PATH_VAGAS = "../Datathon Decision/3_silver/vagas.parquet"
PATH_PROSPECTS = "../Datathon Decision/3_silver/prospects.parquet"

applicants = pd.read_parquet(PATH_APPLICANTS)
vagas = pd.read_parquet(PATH_VAGAS)
prospects = pd.read_parquet(PATH_PROSPECTS)

plt.figure(figsize=(10, 5))
sns.countplot(
    data=prospects,
    x="situacao_candidado",
    order=prospects["situacao_candidado"].value_counts().index,
)
plt.title("Distribuição da variável-alvo: situacao_candidado")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("distribuicao_situacao_candidato.png")
plt.close()


def missing_report(df, name):
    na = df.isnull().mean().sort_values(ascending=False)
    print(f"\nValores ausentes em {name}:")
    print(na[na > 0])


missing_report(applicants, "applicants")
missing_report(vagas, "vagas")
missing_report(prospects, "prospects")

print("\nEstatísticas descritivas - applicants:")
print(
    applicants.describe(
        include="all",
    )
)

print("\nEstatísticas descritivas - vagas:")
print(
    vagas.describe(
        include="all",
    )
)

print("\nEstatísticas descritivas - prospects:")
print(
    prospects.describe(
        include="all",
    )
)

# Merge para análise cruzada
df_merged = prospects.merge(
    applicants[["nome", "nivel_academico"]], on="nome", how="left"
)

plt.figure(figsize=(10, 5))
sns.countplot(
    data=df_merged,
    x="nivel_academico",
    hue="situacao_candidado",
    order=df_merged["nivel_academico"].value_counts().index,
)
plt.title("Nível acadêmico vs. situação do candidato")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("nivel_academico_vs_situacao.png")
plt.close()

if "area_atuacao" in applicants.columns:
    df_merged_area = prospects.merge(
        applicants[["nome", "area_atuacao"]], on="nome", how="left"
    )
    plt.figure(figsize=(12, 6))
    sns.countplot(
        data=df_merged_area,
        x="area_atuacao",
        hue="situacao_candidado",
        order=df_merged_area["area_atuacao"].value_counts().index,
    )
    plt.title("Área de atuação vs. situação do candidato")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("area_atuacao_vs_situacao.png")
    plt.close()
    # Tabela de contingência
    tab_area = pd.crosstab(
        df_merged_area["area_atuacao"], df_merged_area["situacao_candidado"]
    )
    tab_area.to_csv("tabela_area_atuacao_vs_situacao.csv")
    print("\nTabela de contingência área de atuação vs. situação do candidato salva.")

if "nivel_academico" in df_merged.columns:
    tab_nivel = pd.crosstab(
        df_merged["nivel_academico"], df_merged["situacao_candidado"]
    )
    tab_nivel.to_csv("tabela_nivel_academico_vs_situacao.csv")
    print("Tabela de contingência nível acadêmico vs. situação do candidato salva.")

print("\nEDA concluída. Gráficos salvos no diretório atual.")
