"""
Funciones auxiliares reutilizables para cargar configuraciones.
Módulo modular que puede ser importado por cualquier aplicación.
"""
import json
import os
import re

PATHTABS = 'DataBase/tabs.json'
DATA_FILE = 'DataBase/dataRep/almacenes.json'
DATA_ESTADOS = 'DataBase/dataRep/estados.json'
UBI_TEC = 'DataBase/dataRep/ubicacion_tecnica.json'

def extraer_rutas(data, rutas):
    """Función recursiva para extraer todas las rutas jerárquicas."""
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                ruta = item.get("ruta_jerarquia")
                if ruta:
                    rutas.append(ruta)
                sub = item.get("sububicaciones") or item.get("subcrear_almacenes") or item.get("subalmacenes") or []
                if sub:
                    extraer_rutas(sub, rutas)
    elif isinstance(data, dict):
        ruta = data.get("ruta_jerarquia")
        if ruta:
            rutas.append(ruta)
        sub = data.get("sububicaciones") or data.get("subcrear_almacenes") or data.get("subalmacenes") or []
        if sub:
            extraer_rutas(sub, rutas)

def cargar_ubicaciones():
    """Carga todas las ubicaciones técnicas desde el JSON."""
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

def cargar_estados():
    """Carga la lista de estados desde el JSON."""
    if not os.path.exists(DATA_ESTADOS):
        print(f"[WARN] No existe {DATA_ESTADOS}")
        return []
    try:
        with open(DATA_ESTADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] leyendo estados: {e}")
        return []

def cargar_almacenes():
    """Carga la estructura de almacenes desde el JSON."""
    if not os.path.exists(DATA_FILE):
        print(f"[WARN] No existe {DATA_FILE}")
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] leyendo almacenes: {e}")
        return []

def obtener_nombres_almacenes(almacenes):
    """Extrae recursivamente todos los nombres de almacenes."""
    nombres = []
    for almacen in (almacenes or []):
        nombre = almacen.get('ruta_jerarquia') or almacen.get('nombre')
        if nombre:
            nombres.append(nombre)
        sub = almacen.get('subcrear_almacenes') or almacen.get('sububicaciones') or almacen.get('subalmacenes') or []
        if sub:
            nombres.extend(obtener_nombres_almacenes(sub))
    return nombres

def cargar_tabs():
    """Carga y sanitiza las pestañas desde el JSON."""
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