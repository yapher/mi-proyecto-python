"""
core/logging_config.py
======================
Configuración centralizada de logging para toda la aplicación.
Reemplaza los print() dispersos por un sistema profesional.

Uso:
    from core.logging_config import get_logger
    logger = get_logger(__name__)
    logger.info("Mensaje", extra={"dato": "valor"})
"""
import logging
import sys
from pathlib import Path

# Crear directorio de logs si no existe
LOG_DIR = Path(__file__).parent.parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# Formato profesional
LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def setup_logging(app_name="Empresa", level=logging.INFO):
    """
    Configura el logging global de la aplicación.
    Llama una sola vez al inicio de app.py.
    """
    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Limpiar handlers existentes (evita duplicados en reload)
    root_logger.handlers.clear()
    
    # Handler para consola (desarrollo)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    root_logger.addHandler(console_handler)
    
    # Handler para archivo (producción/debug)
    file_handler = logging.FileHandler(LOG_DIR / f'{app_name}.log', encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    root_logger.addHandler(file_handler)
    
    # Handler separado para errores críticos
    error_handler = logging.FileHandler(LOG_DIR / f'{app_name}_error.log', encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    root_logger.addHandler(error_handler)
    
    # Reducir ruido de librerías externas
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('flask_sqlalchemy').setLevel(logging.WARNING)
    
    root_logger.info(f"✅ Logging configurado: {app_name} (nivel: {logging.getLevelName(level)})")

def get_logger(name):
    """
    Obtiene un logger para un módulo específico.
    Uso: logger = get_logger(__name__)
    """
    return logging.getLogger(name)