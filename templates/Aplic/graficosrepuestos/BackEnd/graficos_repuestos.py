# templates/Aplic/graficosrepuestos/BackEnd/graficos_repuestos.py
"""
Blueprint de Gráficos de Repuestos.
USA core/repuestos.py para funciones reutilizables.
✅ NUEVO: Endpoint de detalle por estado + exportación PDF reutilizada
"""
import os
from flask_login import login_required, current_user
from core.menu import cargar_menu
from auth.login import roles_required
from flask import Blueprint, jsonify, request, render_template
from core.repuestos import (
    cargar_todos_repuestos,
    contar_repuestos_por_estado,
)
from core.logging_config import get_logger

logger = get_logger(__name__)

# ✅ REUTILIZAR: función de exportación PDF de estadosderepuestos
from templates.Aplic.estadosderepuestos.BackEnd.export_pdf import exportar_pdf_reportlab

_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_STATIC_DIR = os.path.abspath(os.path.join(_APP_DIR, '..', 'static'))

graficos_repuestos_bp = Blueprint(
    'indexgraficos_repuestos',
    __name__,
    static_folder=_STATIC_DIR,
    static_url_path='/graficosrepuestos/static'
)


def obtener_jerarquias():
    """Obtiene todas las rutas jerárquicas únicas de los repuestos."""
    repuestos = cargar_todos_repuestos()
    jerarquias = set()
    for item in repuestos:
        rutas = item.get("ruta_jerarquia", [])
        if rutas:
            jerarquias.update(rutas)
    return sorted(jerarquias)


def _filtrar_repuestos_por_estado(estado_nombre):
    """
    Filtra repuestos por el nombre legible del estado.
    Reutiliza la lógica de contar_repuestos_por_estado para obtener el mapa emoji→nombre.
    """
    from core.data_loaders import cargar_estados

    repuestos = cargar_todos_repuestos()
    estados = cargar_estados()

    # Mapa inverso: nombre_legible → emoji
    mapa_nombre_a_emoji = {e['nombre']: e['emoji'] for e in estados}
    # Mapa directo: emoji → nombre_legible
    mapa_emoji_a_nombre = {e['emoji']: e['nombre'] for e in estados}

    # Determinar el emoji buscado
    if estado_nombre in mapa_nombre_a_emoji:
        emoji_buscado = mapa_nombre_a_emoji[estado_nombre]
    elif estado_nombre in mapa_emoji_a_nombre:
        emoji_buscado = estado_nombre  # Ya era un emoji
    elif estado_nombre == "Otros":
        emoji_buscado = None  # Filtro especial
    else:
        return []

    # Filtrar repuestos
    filtrados = []
    for r in repuestos:
        estado_rep = r.get("estado", "")
        if emoji_buscado is None:
            # "Otros": estados que no están en el catálogo
            if estado_rep not in mapa_emoji_a_nombre:
                filtrados.append(r)
        else:
            if estado_rep == emoji_buscado:
                filtrados.append(r)

    return filtrados


# ============================================================
# RUTAS EXISTENTES (sin cambios)
# ============================================================

@graficos_repuestos_bp.route('/graficos_repuestos')
@login_required
@roles_required('viewer')
def indexgraficos_repuestos():
    nemu = cargar_menu()
    jerarquias = obtener_jerarquias()
    datos_estado = contar_repuestos_por_estado()
    datos = {
        "categorias": list(datos_estado.keys()),
        "valores": list(datos_estado.values())
    }
    return render_template(
        'Aplic/graficosrepuestos/FrontEnd/graficos_repuestos.html',
        nemu=nemu,
        roles=current_user.roles,
        datos=datos,
        jerarquias=jerarquias
    )


@graficos_repuestos_bp.route('/graficos_repuestos/datos')
@login_required
@roles_required('viewer')
def datos_filtrados():
    jerarquia_seleccionada = request.args.get('jerarquia', None)
    datos_estado = contar_repuestos_por_estado(filtro_jerarquia=jerarquia_seleccionada)
    return jsonify({
        "categorias": list(datos_estado.keys()),
        "valores": list(datos_estado.values())
    })


# ============================================================
# ✅ NUEVO: Detalle de repuestos por estado (para el modal)
# ============================================================

@graficos_repuestos_bp.route('/graficos_repuestos/detalle/<path:estado>')
@login_required
@roles_required('viewer')
def detalle_estado(estado):
    """
    Retorna HTML parcial con la tabla de repuestos filtrados por estado.
    Se inyecta dentro del modal vía fetch().
    """
    repuestos = _filtrar_repuestos_por_estado(estado)

    logger.info(
        f"Detalle estado '{estado}' → {len(repuestos)} repuestos "
        f"(usuario: {current_user.username})"
    )

    return render_template(
        'Aplic/graficosrepuestos/FrontEnd/component/modal_detalle_estado.html',
        estado=estado,
        repuestos=repuestos,
        total=len(repuestos)
    )


# ============================================================
# ✅ NUEVO: Exportar PDF de repuestos filtrados por estado
# ============================================================

@graficos_repuestos_bp.route('/graficos_repuestos/exportar_pdf/<path:estado>')
@login_required
@roles_required('viewer')
def exportar_pdf_estado(estado):
    """
    Exporta a PDF los repuestos de un estado específico.
    Reutiliza exportar_pdf_reportlab de estadosderepuestos.
    """
    repuestos = _filtrar_repuestos_por_estado(estado)

    if not repuestos:
        return jsonify({"error": "No hay repuestos para exportar"}), 404

    logger.info(
        f"Exportando PDF estado '{estado}' → {len(repuestos)} repuestos "
        f"(usuario: {current_user.username})"
    )

    return exportar_pdf_reportlab(repuestos)