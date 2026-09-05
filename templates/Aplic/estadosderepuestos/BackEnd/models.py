"""
Capa de acceso a datos para repuestos.
Refactorizado para usar UniqueFieldStore de core.

Mantiene la misma API pública para no romper imports existentes:
  - leer_repuestos()
  - guardar_repuestos(repuestos)
  - obtener_por_codigo(codigo)
  - crear_repuesto(datos)
  - actualizar_repuesto(codigo_original, nuevos_datos)
  - eliminar_repuesto(codigo)
"""
from core.json_crud import UniqueFieldStore

# ============================================================
# INSTANCIA REUTILIZABLE DEL STORE
# ============================================================
# Configurado con "codigo" como campo único (no "id")
# No auto-incrementa ID porque los repuestos usan "codigo" como identificador
_store = UniqueFieldStore(
    db_path='DataBase/dataRep/REPUESTOS.json',
    unique_field='codigo',
    auto_id=False
)


# ============================================================
# FUNCIONES DE COMPATIBILIDAD (API pública sin cambios)
# ============================================================

def leer_repuestos():
    """Lee todos los repuestos desde el JSON."""
    return _store.cargar()


def guardar_repuestos(repuestos):
    """Guarda la lista completa de repuestos en el JSON."""
    _store.guardar(repuestos)


def obtener_por_codigo(codigo):
    """Busca un repuesto por su código."""
    return _store.buscar_por_unique(codigo)


def crear_repuesto(datos):
    """
    Crea un nuevo repuesto. Retorna (exito, mensaje).
    Valida que no exista otro repuesto con el mismo código.
    """
    # Validar campos obligatorios antes de delegar al store
    codigo = datos.get('codigo')
    if not codigo or str(codigo).strip() == '':
        return False, "El código es obligatorio"
    
    # Usar el store con validación de unicidad
    return _store.crear(datos, skip_unique_check=False)


def actualizar_repuesto(codigo_original, nuevos_datos):
    """
    Actualiza un repuesto existente. Retorna (exito, mensaje).
    Valida que el nuevo código (si cambia) no exista ya.
    """
    return _store.actualizar_por_unique(
        valor_original=codigo_original,
        nuevos_datos=nuevos_datos,
        check_new_unique=True
    )


def eliminar_repuesto(codigo):
    """Elimina un repuesto por código. Retorna (exito, mensaje)."""
    return _store.eliminar_por_unique(codigo)


# ============================================================
# FUNCIONES ADICIONALES (nuevas, usando UniqueFieldStore)
# ============================================================

def existe_codigo(codigo):
    """Verifica si existe un repuesto con el código dado."""
    return _store.existe_por_unique(codigo)


def buscar_repuestos(**criterios):
    """Busca repuestos que cumplan todos los criterios."""
    return _store.buscar(**criterios)


def contar_repuestos():
    """Retorna la cantidad total de repuestos."""
    return _store.contar()