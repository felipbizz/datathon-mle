import argparse
import subprocess
from mle_datathon.logger import set_log
from mle_datathon.model import train, tune
from mle_datathon import ModelRegister
# from mle_datathon.train_model import train

import mlflow
from mlflow.tracking import MlflowClient


client = MlflowClient("http://127.0.0.1:5000")

logger = set_log("main")
mr = ModelRegister(client=client)


def preprocess():
    logger.info('Iniciando preprocess')
    subprocess.run(["python", "src/preprocess_data.py"], check=True)
    logger.info('Finalizou preprocess')

def consolidate():
    logger.info('Iniciando consolidar_dados')
    subprocess.run(["python", "src/consolidar_dados.py"], check=True)
    logger.info('Finalizou consolidar_dados')

def define_target():
    logger.info('Iniciando definir_target')
    subprocess.run(["python", "src/definir_target.py"], check=True)
    logger.info('Finalizou definir_target')

def feature_engineering():
    logger.info('Iniciando feature_engineering')
    subprocess.run(["python", "src/feature_engineering.py"], check=True)
    logger.info('Finalizou feature_engineering')

def train_model():
    logger.info('Iniciando train_model')
    # subprocess.run(["python", "src/train_model.py"], check=True)
    train()
    logger.info('Finalizou train_model')

def tune_model():
    logger.info('Iniciando tune_model')
    tune()
    logger.info('Finalizou tune_model')

def list_registered_models():
    logger.info(f'Modelos Registrados:\n{mr.list_registered_models()}')

def purge_registered_models():
    mr.purge_registered_models()
    logger.info('Modelos registrados removidos com sucesso!')
    


def main(steps):

    # Set up MLflow tracking URI
    mlflow.set_tracking_uri("http://127.0.0.1:5000")


    # Set up MLflow experiment
    mlflow.set_experiment(f"experiment_{steps[0]}") #_{current_datetime}")
    # Enable system metrics logging
    mlflow.enable_system_metrics_logging()

    if "preprocess" in steps:
        preprocess()
    if "consolidate" in steps:
        consolidate()
    if "define_target" in steps:
        define_target()
    if "feature_engineering" in steps:
        feature_engineering()
    if "train_model" in steps:
        train_model()
    if "tune" in steps:
        tune_model()
    if "list_registered_models" in steps:
        list_registered_models()
    if "purge_registered_models" in steps:
        purge_registered_models()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--steps",
        nargs="+",
        default=[
            "preprocess",
            "consolidate",
            "define_target",
            "feature_engineering",
            "train_model",
        ],
    )
    args = parser.parse_args()
    main(args.steps)
