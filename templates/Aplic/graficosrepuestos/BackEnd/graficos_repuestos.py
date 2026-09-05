"""
Blueprint de Gráficos de Repuestos.
AHORA USA SQL en lugar de JSON.
"""
from flask_login import login_required, current_user
from core.menu import cargar_menu
from auth.login import roles_required
from flask import Blueprint, jsonify, request, render_template
from collections import Counter

# ✅ IMPORT DIRECTO DESDE CORE (más limpio)
from core.data_loaders import cargar_estados
# ✅ NUEVO: importar el store SQL de repuestos
from core.db_sql_store import repuesto_store

graficos_repuestos_bp = Blueprint('indexgraficos_repuestos', __name__)


def obtener_jerarquias():
    """Obtiene todas las rutas jerárquicas únicas de los repuestos."""
    repuestos = repuesto_store.cargar()
    jerarquias = set()
    for item in repuestos:
        rutas = item.get("ruta_jerarquia", [])
        if rutas:
            jerarquias.update(rutas)
    return sorted(jerarquias)


def contar_repuestos_por_estado(jerarquia=None):
    """Cuenta repuestos agrupados por estado, opcionalmente filtrado por jerarquía."""
    repuestos = repuesto_store.cargar()
    contador = Counter()
    estados = cargar_estados()

    # Mapa emoji → nombre legible
    mapa_estados = {e['emoji']: e['nombre'] for e in estados}

    for item in repuestos:
        rutas = item.get("ruta_jerarquia", [])
        if jerarquia and jerarquia not in rutas:
            continue
        estado = item.get("estado", "Otros")
        estado_legible = mapa_estados.get(estado, "Otros")
        contador[estado_legible] += 1

    return dict(contador)


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
    datos_estado = contar_repuestos_por_estado(jerarquia_seleccionada)
    return jsonify({
        "categorias": list(datos_estado.keys()),
        "valores": list(datos_estado.values())
    })