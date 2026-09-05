"""
Modelos SQLAlchemy del proyecto.
Cada modelo representa una tabla en la base de datos.
"""
from core.db_sql import db

# Modelos existentes (no tocar)
from .usuario import Usuario
from .evento import Evento
from .tarea import Tarea

# Nuevos modelos (Fase 1)
from .menu import Menu
from .rubro import Rubro
from .almacen import Almacen
from .ubicacion import Ubicacion
from .tab import Tab
from .estado import Estado
from .repuesto import Repuesto
from .pago import Pago
from .nodo_bloqueo import NodoBloqueo
from .orden_trabajo import OrdenTrabajo

__all__ = [
    'db',
    # Existentes
    'Usuario', 'Evento', 'Tarea',
    # Nuevos
    'Menu', 'Rubro', 'Almacen', 'Ubicacion',
    'Tab', 'Estado', 'Repuesto', 'Pago',
    'NodoBloqueo', 'OrdenTrabajo',
]