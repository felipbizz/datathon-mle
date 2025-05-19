from mlflow.tracking import MlflowClient
import pandas as pd
import numpy as np
import mlflow

class ModelRegistry():
    def __init__(self, tracking_uri: str):

        self.client = MlflowClient(tracking_uri=tracking_uri)

    def purge_registered_models(self):
        """
        Remove all registered models from the MLflow tracking server.
        """
        
        for rm in self.client.search_registered_models():
            self.client.delete_registered_model(name=rm.name)

    def list_registered_models(self):
        """
        List all registered models from the MLflow tracking server.
        """

        registered_models = {
            "models" : []
        }
        
        for rm in self.client.search_registered_models():
            model = {
                "name": rm.name,
                "version": rm.latest_versions[0].version,
                "status": rm.latest_versions[0].current_stage,
                "description": rm.description,
                "run_id": rm.latest_versions[0].run_id,
                "creation_time": rm.creation_timestamp,
                "last_updated_time": rm.last_updated_timestamp,
                "tags": rm.tags,
            }
            registered_models["models"].append(model)

        return registered_models
    
    def load_model(self, model_name: str, version: int):
        """
        Carregando modelo treinado do registro.
        """
        model_uri = f"models:/{model_name}/{version}"
        try:
            model = mlflow.sklearn.load_model(model_uri=model_uri)
            print(f'Model type: {type(model)}')
            return model
        except Exception as e:
            print(f"Erro ao carregar o modelo: {e}")
            return None
        
    def predict(self, model_name: str, version: int, data: list, predict_type: str = "predict_proba"):
        """
        Fazendo previsões com o modelo carregado.
        """
        model = self.load_model(model_name=model_name, version=version)
        
        if model is not None:
            try:
                
                data_array = np.array(data).reshape(1,-1)

                match predict_type:
                    case "predict_proba":
                        predictions = model.predict_proba(data_array)
                    case "predict":
                        predictions = model.predict(data_array)
                    case "predict_log_proba":
                        predictions = model.predict_log_proba(data_array)
                    case _:
                        raise ValueError("Tipo de previsão inválido. Use 'predict_proba', 'predict' ou 'predict_log_proba'.")

                # if predict_type == "predict_proba":
                #     predictions = model.predict_proba(data_array)
                # elif predict_type == "predict":
                #     predictions = model.predict(data_array)
                # elif predict_type == "predict_log_proba":
                #     predictions = model.predict_log_proba(data_array)
                # else:
                #     raise ValueError("Tipo de previsão inválido. Use 'predict_proba', 'predict' ou 'predict_log_proba'.")   
        
                return predictions
            except Exception as e:
                print(f"Erro ao fazer previsões: {e}")
                return None
        else:
            print("Modelo não encontrado.")
            return None
