import argparse
from src.log_config import logging

import subprocess

def preprocess():
    subprocess.run(["python", "src/preprocess_data.py"], check=True)

def consolidate():
    subprocess.run(["python", "src/consolidar_dados.py"], check=True)

def define_target():
    subprocess.run(["python", "src/definir_target.py"], check=True)

def feature_engineering():
    subprocess.run(["python", "src/feature_engineering.py"], check=True)

def train_model():
    subprocess.run(["python", "src/train_model.py"], check=True)

def main(steps):
    if 'preprocess' in steps:
        preprocess()
    if 'consolidate' in steps:
        consolidate()
    if 'define_target' in steps:
        define_target()
    if 'feature_engineering' in steps:
        feature_engineering()
    if 'train_model' in steps:
        train_model()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--steps', nargs='+', default=['preprocess', 'consolidate', 'define_target', 'feature_engineering', 'train_model'])
    args = parser.parse_args()
    main(args.steps)
