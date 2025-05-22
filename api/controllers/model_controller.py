from fastapi import APIRouter, Body
from typing import Annotated
from mle_datathon.utils import set_log
from mle_datathon.model import ModelRegistry

import os

from prometheus_client import Summary, Counter

logger = set_log("model_controller", level=10)

tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
logger.info(f"MLflow Tracking URI: {tracking_uri}")

mr = ModelRegistry(tracking_uri=tracking_uri)

router = APIRouter(prefix="/api/v1/model", tags=["Endpoints do Modelo"])

# Define Prometheus metrics
TUNE_REQUEST_TIME = Summary(
    "tune_request_processing_seconds", "Tempo gasto processando requisições de ajuste"
)
TRAIN_REQUEST_TIME = Summary(
    "train_request_processing_seconds",
    "Tempo gasto processando requisições de treinamento",
)
PREDICT_REQUEST_TIME = Summary(
    "predict_request_processing_seconds",
    "Tempo gasto processando requisições de previsão",
)
PREDICT_COUNT = Counter("request_count", "Número total de previsões")


@router.get("/list")
def list_models():
    """
    Lista os modelos treinados disponíveis para serem utilizados em previsões.

    Parameters:

        Nenhum parâmetro necessário.

    Returns:

        list : Lista com o nome dos arquivos de modelos disponíveis.
    """

    logger.info(
        "---------------------------------------------------------------------------------------------------"
    )
    logger.info("Listando modelos disponíveis para predição.")

    model_list = mr.list_registered_models()

    logger.debug(f"Retornando a lista de arquivos existentes: {model_list}")

    return model_list


@router.post("/predict")
@PREDICT_REQUEST_TIME.time()
def predict(
    model_name: Annotated[str | None, Body()],
    model_version: Annotated[int | None, Body()],
    data: Annotated[list | None, Body()],
):
    logger.info(
        "---------------------------------------------------------------------------------------------------"
    )
    logger.info(
        f"Iniciando previsão utilizando o modelo {model_name} versão {model_version}"
    )
    PREDICT_COUNT.inc()

    return mr.predict(model_name=model_name, version=model_version, data=data).tolist()
