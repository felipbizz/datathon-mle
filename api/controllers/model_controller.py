from fastapi import APIRouter, Body
from typing import Annotated, Any
from mle_utils.logger import set_log

import os

from prometheus_client import Summary, Counter

logger = set_log("model_controller", level=10)

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

    path = "ml_models"

    logger.info(f"Obtendo lista de arquivos em {path}")
    model_list = os.listdir(path)

    logger.debug(f"Retornando a lista de arquivos existentes: {model_list}")

    return model_list


@router.get("/tune")
@TUNE_REQUEST_TIME.time()
def tune():
    ## TBD

    return 


@router.post("/train")
@TRAIN_REQUEST_TIME.time()
def train(best_config: Annotated[dict | None, Body()]) -> str:
    ## TBD
    return 


@router.post("/predict")
@PREDICT_REQUEST_TIME.time()
def predict(model_file: Annotated[str | None, Body()], stock_option: str = "VALE3.SA"):
    logger.info(
        "---------------------------------------------------------------------------------------------------"
    )
    logger.info(f"Iniciando previsão utilizando o modelo {model_file}")
    PREDICT_COUNT.inc()
    return {"message": "return predicion : TBD"}
