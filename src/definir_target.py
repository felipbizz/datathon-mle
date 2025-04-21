from log_config import logging
import pandas as pd
from config import load_config, get_abs_path

config = load_config()
paths = config["paths"]

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

def define_target():
    # Lê o dataset consolidado usando caminho absoluto
    df = pd.read_parquet(get_abs_path(paths["dataset_consolidado"]))
    df["situacao_candidado"] = df["situacao_candidado"].replace(mapping)

    # Definindo a target
    df["target"] = (df["situacao_candidado"] == "aprovado").astype(int)

    # Remover colunas que não podem ser usadas como preditoras
    colunas_remover = ['analista_responsavel', 'cidade','cliente','cod_vaga','codigo', 'data_candidatura', 'data_final', 'data_inicial','data_requicisao',
                        'empresa_divisao','estado','limite_esperado_para_contratacao', 'local_trabalho','nome','recrutador',
                        'regiao','requisitante', 'situacao_candidado', 'solicitante_cliente', 'ultima_atualizacao']
    df_model = df.drop(columns=[col for col in colunas_remover if col in df.columns])

    # Salva o dataset de modelagem usando caminho absoluto
    df_model.to_parquet(get_abs_path(paths["dataset_modelagem"]), index=False)
    logging.info(f"Dataset para modelagem salvo em {paths['dataset_modelagem']}")
    logging.info("Distribuição da variável-alvo:")
    logging.info(df["target"].value_counts())
    logging.info("Distribuição das categorias de situação do candidato:")
    logging.info(df["situacao_candidado"].value_counts())

if __name__ == '__main__':
    define_target()