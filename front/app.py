import sys
import os

current_script_path = os.path.abspath(__file__)
current_script_dir = os.path.dirname(current_script_path)
project_root = os.path.dirname(current_script_dir)
src_dir_path = os.path.join(project_root, 'src')

if src_dir_path not in sys.path:
    sys.path.insert(0, src_dir_path)

from mle_datathon.utils import load_config, get_abs_path
from mle_datathon.data_processing.feature_engineering import clean_features_data, transform_new_data
from loguru import logger # Assuming log_config.py is in src
import pandas as pd
import streamlit as st
import pickle
import json
import requests

st.title('Teste App')

url = "http://localhost:8000/api/v1/model/predict"

local_path = os.getcwd()
config = load_config(local_path)

paths = config['paths']

with open(paths['modelo_treinado'], 'rb') as f:
    dados_carregados = pickle.load(f)

modelo = dados_carregados['model']
imputer = dados_carregados['imputer']
scaler = dados_carregados['scaler']
features = dados_carregados['features']

# Todos os dados que entrarem na aplicação vão passar passar pelo pipeline de limpeza e construção das camadas do Data Lake.
# Então nós já vamos pegar da camada silves pra otimizar
df_prospects = pd.read_parquet(get_abs_path(local_path, paths['prospects_silver']))
df_vagas = pd.read_parquet(get_abs_path(local_path, paths['vagas_silver']))

um_prospect_aleatorio = None

if st.button('Carregar dados de um prospect aleatório'):

    um_prospect_aleatorio = df_prospects.sample(1)
    st.write('Um prospect aleatório:')
    st.write(um_prospect_aleatorio)

if um_prospect_aleatorio is not None:
    with st.spinner('Carregando dados de um prospect aleatório...'):
        um_caso_aleatorio = um_prospect_aleatorio.merge(
            df_vagas, on='cod_vaga', how='left', suffixes=('', '_vaga')
        )

        encoders_path = '/home/felip/projetos/datathon-mle/Datathon Decision/4_gold/encoders'

        um_caso_aleatorio = transform_new_data(um_caso_aleatorio, encoders_path=encoders_path)

        um_caso_aleatorio = clean_features_data(um_caso_aleatorio)
        st.write('Features do prospect aleatório:')
        st.write(um_caso_aleatorio.values)

        payload = json.dumps({
        "model_name": "RandomForest",
        "model_version": 1,
        "data": um_caso_aleatorio.values.tolist()
        })
        headers = {
        'Content-Type': 'application/json',
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        st.write('Resultados do modelo:')
        st.write(response.text)


try:
    logger.info("Streamlit app started successfully.")
    st.write("Check your logs for messages from logger.")

except NameError as e:
    st.warning(f"A function or variable might not be defined yet: {e}")
except Exception as e:
    st.error(f"An error occurred during execution: {e}")