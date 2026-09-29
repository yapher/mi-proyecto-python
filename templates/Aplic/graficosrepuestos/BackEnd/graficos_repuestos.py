# templates/Aplic/graficosrepuestos/BackEnd/graficos_repuestos.py
"""
Blueprint de Gráficos de Repuestos.
"""

import os
import logging

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

from core.menu import cargar_menu
from auth.login import roles_required

from core.repuestos import (
    cargar_todos_repuestos,
    contar_repuestos_por_estado,
)

from core.repuestos_filtros import (
    normalizar_texto,
    obtener_jerarquias,
    filtrar_repuestos_por_estado,
)

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


@graficos_repuestos_bp.route('/graficos_repuestos')
@login_required
@roles_required('viewer')
def indexgraficos_repuestos():
    nemu = cargar_menu()

    repuestos = cargar_todos_repuestos()
    jerarquias = obtener_jerarquias(repuestos)

    jerarquia_inicial = normalizar_texto(request.args.get('jerarquia', ''))

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


@graficos_repuestos_bp.route('/graficos_repuestos/detalle/<path:estado>')
@login_required
@roles_required('viewer')
def detalle_estado(estado):
    jerarquia_seleccionada = request.args.get('jerarquia', '')

    repuestos = filtrar_repuestos_por_estado(
        repuestos=cargar_todos_repuestos(),
        estado_nombre=estado,
        jerarquia_seleccionada=jerarquia_seleccionada
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


@graficos_repuestos_bp.route('/graficos_repuestos/exportar_pdf/<path:estado>')
@login_required
@roles_required('viewer')
def exportar_pdf_estado(estado):
    if exportar_pdf_reportlab is None:
        logger.error("No se pudo importar exportar_pdf_reportlab.")
        return jsonify({"error": "Exportador PDF no disponible"}), 500

    jerarquia_seleccionada = request.args.get('jerarquia', '')

    repuestos = filtrar_repuestos_por_estado(
        repuestos=cargar_todos_repuestos(),
        estado_nombre=estado,
        jerarquia_seleccionada=jerarquia_seleccionada
    )

    if not repuestos:
        return jsonify({"error": "No hay repuestos para exportar"}), 404

    logger.info(
        f"Exportando PDF estado '{estado}' "
        f"jerarquia '{jerarquia_seleccionada}' → {len(repuestos)} repuestos "
        f"(usuario: {current_user.username})"
    )

    return exportar_pdf_reportlab(repuestos)