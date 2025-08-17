from flask_login import login_required, current_user
from menu import cargar_menu
from login import roles_required
from flask import Blueprint, jsonify, request, render_template
import json, os
from collections import Counter
from templates.Aplic.estadosderepuestos.BackEnd.estados_de_repuestos import  cargar_estados


graficos_repuestos_bp = Blueprint('indexgraficos_repuestos', __name__)

PATHREPUESTOS = 'DataBase/dataRep/REPUESTOS.json'


def obtener_jerarquias():
    if not os.path.exists(PATHREPUESTOS):
        return []
    with open(PATHREPUESTOS, 'r', encoding='utf-8') as f:
        data = json.load(f)

    jerarquias = set()
    for item in data:
        rutas = item.get("ruta_jerarquia", [])
        if rutas:
            jerarquias.update(rutas)
    return sorted(jerarquias)

def contar_repuestos_por_estado(jerarquia=None):
    if not os.path.exists(PATHREPUESTOS):
        return {}

    with open(PATHREPUESTOS, 'r', encoding='utf-8') as f:
        data = json.load(f)

    contador = Counter()
    estados = cargar_estados()
    for item in data:
        rutas = item.get("ruta_jerarquia", [])
        if jerarquia and jerarquia not in rutas:
            continue
        estado = item.get("estado", "Otros")
        estado_legible = {e['emoji']: e['nombre'] for e in estados}.get(estado, "Otros")
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
    return render_template('Aplic/graficosrepuestos/FrontEnd/graficos_repuestos.html',
                           nemu=nemu, roles=current_user.roles, datos=datos, jerarquias=jerarquias)

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

