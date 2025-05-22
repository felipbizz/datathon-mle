import sys
import os
import pandas as pd
import streamlit as st
import pickle
import json
import requests
from loguru import logger

# --- Configuração Inicial de Paths e Módulos ---
try:
    current_script_path = os.path.abspath(__file__)
    current_script_dir = os.path.dirname(current_script_path)
    project_root = os.path.dirname(
        current_script_dir
    )  # Assumindo que app.py está em uma subpasta
    # Se o script estiver na raiz do projeto: project_root = current_script_dir
    src_dir_path = os.path.join(project_root, "src")

    if src_dir_path not in sys.path:
        sys.path.insert(0, src_dir_path)

    # As importações de mle_datathon permanecem, pois são sua biblioteca customizada
    from mle_datathon.utils import (
        get_abs_path,
    )  # Pode ser menos usado agora, mas mantido caso suas funções internas precisem
    from mle_datathon.data_processing.feature_engineering import (
        clean_features_data,
        transform_new_data,
    )
except ImportError as e:
    st.error(
        f"Erro ao importar módulos do projeto: {e}. Verifique a estrutura de pastas e o PYTHONPATH."
    )
    logger.critical(f"Falha na importação de módulos customizados: {e}")
    st.stop()
except (
    NameError
):  # __file__ not defined (e.g. running in stlite or certain IDEs without it)
    project_root = os.getcwd()  # Fallback
    logger.warning(
        "__file__ não definido, usando os.getcwd() como project_root. Caminhos hardcoded podem precisar de ajuste manual."
    )
    # Potencialmente adicionar src_dir_path aqui também se necessário e não feito acima.

st.set_page_config(layout="wide", page_title="Previsão de Sucesso de Candidatos")

# --- Valores Hardcoded (Substitua pelos seus caminhos e URL corretos) ---
# Estes caminhos são relativos à raiz do projeto (project_root)
PATH_MODELO_TREINADO = os.path.join(
    project_root, "Datathon Decision/4_gold", "modelo_treinado.pkl"
)  # Exemplo, ajuste o nome
PATH_PROSPECTS_SILVER = os.path.join(
    project_root, "Datathon Decision/3_silver", "prospects.parquet"
)  # Exemplo
PATH_VAGAS_SILVER = os.path.join(
    project_root, "Datathon Decision/3_silver", "vagas.parquet"
)  # Exemplo
PATH_ENCODERS_GOLD = os.path.join(
    project_root, "Datathon Decision/4_gold", "encoders"
)  # Exemplo
API_URL = "http://localhost:8000/api/v1/model/predict"

# --- Funções Auxiliares ---


@st.cache_data  # Usar _ aqui para indicar que a função não recebe argumentos variáveis para cache
def carregar_recursos_aplicacao_hardcoded():
    logger.info("Carregando recursos da aplicação (valores hardcoded)...")
    try:
        # Usar os paths hardcoded diretamente
        with open(PATH_MODELO_TREINADO, "rb") as f_model:
            dados_modelo = pickle.load(f_model)

        df_prospects = pd.read_parquet(PATH_PROSPECTS_SILVER)
        df_vagas = pd.read_parquet(PATH_VAGAS_SILVER)

        # Verificar se o caminho dos encoders existe
        if not os.path.exists(PATH_ENCODERS_GOLD):
            logger.warning(
                f"Caminho para encoders não encontrado: {PATH_ENCODERS_GOLD}. 'transform_new_data' pode falhar."
            )

        logger.info("Recursos da aplicação carregados com sucesso.")
        return dados_modelo, df_prospects, df_vagas, API_URL, PATH_ENCODERS_GOLD
    except FileNotFoundError as e:
        logger.error(f"Arquivo não encontrado durante o carregamento de recursos: {e}")
        st.error(
            f"Erro: Arquivo essencial não encontrado: {e}. Verifique os caminhos definidos no código."
        )
        return None, None, None, None, None
    except Exception as e:
        logger.error(f"Erro inesperado ao carregar recursos: {e}")
        st.error(f"Erro inesperado ao carregar recursos da aplicação: {e}")
        return None, None, None, None, None


def preparar_dados_para_payload(
    prospect_df,
    vagas_df,
    encoders_path_param,
    feature_list_param,
    imputer_obj_param,
    scaler_obj_param,
):
    logger.info("Iniciando preparação de dados para o payload.")
    caso_merged = prospect_df.merge(
        vagas_df, on="cod_vaga", how="left", suffixes=("", "_vaga")
    )

    if not encoders_path_param or not os.path.exists(encoders_path_param):
        msg = f"Caminho dos encoders inválido ou não encontrado: {encoders_path_param}"
        logger.error(msg)
        return pd.DataFrame(), msg

    try:
        caso_transformado = transform_new_data(
            caso_merged.copy(), encoders_path=encoders_path_param
        )
        caso_limpo_com_features = clean_features_data(caso_transformado.copy())

        features_df_payload = caso_limpo_com_features[feature_list_param].fillna(0)
        logger.info(
            f"Dados preparados. Features para payload: {features_df_payload.columns.tolist()}"
        )
        return features_df_payload, None
    except KeyError as e:
        disponiveis_str = (
            caso_limpo_com_features.columns.tolist()
            if "caso_limpo_com_features" in locals()
            else "N/A (erro antes da criação)"
        )
        msg = f"Erro ao selecionar features para o modelo: {e}. Features esperadas: {feature_list_param}. Features disponíveis: {disponiveis_str}"
        logger.error(msg)
        return pd.DataFrame(), msg
    except Exception as e:
        msg = f"Erro inesperado durante a preparação dos dados: {e}"
        logger.exception(msg)
        return pd.DataFrame(), msg


def obter_predicao_api(
    api_url_param, payload_data_list, model_type_param, model_version_str_param
):
    logger.info(f"Enviando requisição para API: {api_url_param}")
    if not payload_data_list or not payload_data_list[0]:
        logger.error("Payload para API está vazio ou inválido.")
        return {
            "error": "Payload Inválido",
            "details": "Não foi possível gerar dados válidos para a API.",
        }, "Payload Inválido"

    payload = json.dumps(
        {
            "model_name": model_type_param,
            "model_version": model_version_str_param,
            "data": payload_data_list,
        }
    )
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(
            api_url_param, headers=headers, data=payload, timeout=20
        )
        response.raise_for_status()
        logger.info(
            f"Resposta da API recebida com sucesso. Status: {response.status_code}"
        )
        return response.json(), None
    except requests.exceptions.Timeout:
        msg = f"Timeout (20s) ao tentar conectar à API em {api_url_param}."
        logger.error(msg)
        return {"error": "Timeout API", "details": msg}, msg
    except requests.exceptions.ConnectionError:
        msg = f"Erro de conexão com a API em {api_url_param}. Verifique o servidor."
        logger.error(msg)
        return {"error": "Erro de Conexão API", "details": msg}, msg
    except requests.exceptions.HTTPError as http_err:
        msg = f"Erro HTTP da API: {http_err}. Resposta: {http_err.response.text}"
        logger.error(msg)
        return {
            "error": f"Erro HTTP API: {http_err.response.status_code}",
            "details": http_err.response.text,
        }, msg
    except requests.exceptions.RequestException as req_err:
        msg = f"Erro na requisição à API: {req_err}"
        logger.error(msg)
        return {"error": "Erro Requisição API", "details": str(req_err)}, msg
    except json.JSONDecodeError:
        raw_resp_text = (
            response.text if "response" in locals() else "N/A (resposta não capturada)"
        )
        msg = "A API retornou uma resposta que não é um JSON válido."
        logger.error(f"{msg} Raw response: {raw_resp_text}")
        return {
            "error": "JSON Inválido API",
            "details": msg,
            "raw_response": raw_resp_text,
        }, msg


def calcular_indice_adequacao(probabilidade_sucesso):
    if probabilidade_sucesso <= 0.2:
        indice = 1 + (probabilidade_sucesso / 0.2) * 1.5
        return min(max(round(indice, 1), 1.0), 2.5)
    elif probabilidade_sucesso <= 0.40:
        indice = 2.6 + ((probabilidade_sucesso - 0.2) / 0.2) * 2.4
        return min(max(round(indice, 1), 2.6), 5.0)
    elif probabilidade_sucesso <= 0.6:
        indice = 5.1 + ((probabilidade_sucesso - 0.4) / 0.2) * 2.4
        return min(max(round(indice, 1), 5.1), 7.5)
    else:
        indice = 7.6 + ((probabilidade_sucesso - 0.6) / 0.4) * 2.4
        return min(max(round(indice, 1), 7.6), 10.0)


# --- Inicialização da Aplicação Streamlit ---
dados_carregados, df_prospects, df_vagas, api_url_loaded, encoders_path_loaded = (
    carregar_recursos_aplicacao_hardcoded()
)

if not dados_carregados:
    st.error(
        "Falha crítica ao carregar recursos essenciais. A aplicação não pode continuar."
    )
    st.stop()

modelo = dados_carregados["model"]
imputer = dados_carregados["imputer"]
scaler = dados_carregados["scaler"]
features = dados_carregados["features"]
model_type_loaded = dados_carregados.get("model_type", "RandomForest")
model_version_loaded = str(dados_carregados.get("model_version", 1))

# --- Interface Principal ---
st.title("🚀 Previsão de Sucesso de Candidatos")
st.markdown("""
Bem-vindo ao Sistema de Previsão de Sucesso de Candidatos!
Esta aplicação demonstra um pipeline de Machine Learning para prever a chance do perfil do candidato ser bem-sucedido na vaga.
Utilize o botão abaixo para carregar os dados de um candidato aleatório e ver a previsão. ✨
""")
st.markdown("---")

# --- Sidebar ---
st.sidebar.header("ℹ️ Sobre o Projeto")
st.sidebar.markdown("""
Este projeto demonstra a implementação de um pipeline completo de Engenharia de Machine Learning (MLE) para prever o sucesso de candidatos em processos seletivos.
- **Objetivos:** Pipeline robusto, MLOps, sistema pronto para produção.
- **Tecnologias:** Python, Streamlit, FastAPI, Scikit-learn, Docker.
""")
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
Este sistema utiliza um modelo **{model_type_loaded}** para prever o sucesso.
- **Versão do Modelo:** {model_version_loaded}
""")
st.sidebar.markdown("---")

# --- Gerenciamento de Estado da Sessão ---
if "prospect_selecionado" not in st.session_state:
    st.session_state.prospect_selecionado = None
if "caso_processado" not in st.session_state:
    st.session_state.caso_processado = None
if "resultado_previsao" not in st.session_state:
    st.session_state.resultado_previsao = None

# --- Interação Principal ---
st.header("🔮 Teste de Previsão")

if st.button(
    "👤 Carregar Prospect Aleatório e Prever",
    type="primary",
    help="Clique para selecionar um candidato e obter a previsão.",
):
    st.session_state.prospect_selecionado = None
    st.session_state.caso_processado = None
    st.session_state.resultado_previsao = None

    if df_prospects is None or df_prospects.empty:
        st.error(
            "Não há dados de prospects carregados. Verifique os caminhos hardcoded e os arquivos de dados."
        )
        st.stop()

    with st.spinner("Selecionando prospect e preparando dados..."):
        um_prospect_aleatorio_df = df_prospects.sample(1)
        st.session_state.prospect_selecionado = um_prospect_aleatorio_df

        features_df_payload, erro_preparacao = preparar_dados_para_payload(
            um_prospect_aleatorio_df,
            df_vagas,
            encoders_path_loaded,
            features,
            imputer,
            scaler,
        )

        if erro_preparacao:
            st.error(f"Falha na preparação dos dados: {erro_preparacao}")
            st.session_state.caso_processado = pd.DataFrame()
            logger.error(f"Erro na preparação de dados (UI): {erro_preparacao}")
        else:
            st.session_state.caso_processado = features_df_payload

    if (
        st.session_state.caso_processado is not None
        and not st.session_state.caso_processado.empty
    ):
        with st.spinner("Enviando dados para a API e aguardando previsão... ⏳"):
            payload_list = st.session_state.caso_processado.values.tolist()

            resultado_api, erro_api = obter_predicao_api(
                api_url_loaded, payload_list, model_type_loaded, model_version_loaded
            )
            st.session_state.resultado_previsao = resultado_api
            if (
                erro_api
                and isinstance(resultado_api, dict)
                and "error" in resultado_api
            ):  # erro já formatado
                pass
            elif erro_api:
                st.session_state.resultado_previsao = {
                    "error": "Erro API Genérico",
                    "details": erro_api,
                }
                logger.error(f"Erro genérico da API (UI): {erro_api}")

# --- Exibição dos Resultados ---
if st.session_state.prospect_selecionado is not None:
    st.markdown("---")
    st.subheader("📄 Detalhes do Processo")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Prospect Original Selecionado:**")
        st.dataframe(st.session_state.prospect_selecionado)

        if (
            st.session_state.caso_processado is not None
            and not st.session_state.caso_processado.empty
        ):
            with st.expander("Ver Features Enviadas ao Modelo"):
                st.write("**Features Processadas e Enviadas:**")
                st.dataframe(st.session_state.caso_processado)
        elif (
            st.session_state.caso_processado is not None
            and st.session_state.caso_processado.empty
        ):
            st.warning(
                "Não foi possível processar as features para este prospect devido a um erro anterior."
            )

    with col2:
        st.write("**Resultados:**")
        resultado = st.session_state.resultado_previsao

        if resultado:
            if isinstance(resultado, dict) and "error" in resultado:
                error_msg = resultado.get("details", resultado["error"])
                st.error(f"Falha na obtenção da previsão: {error_msg}")
                logger.warning(f"Exibindo erro da API para o usuário (UI): {error_msg}")
                if "raw_response" in resultado:
                    st.text_area(
                        "Resposta Bruta da API (debug):",
                        resultado["raw_response"],
                        height=100,
                    )
                elif isinstance(resultado.get("details"), str) and resultado[
                    "details"
                ].strip().startswith("{"):
                    try:
                        st.json(json.loads(resultado["details"]))
                    except:
                        pass
            else:
                actual_predictions_data = None
                if isinstance(resultado, dict) and "predictions" in resultado:
                    actual_predictions_data = resultado["predictions"]
                elif (
                    isinstance(resultado, list)
                    and len(resultado) > 0
                    and isinstance(resultado[0], list)
                ):
                    actual_predictions_data = resultado

                if (
                    actual_predictions_data
                    and isinstance(actual_predictions_data, list)
                    and actual_predictions_data
                ):
                    first_sample_prediction_list = actual_predictions_data[0]

                    if (
                        isinstance(first_sample_prediction_list, list)
                        and len(first_sample_prediction_list) >= 2
                    ):
                        probabilidade_sucesso = float(first_sample_prediction_list[1])
                        logger.info(
                            f"Probabilidade de sucesso extraída: {probabilidade_sucesso}"
                        )

                        status_candidato = ""
                        recomendacao_msg = ""

                        if probabilidade_sucesso <= 0.25:
                            status_candidato = "Performance Baixa"
                            recomendacao_msg = (
                                "Enviar feedback para melhorar preenchimento do perfil."
                            )
                            st.error(recomendacao_msg)
                        elif probabilidade_sucesso <= 0.40:
                            status_candidato = "Performance Moderada"
                            recomendacao_msg = "Analisar com cautela se houver outros fatores positivos."
                            st.warning(recomendacao_msg)
                        elif probabilidade_sucesso <= 0.6:
                            status_candidato = "Performance Boa"
                            recomendacao_msg = "Recomendado, mas pode necessitar de desenvolvimento ou validação adicional."
                            st.info(recomendacao_msg)
                        else:
                            status_candidato = "Performance Alta"
                            recomendacao_msg = "Candidato com performance alta! Forte recomendação para prosseguir."
                            st.success(recomendacao_msg)

                        indice_adequacao_candidato = calcular_indice_adequacao(
                            probabilidade_sucesso
                        )

                        st.metric(
                            label="Previsão de Sucesso (Modelo)",
                            value=f"{probabilidade_sucesso:.2%}",
                            delta=status_candidato,
                            delta_color="off",
                        )
                        if indice_adequacao_candidato >= 8:
                            st.markdown("⭐⭐⭐ Excelente Fit!")
                        elif indice_adequacao_candidato >= 6:
                            st.markdown("⭐⭐ Bom Fit.")
                        elif indice_adequacao_candidato >= 3:
                            st.markdown("⭐ Fit Moderado.")
                        else:
                            st.markdown("⚠️ Baixo Fit.")

                        with st.expander("Ver Dados da Previsão da API"):
                            st.json(actual_predictions_data)
                        if isinstance(resultado, dict) and "predictions" in resultado:
                            with st.expander("Ver Resposta Completa Original da API"):
                                st.json(resultado)
                    else:
                        st.error("Formato da lista de predição interna inesperado.")
                        st.json(resultado)
                        logger.error(
                            f"Formato inesperado para first_sample_prediction_list (UI): {first_sample_prediction_list}"
                        )
                else:
                    st.error(
                        "A resposta da API não continha dados de predição válidos no formato esperado."
                    )
                    st.json(resultado)
                    logger.error(
                        f"actual_predictions_data não é válido ou está vazio (UI): {actual_predictions_data}"
                    )
        else:
            st.info(
                "Clique no botão 'Carregar Prospect Aleatório e Prever' para ver a análise."
            )
else:
    if not dados_carregados:
        st.warning(
            "Recursos da aplicação não puderam ser carregados. Verifique os logs e os caminhos no código."
        )
    else:
        st.info("Aguardando a seleção de um prospect para iniciar a análise.")

st.markdown("---")
logger.info("Renderização da página Streamlit concluída.")
