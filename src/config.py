import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


def get_abs_path(rel_path):
    """Retorna o caminho absoluto a partir da raiz do projeto."""
    BASE_DIR = Path(__file__).resolve().parent.parent
    return str(BASE_DIR / rel_path)


def load_config(config_path=CONFIG_PATH):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
