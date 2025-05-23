from fastapi import FastAPI, APIRouter
from typing import Any
import os
import importlib
from mle_datathon.utils.logger import set_log


logger = set_log("api_settings")


def include_router_from_module(app: FastAPI, module: Any, module_name: str) -> None:
    logger.info(f"Extraindo atributos do módulo: {module_name}")
    module_attributes: dict = vars(module)

    router_found = False

    for attribute in module_attributes.values():
        if isinstance(attribute, APIRouter):
            router_found = True
            app.include_router(attribute)
            logger.info(f"Rotas carregadas de {module_name} ")

    if not router_found:
        logger.warning(f"Nenhuma rota encontrada no módulo {module_name}")


def detect_routers(app: FastAPI, module_dir: str | None) -> None:
    logger.info(
        "---------------------------------------------------------------------------------------------------"
    )

    if module_dir is None:
        logger.warning("Nenhum diretório de módulos fornecido. Usando o padrão.")
        # Define o diretório padrão
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
