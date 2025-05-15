import yaml

def load_config(filepath: str) -> dict:
    """Загружает конфигурационные параметры из файла по пути filepath"""
    with open(filepath, mode="r", encoding="utf-8") as config:
        try:
            return yaml.safe_load(config)
        except yaml.YAMLError as exception:
            raise f"Error during loading {filepath} - {exception}"