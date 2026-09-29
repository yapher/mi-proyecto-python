# templates/Aplic/graficosrepuestos/BackEnd/graficos_repuestos.py
"""
Blueprint de Gráficos de Repuestos.

Reutiliza:
- core/repuestos.py
- core/data_loaders.py (si existe)
- core/pdf.py (si existe)

Objetivo:
- Mantener visibles los gráficos.
- Abrir modal de detalle al hacer click.
- Aplicar el filtro de ubicación técnica también al modal.
- Permitir editar/eliminar reutilizando partials de repuestos.
"""

import os
import json
import logging

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

from core.menu import cargar_menu
from auth.login import roles_required

from core.repuestos import (
    cargar_todos_repuestos,
    contar_repuestos_por_estado,
)

# ============================================================
# Imports robustos para no romper si algún módulo base no existe
# ============================================================
try:
    from core.data_loaders import (
        cargar_estados,
        cargar_ubicaciones,
        cargar_almacenes,
        obtener_nombres_almacenes,
    )
except ImportError:
    def cargar_estados():
        return []

    def cargar_ubicaciones():
        return []

    def cargar_almacenes():
        return []

    def obtener_nombres_almacenes(almacenes=None):
        return []


try:
    from core.pdf import exportar_pdf_reportlab
except ImportError:
    try:
        from core import exportar_pdf_reportlab
    except ImportError:
        exportar_pdf_reportlab = None


logger = logging.getLogger(__name__)

_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_STATIC_DIR = os.path.abspath(os.path.join(_APP_DIR, '..', 'static'))

graficos_repuestos_bp = Blueprint(
    'indexgraficos_repuestos',
    __name__,
    static_folder=_STATIC_DIR,
    static_url_path='/graficosrepuestos/static'
)


# ============================================================
# HELPERS
# ============================================================
def _normalizar_texto(valor):
    if valor is None:
        return ''
    return str(valor).strip()


def _texto_de_elemento_ruta(elemento):
    """
    Extrae texto útil de un elemento de ruta_jerarquia.
    Soporta dict, list, str, etc.
    """
    if isinstance(elemento, dict):
        for key in ('ruta_jerarquia', 'ruta', 'nombre', 'value'):
            if key in elemento:
                return _normalizar_texto(elemento[key])
        return ''

    return _normalizar_texto(elemento)


def _iter_rutas(valor):
    """
    Normaliza ruta_jerarquia puede venir como:
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
        rutas = []
        for item in valor:
            texto = _texto_de_elemento_ruta(item)
            if texto:
                rutas.append(texto)
        return rutas

    if isinstance(valor, dict):
        rutas = []
        for key in ('ruta_jerarquia', 'rutas', 'ruta', 'nombre'):
            if key in valor:
                rutas.extend(_iter_rutas(valor[key]))
        return rutas

    if isinstance(valor, str):
        s = valor.strip()
        if not s:
            return []

        if s.startswith('['):
            try:
                parsed = json.loads(s)
                if isinstance(parsed, list):
                    rutas = []
                    for item in parsed:
                        texto = _texto_de_elemento_ruta(item)
                        if texto:
                            rutas.append(texto)
                    return rutas
            except Exception:
                pass

        return [s]

    texto = _normalizar_texto(valor)
    return [texto] if texto else []


def obtener_jerarquias(repuestos=None):
    """
    Obtiene todas las rutas jerárquicas únicas de los repuestos.
    """
    if repuestos is None:
        repuestos = cargar_todos_repuestos()

    jerarquias = set()

    for item in repuestos:
        rutas = _iter_rutas(item.get('ruta_jerarquia', []))
        for ruta in rutas:
            if ruta:
                jerarquias.add(ruta)

    return sorted(jerarquias)


def _coincide_jerarquia(repuesto, jerarquia_seleccionada):
    """
    Devuelve True si el repuesto pertenece a la ubicación técnica seleccionada.
    """
    seleccionada = _normalizar_texto(jerarquia_seleccionada)

    if not seleccionada:
        return True

    rutas = _iter_rutas(repuesto.get('ruta_jerarquia', []))

    if not rutas:
        return False

    seleccionada_low = seleccionada.lower()

    for ruta in rutas:
        if _normalizar_texto(ruta).lower() == seleccionada_low:
            return True

    return False


def _mapear_estados():
    """
    Devuelve mapa emoji/estado_raw -> nombre legible.
    """
    mapa = {}

    try:
        estados = cargar_estados()
    except Exception as exc:
        logger.warning(f"No se pudieron cargar estados para mapeo: {exc}")
        estados = []

    for e in estados:
        if not isinstance(e, dict):
            continue

        emoji = _normalizar_texto(e.get('emoji') or e.get('emojy') or '')
        nombre = _normalizar_texto(e.get('nombre') or '')

        if emoji and nombre:
            mapa[emoji] = nombre
        elif emoji:
            mapa[emoji] = emoji

    return mapa


def _filtrar_repuestos_por_estado(estado_nombre, jerarquia_seleccionada=None):
    """
    Filtra repuestos por estado y, opcionalmente, por ubicación técnica.

    Soporta:
    - estado legible: "Operativo"
    - estado raw/emoji: "🟢"
    - "Otros" para estados vacíos o no mapeados.
    """
    repuestos = cargar_todos_repuestos()

    filtro_jerarquia = _normalizar_texto(jerarquia_seleccionada)

    if filtro_jerarquia:
        repuestos = [
            r for r in repuestos
            if _coincide_jerarquia(r, filtro_jerarquia)
        ]

    objetivo = _normalizar_texto(estado_nombre)

    if not objetivo:
        return repuestos

    mapa_estados = _mapear_estados()
    objetivo_low = objetivo.lower()

    resultado = []

    for r in repuestos:
        estado_raw = _normalizar_texto(r.get('estado', ''))
        estado_legible = _normalizar_texto(
            mapa_estados.get(estado_raw, estado_raw or 'Otros')
        )

        if objetivo_low == estado_raw.lower() or objetivo_low == estado_legible.lower():
            resultado.append(r)

    return resultado


# ============================================================
# VISTA PRINCIPAL
# ============================================================
@graficos_repuestos_bp.route('/graficos_repuestos')
@login_required
@roles_required('viewer')
def indexgraficos_repuestos():
    nemu = cargar_menu()

    repuestos = cargar_todos_repuestos()
    jerarquias = obtener_jerarquias(repuestos)

    jerarquia_inicial = _normalizar_texto(request.args.get('jerarquia', ''))

    if jerarquia_inicial:
        datos_estado = contar_repuestos_por_estado(
            filtro_jerarquia=jerarquia_inicial
        )
    else:
        datos_estado = contar_repuestos_por_estado()

    datos = {
        "categorias": list(datos_estado.keys()),
        "valores": list(datos_estado.values())
    }

    # Variables para reutilizar partials/repuestos/newRep.html
    estados = cargar_estados()
    ubicaciones = cargar_ubicaciones()
    almacenes = cargar_almacenes()
    nombres_almacenes = obtener_nombres_almacenes(almacenes)

    return render_template(
        'Aplic/graficosrepuestos/FrontEnd/graficos_repuestos.html',
        nemu=nemu,
        roles=current_user.roles,
        datos=datos,
        jerarquias=jerarquias,
        jerarquia_inicial=jerarquia_inicial,
        estados=estados,
        ubicaciones=ubicaciones,
        nombres_almacenes=nombres_almacenes,
        return_to='indexgraficos_repuestos.indexgraficos_repuestos',
        active_tab=''
    )


# ============================================================
# DATOS FILTRADOS POR JERARQUÍA
# ============================================================
@graficos_repuestos_bp.route('/graficos_repuestos/datos')
@login_required
@roles_required('viewer')
def datos_filtrados():
    jerarquia_seleccionada = request.args.get('jerarquia', None)

    datos_estado = contar_repuestos_por_estado(
        filtro_jerarquia=jerarquia_seleccionada
    )

    return jsonify({
        "categorias": list(datos_estado.keys()),
        "valores": list(datos_estado.values())
    })


# ============================================================
# DETALLE DE REPUESTOS POR ESTADO (MODAL)
# ============================================================
@graficos_repuestos_bp.route('/graficos_repuestos/detalle/<path:estado>')
@login_required
@roles_required('viewer')
def detalle_estado(estado):
    """
    Retorna HTML parcial con la tabla de repuestos filtrados por estado.
    Ahora también respeta el filtro de ubicación técnica:
    /graficos_repuestos/detalle/<estado>?jerarquia=<valor>
    """
    jerarquia_seleccionada = request.args.get('jerarquia', '')

    repuestos = _filtrar_repuestos_por_estado(
        estado,
        jerarquia_seleccionada
    )

    logger.info(
        f"Detalle estado '{estado}' "
        f"jerarquia '{jerarquia_seleccionada}' → {len(repuestos)} repuestos "
        f"(usuario: {current_user.username})"
    )

    return render_template(
        'Aplic/graficosrepuestos/FrontEnd/component/modal_detalle_estado.html',
        estado=estado,
        repuestos=repuestos,
        total=len(repuestos),
        jerarquia_seleccionada=jerarquia_seleccionada,
        return_to='indexgraficos_repuestos.indexgraficos_repuestos',
        active_tab=''
    )


# ============================================================
# EXPORTAR PDF POR ESTADO
# ============================================================
@graficos_repuestos_bp.route('/graficos_repuestos/exportar_pdf/<path:estado>')
@login_required
@roles_required('viewer')
def exportar_pdf_estado(estado):
    """
    Exporta a PDF los repuestos de un estado específico.
    También respeta el filtro de ubicación técnica si se envía por query:
    /graficos_repuestos/exportar_pdf/<estado>?jerarquia=<valor>
    """
    if exportar_pdf_reportlab is None:
        logger.error("No se pudo importar exportar_pdf_reportlab.")
        return jsonify({"error": "Exportador PDF no disponible"}), 500

    jerarquia_seleccionada = request.args.get('jerarquia', '')

    repuestos = _filtrar_repuestos_por_estado(
        estado,
        jerarquia_seleccionada
    )

    if not repuestos:
        return jsonify({"error": "No hay repuestos para exportar"}), 404

    logger.info(
        f"Exportando PDF estado '{estado}' "
        f"jerarquia '{jerarquia_seleccionada}' → {len(repuestos)} repuestos "
        f"(usuario: {current_user.username})"
    )

    return exportar_pdf_reportlab(repuestos)