"""
Capa de acceso a datos para repuestos.
AHORA USA SQL en lugar de JSON.
Mantiene la misma API pública para no romper imports existentes:
- leer_repuestos()
- guardar_repuestos(repuestos)
- obtener_por_codigo(codigo)
- crear_repuesto(datos)
- actualizar_repuesto(codigo_original, nuevos_datos)
- eliminar_repuesto(codigo)
"""
from core.db_sql_store import repuesto_store


# ============================================================
# FUNCIONES DE COMPATIBILIDAD (API pública sin cambios)
# ============================================================
def leer_repuestos():
    """Lee todos los repuestos desde SQL."""
    return repuesto_store.cargar()


def guardar_repuestos(repuestos):
    """Guarda la lista completa de repuestos en SQL (reemplaza todos)."""
    repuesto_store.guardar(repuestos)


def obtener_por_codigo(codigo):
    """Busca un repuesto por su código."""
    return repuesto_store.buscar_por_codigo(codigo)


def crear_repuesto(datos):
    """
    Crea un nuevo repuesto. Retorna (exito, mensaje).
    Valida que no exista otro repuesto con el mismo código.
    """
    codigo = datos.get('codigo')
    if not codigo or str(codigo).strip() == '':
        return False, "El código es obligatorio"
    return repuesto_store.crear(datos, skip_unique_check=False)


def actualizar_repuesto(codigo_original, nuevos_datos):
    """
    Actualiza un repuesto existente. Retorna (exito, mensaje).
    Valida que el nuevo código (si cambia) no exista ya.
    """
    return repuesto_store.actualizar_por_codigo(
        codigo_original=codigo_original,
        nuevos_datos=nuevos_datos,
        check_new_unique=True
    )


def eliminar_repuesto(codigo):
    """Elimina un repuesto por código. Retorna (exito, mensaje)."""
    return repuesto_store.eliminar_por_codigo(codigo)


# ============================================================
# FUNCIONES ADICIONALES
# ============================================================
def existe_codigo(codigo):
    """Verifica si existe un repuesto con el código dado."""
    return repuesto_store.existe_codigo(codigo)


def buscar_repuestos(**criterios):
    """Busca repuestos que cumplan todos los criterios."""
    return repuesto_store.buscar(**criterios)


def contar_repuestos():
    """Retorna la cantidad total de repuestos."""
    return repuesto_store.contar()