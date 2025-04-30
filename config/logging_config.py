"""
Configuración de logging para el proyecto de alertas alimentarias.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

from config.settings import LOGS_DIR

def configure_logging(name=None, log_file=None, level=logging.INFO):
    """
    Configura el sistema de logging.
    
    Args:
        name (str, optional): Nombre del logger. Si es None, configura el logger raíz.
        log_file (str, optional): Ruta al archivo de log. Si es None, se genera automáticamente.
        level (int, optional): Nivel de logging. Por defecto, INFO.
        
    Returns:
        logging.Logger: Logger configurado.
    """
    # Crear directorio de logs si no existe
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # Determinar nombre del logger
    logger_name = name or "food_alerts"
    
    # Obtener logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    
    # Limpiar handlers existentes para evitar duplicados
    if logger.handlers:
        logger.handlers.clear()
    
    # Determinar nombre del archivo de log
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        module_name = name.split(".")[-1] if name else "main"
        log_file = os.path.join(LOGS_DIR, f"{module_name}_{timestamp}.log")
    
    # Configurar handler para archivo
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Configurar handler para consola
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name):
    """
    Obtiene un logger configurado.
    
    Args:
        name (str): Nombre del logger.
        
    Returns:
        logging.Logger: Logger configurado.
    """
    return configure_logging(name)