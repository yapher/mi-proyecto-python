"""
COMPATIBILIDAD: Este archivo mantiene las importaciones para otras aplicaciones.
La lógica real ahora está en: core/data_loaders.py

Las funciones se re-exportan desde core para no romper imports existentes.
"""
# Re-exportar TODO desde core.data_loaders para compatibilidad
from core.data_loaders import (  # noqa: F401
    cargar_tabs,
    cargar_almacenes,
    obtener_nombres_almacenes,
    cargar_estados,
    cargar_ubicaciones,
    extraer_rutas,
    PATHTABS,
    DATA_ALMACENES,
    DATA_ESTADOS,
    UBI_TEC,
)

# Alias legacy: algunos módulos viejos usaban DATA_FILE en lugar de DATA_ALMACENES
DATA_FILE = DATA_ALMACENES