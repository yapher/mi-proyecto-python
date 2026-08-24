"""
Capa de acceso a datos para repuestos.
Solo se preocupa por leer y guardar en REPUESTOS.json.
"""
import json
import os

PATHREPUESTOS = 'DataBase/dataRep/REPUESTOS.json'

def leer_repuestos():
    """Lee todos los repuestos desde el JSON."""
    if not os.path.exists(PATHREPUESTOS):
        return []
    with open(PATHREPUESTOS, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def guardar_repuestos(repuestos):
    """Guarda la lista completa de repuestos en el JSON."""
    with open(PATHREPUESTOS, 'w', encoding='utf-8') as f:
        json.dump(repuestos, f, indent=4, ensure_ascii=False)

def obtener_por_codigo(codigo):
    """Busca un repuesto por su código."""
    repuestos = leer_repuestos()
    return next((r for r in repuestos if str(r.get('codigo')) == str(codigo)), None)

def crear_repuesto(datos):
    """Crea un nuevo repuesto. Retorna (exito, mensaje)."""
    if obtener_por_codigo(datos['codigo']):
        return False, "Ya existe un repuesto con el mismo código."
    repuestos = leer_repuestos()
    repuestos.append(datos)
    guardar_repuestos(repuestos)
    return True, "Repuesto creado correctamente."

def actualizar_repuesto(codigo_original, nuevos_datos):
    """Actualiza un repuesto existente. Retorna (exito, mensaje)."""
    repuestos = leer_repuestos()
    for i, r in enumerate(repuestos):
        if str(r.get('codigo')) == str(codigo_original):
            if nuevos_datos['codigo'] != codigo_original and obtener_por_codigo(nuevos_datos['codigo']):
                return False, "El nuevo código ya existe."
            repuestos[i].update(nuevos_datos)
            guardar_repuestos(repuestos)
            return True, "Repuesto actualizado correctamente."
    return False, "Repuesto no encontrado."

def eliminar_repuesto(codigo):
    """Elimina un repuesto por código. Retorna (exito, mensaje)."""
    repuestos = leer_repuestos()
    filtrados = [r for r in repuestos if str(r.get('codigo')) != str(codigo)]
    if len(filtrados) < len(repuestos):
        guardar_repuestos(filtrados)
        return True, "Repuesto eliminado correctamente."
    return False, "Repuesto no encontrado."