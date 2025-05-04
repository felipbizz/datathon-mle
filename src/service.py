import bentoml
import pandas as pd
import numpy as np
from bentoml.io import NumpyNdarray, PandasDataFrame, JSON

# Use a mesma tag (nome:versão) que você usou no save_model.py
BENTO_MODEL_TAG = "classificador_de_candidatos:v1" # <--- Use a tag exata que foi impressa

# Carrega o runner do BentoML para o modelo salvo
# O BentoML gerencia a otimização e escalabilidade disso
model_runner = bentoml.picklable_model.get(BENTO_MODEL_TAG).to_runner()

# Cria o serviço BentoML
# O nome do serviço será usado nos comandos e na URL
svc = bentoml.Service("api_classificador_candidatos", runners=[model_runner])

# Define a estrutura de entrada esperada (exemplo com JSON)
# Adapte conforme a forma como você quer enviar os dados para a API
# Pode ser JSON, PandasDataFrame, NumpyNdarray, etc.
# Veja: https://docs.bentoml.org/en/latest/concepts/io_descriptors.html
INPUT_SPEC = JSON()
# Exemplo de como seria o JSON de entrada:
# {
#   "feature1": 10.5,
#   "feature2": 20.1,
#   ... (todas as features na ordem esperada)
# }
# Ou uma lista de objetos para batch:
# [ { "f1": 1, "f2": 2 }, { "f1": 3, "f2": 4 } ]

@svc.api(input=INPUT_SPEC, output=JSON())
async def predict(input_data: dict) -> dict:
    """
    Recebe dados de entrada (JSON), aplica pré-processamento e retorna a predição.
    """
    try:
        # 1. Carregar os componentes do runner
        # O runner nos dá acesso ao objeto que salvamos (o dicionário)
        # Usamos 'run' para executar código que usa o objeto salvo
        loaded_components = await model_runner.async_run() # Executa de forma assíncrona

        model = loaded_components["model"]
        imputer = loaded_components["imputer"]
        scaler = loaded_components["scaler"]
        features_list = loaded_components["features"] # Lista de nomes das features

        # 2. Converter entrada para DataFrame (garantindo a ordem das colunas)
        # Se a entrada for um único dicionário
        if isinstance(input_data, dict):
             input_df = pd.DataFrame([input_data])
        # Se a entrada for uma lista de dicionários (batch)
        elif isinstance(input_data, list):
             input_df = pd.DataFrame(input_data)
        else:
            raise ValueError("Input deve ser um JSON object ou uma lista de JSON objects.")

        # Reordena/Seleciona colunas conforme a lista 'features' salva
        input_df = input_df[features_list]

        # 3. Aplicar pré-processamento
        data_imputed = imputer.transform(input_df)
        # O scaler geralmente retorna numpy array, então recriamos o DataFrame se necessário
        # (mas para predict, numpy array é geralmente suficiente)
        data_scaled = scaler.transform(data_imputed)

        # 4. Fazer a predição
        # Use predict_proba se quiser probabilidades, ou predict para a classe
        predictions = model.predict(data_scaled)
        # predictions_proba = model.predict_proba(data_scaled)

        # 5. Formatar a saída
        # Convertendo para lista Python para ser serializável em JSON
        return {"predictions": predictions.tolist(),
                "data_scaled": data_scaled.tolist(),}
        # return {"probabilities": predictions_proba.tolist()} # Exemplo com probabilidades

    except KeyError as e:
        # Captura erro se alguma feature esperada faltar no JSON de entrada
        return {"error": f"Missing feature in input: {str(e)}"}
    except Exception as e:
        # Captura outros erros
        # Em produção, logue o erro detalhado em vez de retorná-lo diretamente
        return {"error": f"An error occurred: {str(e)}"}