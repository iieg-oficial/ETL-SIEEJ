# core/utils/logger.py
import os
import logging
import sys
from pathlib import Path
from datetime import datetime

from rich.logging import RichHandler


def get_console_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    if os.getenv("AIRFLOW_HOME"):
        formatter = logging.Formatter(
            '%(levelname)s:  %(message)s: %(asctime)s ',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(formatter)
    else:
        rich_formatter = logging.Formatter('%(name)s: %(message)s')
        console = RichHandler(rich_tracebacks=True, show_time=False, show_path=False)
        console.setFormatter(rich_formatter)
    logger.addHandler(console)

    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    # Si ya está configurado, retornar
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Formato
    formatter = logging.Formatter(
        '%(levelname)s:  %(message)s: %(asctime)s ',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler: Rich en local, plain en Airflow
    if os.getenv("AIRFLOW_HOME"):
        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(formatter)
    else:
        rich_formatter = logging.Formatter('%(name)s: %(message)s')
        console = RichHandler(rich_tracebacks=True, show_time=False, show_path=False)
        console.setFormatter(rich_formatter)
    logger.addHandler(console)

    # File handler
    log_dir = Path("logs") / Path(*name.split('.'))
    log_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime('%Y%m%d')
    file = logging.FileHandler(log_dir / f"{date_str}.log", encoding='utf-8')
    file.setFormatter(formatter)
    logger.addHandler(file)

    logger.propagate = False

    return logger
