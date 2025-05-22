import os
import logging
from logging.handlers import TimedRotatingFileHandler


def set_log(
    logfile: str,
    format: str = None,
    level: int = logging.ERROR,
    rotation: str = "d",
    backupCount: int = 30,
    log_location: str = None,
):
    logger = logging.getLogger(logfile)

    if format is None:
        format = os.getenv(
            "DEFAULT_LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    default_log_level = os.getenv("DEFAULT_LOG_LEVEL", "INFO")

    logging.basicConfig(level=default_log_level, format=format)

    if log_location is None:
        log_location = os.getenv("DEFAULT_LOG_LOCATION", "logs")

    log_location = os.path.join(log_location, logfile)

    if not os.path.exists(log_location):
        os.makedirs(f"{log_location}")

    if rotation not in ["s", "m", "h", "d", "midnight"]:
        rotation = "midnight"
        logger.error(
            "Período de rotação inválido: %s. Padronizando para rotação diária à meia-noite"
            % rotation
        )

    logger.setLevel(level)
    formatter = logging.Formatter(format)

    handler = TimedRotatingFileHandler(
        f"{log_location}/{logfile}.log", when=rotation, backupCount=backupCount
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
