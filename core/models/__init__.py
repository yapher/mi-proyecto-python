"""
Modelos SQLAlchemy del proyecto.
Cada modelo representa una tabla en la base de datos.
"""
from core.db_sql import db

# Importar todos los modelos para que se registren
from .tarea import Tarea
from .evento import Evento
from .usuario import Usuario

__all__ = ['Tarea', 'Evento', 'Usuario', 'db']