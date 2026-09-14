# templates/Aplic/graficosrepuestos/BackEnd/graficos_repuestos.py
"""
Blueprint de Gráficos de Repuestos.
USA core/repuestos.py para funciones reutilizables.
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