import pandas as pd
from config import load_config, get_abs_path
from log_config import logger

config = load_config()

paths = config['paths']

# PATH_APPLICANTS = get_abs_path(paths["applicants_silver"])
PATH_VAGAS = get_abs_path(paths['vagas_silver'])
PATH_PROSPECTS = get_abs_path(paths['prospects_silver'])

# applicants = pd.read_parquet(PATH_APPLICANTS)
df_vagas = pd.read_parquet(PATH_VAGAS)
df_prospects = pd.read_parquet(PATH_PROSPECTS)

# Merge dos datasets
# prospects contém cod_vaga
# vagas contém cod_vaga


def consolidar_dados():
    # Merge com vagas (via cod_vaga)
    df = df_prospects.merge(df_vagas, on='cod_vaga', how='left', suffixes=('', '_vaga'))

    missing = df.isnull().mean().sort_values(ascending=False)
    logger.info('Colunas com maior proporção de valores ausentes:')
    logger.info(missing[missing > 0.3])

    output_path = get_abs_path(paths['dataset_consolidado'])
    df.to_parquet(output_path, index=False)
    logger.info(f'Dataset consolidado salvo em: {output_path}')


if __name__ == '__main__':
    consolidar_dados()
