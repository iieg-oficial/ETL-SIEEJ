# core/utils/logger.py
import logging
import sys
from pathlib import Path
from datetime import datetime


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    
    # Si ya está configurado, retornar
    if logger.handlers: 
        return logger
    
    logger.setLevel(logging.INFO) 
    
    # Formato
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    logger.addHandler(console)
    
    # File handler
    pipeline_name = name.split('.')[0]
    date_str = datetime.now().strftime('%Y%m%d')
    
    log_dir = Path("logs") / pipeline_name
    log_dir.mkdir(parents=True, exist_ok=True)
    
    file = logging.FileHandler(log_dir / f"{date_str}.log", encoding='utf-8')
    file.setFormatter(formatter)
    logger.addHandler(file)
    
    logger.propagate = False
    
    return logger