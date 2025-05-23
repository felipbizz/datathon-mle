from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from mle_datathon.api_settings import detect_routers
from mle_datathon.utils import set_log

logger = set_log("api", level=10)
logger.info(
    "---------------------------------------------------------------------------------------------------"
)
logger.info("Iniciando API")
app = FastAPI()

logger.info("Adicionando rotas.")
detect_routers(app, module_dir="controllers")

logger.info("Configurando o instrumentador de métricas do cliente do Prometheus.")
metrics_app = make_asgi_app()

logger.info(
    "Definindo o endpoint de coleta de métricas a ser usado pelo servidor do Prometheus."
)
app.mount("/metrics", metrics_app)

logger.info("Realizando configuração inicial da API")

logger.info("Adicionando middleware para CORS")
origins = ["*"]
methods = ["*"]
headers = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=methods,
    allow_headers=headers,
    allow_credentials=True,
)
