"""
core/data_loaders.py
====================
Funciones auxiliares reutilizables para cargar configuraciones jerárquicas.
Extraídas desde estadosderepuestos/helpers.py para ser compartidas por:
  - estadosderepuestos
  - listarepuestos
  - graficosrepuestos
  - (futuras apps que necesiten cargar almacenes/ubicaciones/estados/tabs)

Uso:
    from core.data_loaders import (
        cargar_almacenes, cargar_estados, cargar_ubicaciones,
        cargar_tabs, obtener_nombres_almacenes, extraer_rutas
    )
"""
import json
import os
import re

# ============================================================
# RUTAS DE ARCHIVOS (constantes centralizadas)
# ============================================================
PATHTABS = 'DataBase/tabs.json'
DATA_ALMACENES = 'DataBase/dataRep/almacenes.json'
DATA_ESTADOS = 'DataBase/dataRep/estados.json'
UBI_TEC = 'DataBase/dataRep/ubicacion_tecnica.json'


# ============================================================
# EXTRACCIÓN RECURSIVA DE RUTAS
# ============================================================
def extraer_rutas(data, rutas):
    """
    Función recursiva para extraer todas las rutas jerárquicas
    de un árbol de nodos (almacenes, ubicaciones, etc.).

    Args:
        data: lista o dict con nodos jerárquicos
        rutas: lista acumuladora (se modifica in-place)
    """
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
            or []
        )
        if sub:
            extraer_rutas(sub, rutas)


# ============================================================
# CARGA DE UBICACIONES TÉCNICAS
# ============================================================
def cargar_ubicaciones():
    """
    Carga todas las ubicaciones técnicas desde el JSON.
    Retorna una lista de rutas jerárquicas únicas (sin duplicados).
    """
    if not os.path.exists(UBI_TEC):
        print(f"[WARN] No existe el archivo de ubicaciones: {UBI_TEC}")
        return []
    try:
        with open(UBI_TEC, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[ERROR] Al leer {UBI_TEC}: {e}")
        return []

    rutas = []
    extraer_rutas(data, rutas)

    # Eliminar duplicados manteniendo orden
    seen = set()
    rutas_unicas = []
    for r in rutas:
        if r not in seen:
            rutas_unicas.append(r)
            seen.add(r)

    print(f"[DEBUG] cargadas {len(rutas_unicas)} ubicaciones técnicas")
    return rutas_unicas


# ============================================================
# CARGA DE ESTADOS
# ============================================================
def cargar_estados():
    """
    Carga la lista de estados desde el JSON.
    Retorna una lista de dicts con 'nombre' y 'emoji'.
    """
    if not os.path.exists(DATA_ESTADOS):
        print(f"[WARN] No existe {DATA_ESTADOS}")
        return []
    try:
        with open(DATA_ESTADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] leyendo estados: {e}")
        return []


# ============================================================
# CARGA DE ALMACENES
# ============================================================
def cargar_almacenes():
    """
    Carga la estructura jerárquica de almacenes desde el JSON.
    Retorna una lista de dicts con 'nombre', 'emoji', 'subcrear_almacenes', etc.
    """
    if not os.path.exists(DATA_ALMACENES):
        print(f"[WARN] No existe {DATA_ALMACENES}")
        return []
    try:
        with open(DATA_ALMACENES, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] leyendo almacenes: {e}")
        return []


# ============================================================
# EXTRACCIÓN DE NOMBRES DE ALMACENES
# ============================================================
def obtener_nombres_almacenes(almacenes):
    """
    Extrae recursivamente todos los nombres (ruta_jerarquia o nombre)
    de almacenes para usar en selects.
    """
    nombres = []
    for almacen in (almacenes or []):
        nombre = almacen.get('ruta_jerarquia') or almacen.get('nombre')
        if nombre:
            nombres.append(nombre)
        sub = (
            almacen.get('subcrear_almacenes')
            or almacen.get('sububicaciones')
            or almacen.get('subalmacenes')
            or []
        )
        if sub:
            nombres.extend(obtener_nombres_almacenes(sub))
    return nombres


# ============================================================
# CARGA DE TABS (PESTAÑAS)
# ============================================================
def cargar_tabs():
    """
    Carga y sanitiza las pestañas desde el JSON.
    Agrega un campo 'sanitized_id' a cada tab para usar en HTML.
    """
    if not os.path.exists(PATHTABS):
        print(f"[WARN] No existe {PATHTABS}")
        return []
    try:
        with open(PATHTABS, "r", encoding="utf-8") as f:
            tabs = json.load(f)
    except Exception as e:
        print(f"[ERROR] leyendo tabs: {e}")
        return []

    # Sanitizar los IDs de los tabs para que sean válidos en HTML
    for tab in tabs:
        original_id = str(tab.get('id', ''))
        sanitized_id = re.sub(r'\s+', '-', original_id.strip())
        sanitized_id = re.sub(r'[^\w\-]', '', sanitized_id)
        tab['sanitized_id'] = sanitized_id

    return tabs