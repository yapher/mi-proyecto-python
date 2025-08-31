from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user
from login import roles_required
from menu import cargar_menu
import json, os
from functools import wraps

UBI_TEC = 'DataBase/dataRep/ubicacion_tecnica.json'
instalaciones_bp = Blueprint('indexinstalaciones', __name__)

# ---------- Decorador login requerido JSON ----------
def login_required_json(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'status':'error', 'msg':'No autenticado'}), 401
        return f(*args, **kwargs)
    return decorated

# ---------- Funciones de carga y guardado ----------
def cargar_ubicaciones():
    if not os.path.exists(UBI_TEC):
        return []
    with open(UBI_TEC, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def guardar_ubicaciones(data):
    with open(UBI_TEC, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ---------- Funciones de manipulación ----------
def encontrar_y_modificar(nodos, ruta_jerarquia, nuevos_datos):
    for nodo in nodos:
        if nodo['ruta_jerarquia'] == ruta_jerarquia:
            nodo.update(nuevos_datos)
            return True
        if nodo.get('sububicaciones'):
            if encontrar_y_modificar(nodo['sububicaciones'], ruta_jerarquia, nuevos_datos):
                return True
    return False

def encontrar_y_borrar(nodos, ruta_jerarquia):
    for i, nodo in enumerate(nodos):
        if nodo['ruta_jerarquia'] == ruta_jerarquia:
            del nodos[i]
            return True
        if nodo.get('sububicaciones'):
            if encontrar_y_borrar(nodo['sububicaciones'], ruta_jerarquia):
                return True
    return False

def encontrar_y_agregar(nodos, ruta_padre, nuevo_hijo):
    for nodo in nodos:
        if nodo['ruta_jerarquia'] == ruta_padre:
            if 'sububicaciones' not in nodo:
                nodo['sububicaciones'] = []
            nodo['sububicaciones'].append(nuevo_hijo)
            return True
        if nodo.get('sububicaciones'):
            if encontrar_y_agregar(nodo['sububicaciones'], ruta_padre, nuevo_hijo):
                return True
    return False

# ---------- Rutas ----------
@instalaciones_bp.route('/instalaciones')
@login_required_json
@roles_required('viewer')
def indexinstalaciones():
    nemu = cargar_menu()
    return render_template(
        'Aplic/instalaciones/FrontEnd/instalaciones.html',
        nemu=nemu,
        roles=current_user.roles
    )

@instalaciones_bp.route('/api/ubicaciones')
@login_required_json
@roles_required('viewer')
def api_ubicaciones():
    return jsonify(cargar_ubicaciones())

@instalaciones_bp.route('/api/ubicacion_tecnica_json')
@login_required_json
@roles_required('viewer')
def ubicacion_tecnica_json():
    return jsonify(cargar_ubicaciones())

# ---------- API editar / borrar / agregar ----------
@instalaciones_bp.route('/api/editar_ubicacion', methods=['PUT'])
@login_required_json
@roles_required('editor')
def editar_ubicacion():
    data = cargar_ubicaciones()
    modificado = request.get_json()
    if not modificado:
        return jsonify({'status':'error','msg':'JSON inválido'}), 400

    ruta_jerarquia = modificado.get('ruta_jerarquia')
    if not ruta_jerarquia:
        return jsonify({'status':'error','msg':'Falta ruta_jerarquia'}), 400

    partes = ruta_jerarquia.split('-')
    nueva_ruta = '-'.join(partes[:-1] + [modificado.get('nombre', partes[-1])])
    nuevos_datos = {
        'nombre': modificado.get('nombre', ''),
        'emoji': modificado.get('emoji', ''),
        'ruta': modificado.get('ruta', ''),
        'imagen': modificado.get('imagen', ''),
        'ruta_jerarquia': nueva_ruta
    }

    if encontrar_y_modificar(data, ruta_jerarquia, nuevos_datos):
        guardar_ubicaciones(data)
        return jsonify({'status':'ok'})
    return jsonify({'status':'no encontrado'}), 404

@instalaciones_bp.route('/api/borrar_ubicacion', methods=['DELETE'])
@login_required_json
@roles_required('editor')
def borrar_ubicacion():
    data = cargar_ubicaciones()
    ruta_jerarquia = request.json.get('ruta_jerarquia') if request.json else None
    if not ruta_jerarquia:
        return jsonify({'status':'error','msg':'Falta ruta_jerarquia'}), 400
    if encontrar_y_borrar(data, ruta_jerarquia):
        guardar_ubicaciones(data)
        return jsonify({'status':'ok'})
    return jsonify({'status':'no encontrado'}), 404

@instalaciones_bp.route('/api/agregar_sububicacion', methods=['POST'])
@login_required_json
@roles_required('editor')
def agregar_sububicacion():
    data = cargar_ubicaciones()
    if not request.json:
        return jsonify({'status':'error','msg':'JSON inválido'}), 400
    ruta_padre = request.json.get('ruta_padre')
    nuevo_hijo = request.json.get('nuevo_hijo')
    if not ruta_padre or not nuevo_hijo:
        return jsonify({'status':'error','msg':'Faltan datos'}), 400

    if not nuevo_hijo.get('ruta_jerarquia'):
        nuevo_hijo['ruta_jerarquia'] = f"{ruta_padre}-{nuevo_hijo.get('nombre','nuevo')}"
    if 'sububicaciones' not in nuevo_hijo:
        nuevo_hijo['sububicaciones'] = []

    if encontrar_y_agregar(data, ruta_padre, nuevo_hijo):
        guardar_ubicaciones(data)
        return jsonify({'status':'ok'})
    return jsonify({'status':'no encontrado'}), 404
