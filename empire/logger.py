import yaml
from pathlib import Path
import logging
import logging.config
from empire.core.config import EmpireRunConfiguration


def get_empire_logger(run_config: EmpireRunConfiguration) -> logging.Logger:
    """
    Returns a logger handle configured according to 'config/logging.yaml' 
    and ensures that logs are written to the specified results folder.

    Assumes that the logger named "Empire" exists in the logging configuration.

    :param run_config: Empire run configuration object containing run details.
    :raises: FileNotFoundError, YAMLError
    :return: Configured logger.
    """

    config_path = Path.cwd() / "config/logging.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Logging configuration file not found at {config_path}")

    with open(config_path, "r", encoding="utf-8") as file:
        try:
            log_config = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise RuntimeError(f"Error parsing logging configuration: {e}")

    if "empire" not in log_config.get("loggers", {}):
        raise ValueError("Logger named 'empire' not found in the logging configuration.")

    log_config["handlers"]["file_handler"]["filename"] = run_config.results_path / "logs.txt"
    logging.config.dictConfig(log_config)
    
    return logging.getLogger("empire")
