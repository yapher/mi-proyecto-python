"""
core/data_loaders.py — VERSIÓN SQL
Funciones auxiliares reutilizables para cargar configuraciones.
Ahora usa stores SQL en lugar de leer JSON directamente.
"""
from core.db_sql_store import (
    tab_store, estado_store, almacen_store, ubicacion_store
)


# ============================================================
# CONSTANTES LEGACY (para compatibilidad con imports antiguos)
# ============================================================
PATHTABS = 'DataBase/tabs.json'
DATA_ALMACENES = 'DataBase/dataRep/almacenes.json'
DATA_ESTADOS = 'DataBase/dataRep/estados.json'
UBI_TEC = 'DataBase/dataRep/ubicacion_tecnica.json'


# ============================================================
# EXTRACCIÓN RECURSIVA DE RUTAS
# ============================================================
def extraer_rutas(data, rutas):
    """Función recursiva para extraer rutas jerárquicas."""
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                ruta = item.get("ruta_jerarquia")
                if ruta:
                    rutas.append(ruta)
                sub = (
                    item.get("sububicaciones")
                    or item.get("subcrear_almacenes")
                    or item.get("subalmacenes")
                    or item.get("submenues")
                    or []
                )
                if sub:
                    extraer_rutas(sub, rutas)
    elif isinstance(data, dict):
        ruta = data.get("ruta_jerarquia")
        if ruta:
            rutas.append(ruta)
        sub = (
            data.get("sububicaciones")
            or data.get("subcrear_almacenes")
            or data.get("subalmacenes")
            or data.get("submenues")
            or []
        )
        if sub:
            extraer_rutas(sub, rutas)


# ============================================================
# CARGA DE UBICACIONES TÉCNICAS (desde SQL)
# ============================================================
def cargar_ubicaciones():
    """Carga todas las ubicaciones técnicas desde SQL."""
    arbol = ubicacion_store.cargar_arbol()
    rutas = []
    extraer_rutas(arbol, rutas)

    # Eliminar duplicados manteniendo orden
    seen = set()
    rutas_unicas = []
    for r in rutas:
        if r not in seen:
            rutas_unicas.append(r)
            seen.add(r)
    return rutas_unicas


# ============================================================
# CARGA DE ESTADOS (desde SQL)
# ============================================================
def cargar_estados():
    """Carga la lista de estados desde SQL."""
    return estado_store.cargar()


# ============================================================
# CARGA DE ALMACENES (desde SQL)
# ============================================================
def cargar_almacenes():
    """Carga la estructura jerárquica de almacenes desde SQL."""
    return almacen_store.cargar_arbol()


# ============================================================
# EXTRACCIÓN DE NOMBRES DE ALMACENES
# ============================================================
def obtener_nombres_almacenes(almacenes):
    """Extrae recursivamente todos los nombres de almacenes."""
    nombres = []
    for almacen in (almacenes or []):
        nombre = almacen.get('ruta_jerarquia') or almacen.get('nombre')
        if nombre:
            nombres.append(nombre)
        sub = (
            almacen.get('subcrear_almacenes')
            or almacen.get('sububicaciones')
            or almacen.get('subalmacenes')
            or almacen.get('submenues')
            or []
        )
        if sub:
            nombres.extend(obtener_nombres_almacenes(sub))
    return nombres


# ============================================================
# CARGA DE TABS (desde SQL)
# ============================================================
def cargar_tabs():
    """Carga las pestañas desde SQL."""
    return tab_store.cargar()