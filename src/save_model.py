import pickle
import bentoml
import os
from config import load_config

config = load_config()
paths = config["paths"]


if not os.path.exists(paths["modelo_treinado"]):
    print(f"Erro: Arquivo pickle não encontrado em {paths["modelo_treinado"]}")
else:
    with open(paths["modelo_treinado"], "rb") as f:
        dados_carregados = pickle.load(f)

    # Extrai os componentes (opcional aqui, mas bom para clareza)
    model = dados_carregados["model"]
    imputer = dados_carregados["imputer"]
    scaler = dados_carregados["scaler"]
    features = dados_carregados["features"]

    print("Componentes carregados do pickle.")

    # --- Salve no formato BentoML ---
    tag_modelo = "classificador_de_candidatos" # <--- Escolha um nome para o seu bento model
    versao = "v1" # <--- Escolha uma versão

    # Metadados são úteis para rastreamento
    metadata = {
        "features": features,
        "model_type": type(model).__name__, # Ex: 'RandomForestClassifier'
        "imputer_type": type(imputer).__name__, # Ex: 'SimpleImputer'
        "scaler_type": type(scaler).__name__, # Ex: 'StandardScaler'
    }

    # Salva o dicionário inteiro usando bentoml.picklable_model
    saved_model_ref = bentoml.picklable_model.save_model(
        f"{tag_modelo}:{versao}", # Tag única: nome:versão
        dados_carregados,          # O objeto Python a ser salvo (seu dicionário)
        metadata=metadata
    )

    print(f"Modelo e pré-processadores salvos no BentoML com a tag: {saved_model_ref.tag}")

    # Alternativa (mais avançada): Salvar o modelo SKLearn diretamente
    # E carregar os pré-processadores separadamente no serviço.
    # Requereria salvar imputer/scaler/features de outra forma ou incluí-los
    # como 'arquivos' no bentofile.yaml.
    # Exemplo:
    # bentoml.sklearn.save_model(f"{tag_modelo}_sklearn", model, ...)
    # Você precisaria então carregar 'imputer', 'scaler', 'features' no service.py