import argparse
import os
from mle_datathon.utils import set_log
from mle_datathon.model import train, tune, ModelRegistry
from mle_datathon.data_processing import execute_preprocess, feature_engineering


import mlflow

tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")

logger = set_log("main")
mr = ModelRegistry(tracking_uri)


def list_registered_models():
    logger.info(f"Modelos Registrados:\n{mr.list_registered_models()}")


def purge_registered_models():
    mr.purge_registered_models()
    logger.info("Modelos registrados removidos com sucesso!")


def run_steps(steps):
    """
    Executa os passos especificados no pipeline.
    """

    if "full_pipeline" in steps:
        logger.info("Iniciando pipeline completo")
        execute_preprocess()
        feature_engineering()
        train()
        return

    if "preprocess" in steps:
        logger.info("Iniciando preprocessamento")
        execute_preprocess()
    if "feature_engineering" in steps:
        logger.info("Iniciando engenharia de features")
        feature_engineering()
    if "train_model" in steps:
        logger.info("Iniciando treinamento do modelo")
        train()
    if "tune" in steps:
        logger.info("Iniciando ajuste do modelo")
        tune()
    if "list_registered_models" in steps:
        list_registered_models()


def main(steps):
    # Set up MLflow tracking URI
    mlflow.set_tracking_uri(tracking_uri)

    experiment_name = f"experiment_{steps[0]}"
    logger.info(f"Iniciando experimento: {experiment_name}")

    # Set up MLflow experiment
    mlflow.set_experiment(experiment_name)
    # Enable system metrics logging
    mlflow.enable_system_metrics_logging()

    run_steps(steps)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--steps",
        nargs="+",
        default=[
            "full_pipeline",
        ],
    )
    args = parser.parse_args()
    main(args.steps)
