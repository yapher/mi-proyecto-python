# Archivo backend generado automáticamente

from flask_login import login_required, current_user
from menu import cargar_menu
from login import roles_required
from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, current_app
import json, re, os

crear_rubros_bp = Blueprint('indexcrear_rubros', __name__)


RUBRO_PATH = 'DataBase/hogar/rubro.json'


@crear_rubros_bp.route('/crear_rubros')
@login_required
@roles_required('viewer')
def indexcrear_rubros():
    nemu = cargar_menu()
    return render_template('Aplic/crearrubros/FrontEnd/crear_rubros.html',nemu=nemu, roles=current_user.roles)

###################
#  CRUD DE RUBROS #
###################

# obtiene lista de datos del archivo json rubros carga la tabla
@crear_rubros_bp.route("/api/rubro_arbol", methods=["GET"])
@login_required
@roles_required('viewer')
def obtener_arbol_menu():
    def construir_arbol(menus, ruta_padre=""):
        resultado = []
        for menu in menus:
            ruta_actual = f"{ruta_padre}.{menu['nombre']}" if ruta_padre else menu['nombre']
            nodo = {
                "nombre": menu['nombre'],
                "emoji": menu['emoji'],
                "ruta": menu.get("ruta", ""),
                "ruta_jerarquia": ruta_actual,
                "submenues": construir_arbol(menu.get('submenues', []), ruta_actual)
            }
            resultado.append(nodo)
        return resultado
    data = cargar_rubro()
    return jsonify(construir_arbol(data))

# Crea rubros
@crear_rubros_bp.route("/api/rubro", methods=["POST"])
@login_required
@roles_required('viewer')
def crear_menu():
    datos = request.get_json()
    nombre = datos.get("nombre")
    emoji = datos.get("emoji")
    ruta_menu = datos.get("ruta", "")
    ruta_padre = datos.get("ruta_padre", "")
    if not nombre or not emoji:
        return jsonify({"msg": "Faltan datos","type": "error" }), 400

    data = cargar_rubro()
    padre = buscar_nodo_por_ruta(data, ruta_padre)
    if padre is None:
        return jsonify({"msg": "Ruta padre inválida","type": "error"}), 400

    nuevo_menu = {
        "nombre": nombre,
        "emoji": emoji,
        "ruta": ruta_menu,
        "submenues": []
    }

    if isinstance(padre, list):
        if any(item["nombre"] == nombre for item in padre):
            return jsonify({"msg": "El menú ya existe","type": "info"}), 400
        padre.append(nuevo_menu)
    elif isinstance(padre, dict):
        if any(item["nombre"] == nombre for item in padre.get("submenues", [])):
            return jsonify({"msg": "El submenú ya existe","type": "info"}), 400
        padre.setdefault("submenues", []).append(nuevo_menu)
    else:
        return jsonify({"msg": "Error inesperado","type": "error"}), 400

    guardar_rubro(data)
    return jsonify({"msg": "Rubro creado correctamente"})

# Editar rubro
@crear_rubros_bp.route("/api/rubro", methods=["PUT"])
@login_required
@roles_required('viewer')
def editar_menu():
    datos = request.get_json()
    ruta_jerarquia = datos.get("ruta")
    nombre = datos.get("nombre")
    emoji = datos.get("emoji")
    ruta_menu = datos.get("ruta_menu", "")

    if not ruta_jerarquia or not nombre or not emoji:
        return jsonify({"msg": "Faltan datos","type": "error"}), 400

    data = cargar_rubro()
    partes = ruta_jerarquia.split('.')
    padre_ruta = '.'.join(partes[:-1])
    padre = buscar_nodo_por_ruta(data, padre_ruta)
    if padre is None:
        return jsonify({"msg": "Ruta inválida","type": "error"}), 400

    if isinstance(padre, list):
        nodo = next((item for item in padre if item["nombre"] == partes[-1]), None)
    else:
        nodo = next((item for item in padre.get("submenues", []) if item["nombre"] == partes[-1]), None)

    if nodo is None:
        return jsonify({"msg": "Ítem no encontrado","type": "error"}), 404

    nodo["nombre"] = nombre
    nodo["emoji"] = emoji
    nodo["ruta"] = ruta_menu
    guardar_rubro(data)
    return jsonify({"msg": "Rubro actualizado correctamente"})

# Eliminar rubro
@crear_rubros_bp.route("/api/rubro", methods=["DELETE"])
@login_required
@roles_required('viewer')
def eliminar_menu():
    datos = request.get_json()
    ruta = datos.get("ruta")
    if not ruta:
        return jsonify({"msg": "Ruta requerida","type": "error"}), 400

    data = cargar_rubro()
    partes = ruta.split('.')
    padre_ruta = '.'.join(partes[:-1])
    padre = buscar_nodo_por_ruta(data, padre_ruta)
    if padre is None:
        return jsonify({"msg": "Ruta inválida","type": "error"}), 400

    if isinstance(padre, list):
        padre[:] = [item for item in padre if item["nombre"] != partes[-1]]
    else:
        padre["submenues"] = [item for item in padre.get("submenues", []) if item["nombre"] != partes[-1]]

    guardar_rubro(data)
    return jsonify({"msg": "Rubro eliminado correctamente"})


######################
# funciones de flask #
######################
def cargar_rubro():
    if os.path.exists(RUBRO_PATH):
        with open(RUBRO_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []
    
def guardar_rubro(rubro):
    with open(RUBRO_PATH, 'w', encoding='utf-8') as f:
        json.dump(rubro, f, ensure_ascii=False, indent=4)


def buscar_nodo_por_ruta(data, ruta):
    if not ruta:
        return data
    partes = ruta.split('.')
    nodo = data
    for parte in partes:
        if isinstance(nodo, list):
            nodo = next((item for item in nodo if item['nombre'] == parte), None)
        elif isinstance(nodo, dict):
            nodo = next((item for item in nodo.get('submenues', []) if item['nombre'] == parte), None)
        else:
            return None
        if nodo is None:
            return None
    return nodo