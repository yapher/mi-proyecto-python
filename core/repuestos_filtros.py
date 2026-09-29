# core/repuestos_filtros.py
"""
Funciones comunes para filtrado, normalización y lectura de repuestos.
"""

import json

from flask import request


def normalizar_texto(valor):
    if valor is None:
        return ''
    return str(valor).strip()


def _texto_de_elemento_ruta(elemento):
    if isinstance(elemento, dict):
        for clave in ('ruta_jerarquia', 'ruta', 'nombre', 'value'):
            if clave in elemento:
                return normalizar_texto(elemento[clave])
        return ''

    return normalizar_texto(elemento)


def parsear_lista_rutas(valor):
    """
    Normaliza ruta_jerarquia desde distintos formatos posibles:
    - list
    - tuple
    - set
    - dict
    - string
    - string JSON "[...]"
    """
    if valor is None:
        return []

    if isinstance(valor, (list, tuple, set)):
        resultado = []
        for item in valor:
            resultado.extend(parsear_lista_rutas(item))
        return [x for x in resultado if x]

    if isinstance(valor, dict):
        for clave in ('ruta_jerarquia', 'rutas', 'ruta', 'nombre', 'value'):
            if clave in valor:
                return parsear_lista_rutas(valor[clave])

        resultado = []
        for v in valor.values():
            resultado.extend(parsear_lista_rutas(v))
        return [x for x in resultado if x]

    texto = normalizar_texto(valor)
    if not texto:
        return []

    if texto.startswith('['):
        try:
            data = json.loads(texto)
            if isinstance(data, list):
                return parsear_lista_rutas(data)
        except Exception:
            pass

    if texto.startswith('{'):
        try:
            data = json.loads(texto)
            return parsear_lista_rutas(data)
        except Exception:
            pass

    if '\n' in texto:
        partes = texto.splitlines()
    elif '\r' in texto:
        partes = texto.split('\r')
    else:
        partes = [texto]

    return [normalizar_texto(p) for p in partes if normalizar_texto(p)]


def obtener_rutas_jerarquia_from_form():
    """
    Lee rutas jerárquicas desde el formulario.
    Soporta:
    - multiple select: ruta_jerarquia=A&ruta_jerarquia=B
    - multiple select con corchetes: ruta_jerarquia[]=A&ruta_jerarquia[]=B
    - hidden JSON: ruta_jerarquia=["A","B"]
    - textarea con líneas
    """
    valores = []

    claves = (
        'ruta_jerarquia',
        'ruta_jerarquia[]',
        'rutas_jerarquia',
        'rutas_jerarquia[]',
        'ubicaciones',
        'ubicaciones[]',
        'ruta',
        'ruta[]',
    )

    for clave in claves:
        try:
            valores.extend(request.form.getlist(clave))
        except Exception:
            pass

    rutas = []
    for valor in valores:
        rutas.extend(parsear_lista_rutas(valor))

    vistos = set()
    resultado = []

    for ruta in rutas:
        ruta = normalizar_texto(ruta)
        if ruta and ruta not in vistos:
            vistos.add(ruta)
            resultado.append(ruta)

    return resultado


def obtener_datos_repuesto_from_form():
    """
    Extrae datos del repuesto desde el POST de forma tolerante.
    """
    cantidad_raw = request.form.get('cantidad', '0')
    try:
        cantidad = int(float(cantidad_raw or 0))
    except Exception:
        cantidad = 0

    estado = (
        request.form.get('estado')
        or request.form.get('estado1')
        or ''
    )

    fecha_creacion = (
        request.form.get('fecha_creacion')
        or request.form.get('fecha_alta')
        or ''
    )

    fecha_fin = (
        request.form.get('fecha_fin')
        or request.form.get('fecha_baja')
        or ''
    )

    return {
        'codigo': normalizar_texto(request.form.get('codigo')),
        'nombre': normalizar_texto(request.form.get('nombre')),
        'cantidad': cantidad,
        'equipo': normalizar_texto(request.form.get('equipo')),
        'estado': normalizar_texto(estado),
        'link': normalizar_texto(request.form.get('link')),
        'comentario': normalizar_texto(request.form.get('comentario')),
        'fecha_creacion': normalizar_texto(fecha_creacion),
        'fecha_fin': normalizar_texto(fecha_fin),
        'ruta_jerarquia': obtener_rutas_jerarquia_from_form(),
    }


def coincide_jerarquia(repuesto, ruta_objetivo):
    """
    Devuelve True si el repuesto pertenece a la ubicación técnica seleccionada.
    """
    objetivo = normalizar_texto(ruta_objetivo).lower()

    if not objetivo:
        return True

    rutas = [
        normalizar_texto(r).lower()
        for r in parsear_lista_rutas(repuesto.get('ruta_jerarquia', []))
        if normalizar_texto(r)
    ]

    return objetivo in rutas


def filtro_buscar(repuestos, buscar):
    """
    Filtro global de texto para tablas/PDF.
    """
    buscar = normalizar_texto(buscar).lower()

    if not buscar:
        return list(repuestos)

    resultado = []

    for r in repuestos:
        partes = [
            normalizar_texto(r.get('nombre', '')),
            normalizar_texto(r.get('codigo', '')),
            normalizar_texto(r.get('equipo', '')),
            normalizar_texto(r.get('estado', '')),
            str(r.get('cantidad', '')),
            normalizar_texto(r.get('comentario', '')),
            normalizar_texto(r.get('link', '')),
            normalizar_texto(r.get('fecha_creacion', '')),
            normalizar_texto(r.get('fecha_fin', '')),
        ]

        rutas = parsear_lista_rutas(r.get('ruta_jerarquia', []))
        partes.extend(normalizar_texto(x) for x in rutas if normalizar_texto(x))

        texto = ' '.join(partes).lower()

        if buscar in texto:
            resultado.append(r)

    return resultado


def mapear_estados(estados=None):
    """
    Devuelve mapa emoji/estado -> nombre legible.
    """
    if estados is None:
        try:
            from core.data_loaders import cargar_estados
            estados = cargar_estados()
        except Exception:
            estados = []

    mapa = {}

    for e in estados:
        if not isinstance(e, dict):
            continue

        emoji = normalizar_texto(e.get('emoji') or e.get('emojy') or '')
        nombre = normalizar_texto(e.get('nombre') or '')

        if emoji:
            mapa[emoji] = nombre or emoji

        if nombre:
            mapa[nombre] = nombre

    return mapa


def obtener_jerarquias(repuestos=None):
    """
    Obtiene todas las rutas jerárquicas únicas de los repuestos.
    """
    if repuestos is None:
        try:
            from core.repuestos import cargar_todos_repuestos
            repuestos = cargar_todos_repuestos()
        except Exception:
            repuestos = []

    jerarquias = set()

    for item in repuestos:
        rutas = parsear_lista_rutas(item.get('ruta_jerarquia', []))
        for ruta in rutas:
            if ruta:
                jerarquias.add(ruta)

    return sorted(jerarquias)


def filtrar_repuestos_por_estado(
    repuestos=None,
    estado_nombre='',
    jerarquia_seleccionada=None,
    estados=None
):
    """
    Filtra repuestos por estado y, opcionalmente, por ubicación técnica.

    Soporta:
    - estado legible: "Operativo"
    - estado raw/emoji: "🟢"
    - "Otros" para estados vacíos o no mapeados.
    """
    if repuestos is None:
        try:
            from core.repuestos import cargar_todos_repuestos
            repuestos = cargar_todos_repuestos()
        except Exception:
            repuestos = []

    base = list(repuestos)

    filtro_jerarquia = normalizar_texto(jerarquia_seleccionada)

    if filtro_jerarquia:
        base = [
            r for r in base
            if coincide_jerarquia(r, filtro_jerarquia)
        ]

    objetivo = normalizar_texto(estado_nombre)

    if not objetivo:
        return base

    mapa_estados = mapear_estados(estados)
    objetivo_low = objetivo.lower()

    resultado = []

    for r in base:
        estado_raw = normalizar_texto(r.get('estado', ''))
        estado_legible = normalizar_texto(
            mapa_estados.get(estado_raw, estado_raw or 'Otros')
        )

        if objetivo_low == estado_raw.lower() or objetivo_low == estado_legible.lower():
            resultado.append(r)

    return resultado


def normalizar_repuesto(repuesto):
    """
    Normaliza un repuesto para consumo seguro en templates/JS/PDF.
    - comentario siempre string
    - ruta_jerarquia siempre list[str]
    - campos básicos normalizados
    """
    if not isinstance(repuesto, dict):
        return repuesto

    data = dict(repuesto)

    data['comentario'] = normalizar_texto(data.get('comentario', ''))
    data['ruta_jerarquia'] = parsear_lista_rutas(data.get('ruta_jerarquia', []))

    for campo in (
        'codigo',
        'nombre',
        'equipo',
        'estado',
        'link',
        'imagen',
        'fecha_creacion',
        'fecha_fin',
    ):
        if campo in data:
            data[campo] = normalizar_texto(data.get(campo, ''))

    if 'cantidad' in data:
        try:
            data['cantidad'] = int(float(data.get('cantidad') or 0))
        except Exception:
            data['cantidad'] = 0

    return data


def normalizar_lista_repuestos(repuestos):
    """
    Normaliza una lista de repuestos.
    Reutilizable por todas las apps de repuestos.
    """
    if not repuestos:
        return []
    return [normalizar_repuesto(r) for r in repuestos]