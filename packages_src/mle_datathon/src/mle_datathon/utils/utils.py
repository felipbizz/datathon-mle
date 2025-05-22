import yaml


def get_abs_path(local_path: str, rel_path: str) -> str:
    """Retorna o caminho absoluto a partir da raiz do projeto."""
    return f"{local_path}/{rel_path}"


def load_config(config_path):
    config_path = f"{config_path}/config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
