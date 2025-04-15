import pandas as pd
from pathlib import Path

base_path = Path("../Datathon Decision/3_silver")
arquivos = {
    "applicants": base_path / "applicants.parquet",
    "vagas": base_path / "vagas.parquet",
    "prospects": base_path / "prospects.parquet",
}


def gerar_template_dicionario(nome, df):
    md = f"## {nome}\n\n| Coluna | Tipo | Descrição | Possíveis valores |\n|--------|------|-----------|------------------|\n"
    for col in df.columns:
        tipo = str(df[col].dtype)
        md += f"| {col} | {tipo} |  |  |\n"
    return md


if __name__ == "__main__":
    with open("data_dictionary_template.md", "w", encoding="utf-8") as f:
        for nome, caminho in arquivos.items():
            df = pd.read_parquet(caminho)
            md = gerar_template_dicionario(nome, df)
            f.write(md + "\n\n")
    print("Template de dicionário de dados gerado em data_dictionary_template.md")
