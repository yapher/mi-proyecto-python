"""
Parser de avisos de paradas.
Módulo reutilizable para extraer datos de archivos de texto con formato de paradas.
"""
import re
import os
from collections import Counter
from datetime import datetime
from flask import current_app

def parse_date_to_dt(s):
    """Intenta convertir s a datetime. Acepta: DD.MM.YYYY, DD/MM/YYYY, YYYY-MM-DD"""
    if not s:
        return None
    s = s.strip().replace('\ufeff', '').strip()
    fmts = ('%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d')
    for fmt in fmts:
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            pass
    m = re.search(r'(\d{1,2}[./]\d{1,2}[./]\d{4})', s)
    if m:
        candidate = m.group(1)
        for fmt in ('%d.%m.%Y', '%d/%m/%Y'):
            try:
                return datetime.strptime(candidate, fmt)
            except Exception:
                pass
    return None

def parsear_avisos_desde_texto(texto):
    """Parser robusto para el formato de avisos de paradas."""
    avisos = []
    lineas = texto.splitlines()
    inicio_datos = 0
    for i, linea in enumerate(lineas):
        if re.search(r'\bCl\.?\b', linea, re.IGNORECASE) and re.search(r'\bAviso\b', linea, re.IGNORECASE):
            inicio_datos = i + 2
            break

    for linea in lineas[inicio_datos:]:
        if not linea or not linea.strip() or set(linea.strip()) <= set('- ') or not linea.strip().startswith('|'):
            continue
        
        partes = linea.split('|')
        if len(partes) < 3:
            continue
            
        aviso_token = partes[2].strip() if len(partes) > 2 else ''
        if not re.search(r'\d', aviso_token):
            continue
            
        def g(i):
            return partes[i].strip() if i < len(partes) else ''
            
        avisos.append({
            'Cl': g(1).replace('X', '').strip(),
            'Aviso': g(2),
            'Fecha': g(3),
            'Descripcion': g(4),
            'Equipo': g(5),
            'Ubicac_tecnica': g(6),
            'DurParada': g(7),
            'Aut_aviso': g(8),
            'Por': g(9),
            'Orden': g(10),
            'Fin_desead': g(11),
            'Texto_codigo': g(12)
        })
    return avisos

def parsear_avisos_default():
    """Carga y parsea el archivo de avisos por defecto."""
    ruta_archivo = os.path.join(current_app.static_folder, 'modelos', 'avisos.txt')
    try:
        with open(ruta_archivo, 'r', encoding='utf-8-sig') as f:
            return parsear_avisos_desde_texto(f.read())
    except Exception as e:
        print(f"Error al leer archivo por defecto: {e}")
        return []

def obtener_columnas():
    """Retorna lista de columnas disponibles para filtrar."""
    return [
        {'key': 'Cl', 'nombre': 'Clase'}, {'key': 'Aviso', 'nombre': 'Aviso'},
        {'key': 'Fecha', 'nombre': 'Fecha'}, {'key': 'Descripcion', 'nombre': 'Descripción'},
        {'key': 'Equipo', 'nombre': 'Equipo'}, {'key': 'Ubicac_tecnica', 'nombre': 'Ubicación Técnica'},
        {'key': 'DurParada', 'nombre': 'Duración Parada'}, {'key': 'Aut_aviso', 'nombre': 'Autor Aviso'},
        {'key': 'Por', 'nombre': 'Por'}, {'key': 'Orden', 'nombre': 'Orden'},
        {'key': 'Fin_desead', 'nombre': 'Fin Deseado'}, {'key': 'Texto_codigo', 'nombre': 'Texto Código'}
    ]