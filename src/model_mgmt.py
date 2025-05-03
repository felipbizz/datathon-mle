from mlflow.tracking import MlflowClient
import argparse

client = MlflowClient("http://127.0.0.1:5000")

def purge_registered_models():
    """
    Remove all registered models from the MLflow tracking server.
    """
    # List all registered models
    print("Removendo todos os modelos registrados...")
    for rm in client.search_registered_models():
        client.delete_registered_model(name=rm.name)
        print(f"Modelo {rm.name} removido com sucesso.")

def list_registered_models():
    """
    List all registered models from the MLflow tracking server.
    """
    # List all registered models
    print("Listando todos os modelos registrados...")
    for rm in client.search_registered_models():
        print(f"Modelo: {rm.name}, Versão: {rm.latest_versions[0].version}, Status: {rm.latest_versions[0].current_stage}")
    print("Modelos registrados listados com sucesso.")

def main(action):

    if "list_registered_models" in action:
        list_registered_models()
    if "purge_registered_models" in action:
        purge_registered_models()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--action",
        nargs="+",
        default=[
            "list_registered_models",
            "purge_registered_models",
        ],
    )
    args = parser.parse_args()
    main(args.action)