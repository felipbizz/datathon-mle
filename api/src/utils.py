import importlib
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from fastapi import FastAPI, APIRouter
from typing import Any

def set_log(
    logfile: str,
    format: str = None,
    level: int = logging.DEBUG,
    rotation: str = "d",
    backupCount: int = 30,
    log_location: str = None,
):
    logger = logging.getLogger(logfile)

    if format is None:
        format = os.getenv(
            "DEFAULT_LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    default_log_level = os.getenv("DEFAULT_LOG_LEVEL", "INFO")

    logging.basicConfig(level=default_log_level, format=format)

    if log_location is None:
        log_location = os.getenv("DEFAULT_LOG_LOCATION", "logs")

    log_location = os.path.join(log_location, logfile)

    if not os.path.exists(log_location):
        os.makedirs(f"{log_location}")

    if rotation not in ["s", "m", "h", "d", "midnight"]:
        rotation = "midnight"
        logger.error(
            "Período de rotação inválido: %s. Padronizando para rotação diária à meia-noite"
            % rotation
        )

    logger.setLevel(level)
    formatter = logging.Formatter(format)

    handler = TimedRotatingFileHandler(
        f"{log_location}/{logfile}.log", when=rotation, backupCount=backupCount
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


logger = set_log("setup")


def include_router_from_module(app: FastAPI, module: Any, module_name: str) -> None:
    logger.info(f"Extraindo atributos do módulo {module_name}")
    module_attributes: dict = vars(module)

    router_found = False

    for attribute in module_attributes.values():
        if isinstance(attribute, APIRouter):
            router_found = True
            app.include_router(attribute)
            logger.info(f"Rotas carregadas de {module_name} ")

    if not router_found:
        logger.warning(f"Nenhuma rota encontrada no módulo {module_name}")


def detect_routers(app: FastAPI) -> None:
    logger.info(
        "---------------------------------------------------------------------------------------------------"
    )
    module_dir: str = "controllers"

    logger.info(f"Buscando rotas em {module_dir}")
    module_files: list = [f for f in os.listdir(module_dir) if f.endswith(".py")]
    logger.debug(f"Módulos encontrados: {module_files}")

    for module_file in module_files:
        logger.info(f"Carregando rotas de : {module_file}")

        module_name: str = module_file.replace(".py", "")
        package_path: str = module_dir.replace("/", ".")

        module: Any = importlib.import_module("." + module_name, package=package_path)

        include_router_from_module(app, module, module_name)