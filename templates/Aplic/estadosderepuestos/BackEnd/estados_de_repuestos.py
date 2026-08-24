"""
COMPATIBILIDAD: Este archivo mantiene las importaciones para otras aplicaciones.
La lógica real está en los módulos modulares: helpers.py, models.py, services.py, routes.py
"""

# Re-exportar desde helpers para compatibilidad con otras aplicaciones
from .helpers import (
    cargar_tabs,
    cargar_almacenes,
    obtener_nombres_almacenes,
    cargar_estados,
    cargar_ubicaciones
)

# Re-exportar desde models para compatibilidad
from .models import (
    leer_repuestos,
    guardar_repuestos
)

# Re-exportar desde routes para compatibilidad
from .routes import estadoRep_bp

# El Blueprint ya está registrado automáticamente por blueprint_registry.py