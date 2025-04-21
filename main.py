import argparse
import subprocess
from src.log_config import logging


def preprocess():
    logging.info('Iniciando preprocess')
    subprocess.run(["python", "src/preprocess_data.py"], check=True)
    logging.info('Finalizou preprocess')

def consolidate():
    logging.info('Iniciando consolidar_dados')
    subprocess.run(["python", "src/consolidar_dados.py"], check=True)
    logging.info('Finalizou consolidar_dados')

def define_target():
    logging.info('Iniciando definir_target')
    subprocess.run(["python", "src/definir_target.py"], check=True)
    logging.info('Finalizou definir_target')

def feature_engineering():
    logging.info('Iniciando feature_engineering')
    subprocess.run(["python", "src/feature_engineering.py"], check=True)
    logging.info('Finalizou feature_engineering')

def train_model():
    logging.info('Iniciando train_model')
    subprocess.run(["python", "src/train_model.py"], check=True)
    logging.info('Finalizou train_model')

def main(steps):
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
