# templates/Aplic/estadosderepuestos/BackEnd/models.py
"""
Capa de acceso a datos para repuestos.
AHORA USA core/repuestos.py como punto único de acceso.
Mantiene la misma API pública para no romper imports existentes.
"""
# ✅ IMPORTAR TODO DESDE core/repuestos.py
from core.repuestos import (
    cargar_todos_repuestos,
    guardar_todos_repuestos,
    obtener_repuesto_por_codigo,
    crear_repuesto as _core_crear_repuesto,
    actualizar_repuesto as _core_actualizar_repuesto,
    eliminar_repuesto as _core_eliminar_repuesto,
    existe_codigo,
)

# ============================================================
# FUNCIONES DE COMPATIBILIDAD (API pública sin cambios)
# ============================================================

def leer_repuestos():
    """Lee todos los repuestos desde SQL."""
    return cargar_todos_repuestos()


def guardar_repuestos(repuestos):
    """Guarda la lista completa de repuestos en SQL."""
    guardar_todos_repuestos(repuestos)


def obtener_por_codigo(codigo):
    """Busca un repuesto por su código."""
    return obtener_repuesto_por_codigo(codigo)


def crear_repuesto(datos):
    """Crea un nuevo repuesto. Retorna (exito, mensaje)."""
    return _core_crear_repuesto(datos)


def actualizar_repuesto(codigo_original, nuevos_datos):
    """Actualiza un repuesto existente. Retorna (exito, mensaje)."""
    return _core_actualizar_repuesto(codigo_original, nuevos_datos)


def eliminar_repuesto(codigo):
    """Elimina un repuesto por código. Retorna (exito, mensaje)."""
    return _core_eliminar_repuesto(codigo)


def buscar_repuestos(**criterios):
    """Busca repuestos que cumplan todos los criterios."""
    from core.db_sql_store import repuesto_store
    return repuesto_store.buscar(**criterios)


def contar_repuestos():
    """Retorna la cantidad total de repuestos."""
    from core.db_sql_store import repuesto_store
    return repuesto_store.contar()