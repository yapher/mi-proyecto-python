from flask_login import login_required, current_user
from menu import cargar_menu
from login import roles_required
from flask import Blueprint, jsonify, request, render_template
import os
import json
    
   
ubicacion_bp = Blueprint('ubicacion', __name__)
DATA_FILE = 'DataBase/dataRep/ubicacion_tecnica.json'


@ubicacion_bp.route("/creaUbTec")
@login_required
@roles_required('viewer')
def creaUbiTec():
    nemu = cargar_menu()
    return render_template('Aplic/crearubicaciontecnica/FrontEnd/crear_ubicacion_tecnica.html', nemu=nemu, roles=current_user.roles)


def cargar_datos():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def guardar_datos(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def agregar_nodo(ubicaciones, nombre, emoji, ruta_ubicacion, ruta_padre):
    partes = ruta_padre.split('-') if ruta_padre else []
    actual = ubicaciones

    for parte in partes:
        nodo = next((u for u in actual if u['nombre'] == parte), None)
        if not nodo:
            return False
        if 'sububicaciones' not in nodo:
            nodo['sububicaciones'] = []
        actual = nodo['sububicaciones']

    nuevo = {
        'nombre': nombre,
        'emoji': emoji,
        'ruta': ruta_ubicacion,
        'ruta_jerarquia': f"{ruta_padre + '-' if ruta_padre else ''}{nombre}",
        'sububicaciones': []
    }

    actual.append(nuevo)
    return True


def buscar_y_actualizar(ubicaciones, ruta, nuevos_datos):
    for ubicacion in ubicaciones:
        if ubicacion['ruta_jerarquia'] == ruta:
            ubicacion.update(nuevos_datos)
            return True
        if 'sububicaciones' in ubicacion:
            if buscar_y_actualizar(ubicacion['sububicaciones'], ruta, nuevos_datos):
                return True
    return False


def eliminar_nodo(ubicaciones, ruta):
    for i, ubicacion in enumerate(ubicaciones):
        if ubicacion['ruta_jerarquia'] == ruta:
            ubicaciones.pop(i)
            return True
        if 'sububicaciones' in ubicacion:
            if eliminar_nodo(ubicacion['sububicaciones'], ruta):
                return True
    return False


@ubicacion_bp.route('/ubicaciones')
def vista_ubicaciones():
    return render_template('ubicaciones.html')


@ubicacion_bp.route('/api/ubicacion_arbol')
def api_arbol_ubicacion():
    datos = cargar_datos()
    return jsonify(datos)


@ubicacion_bp.route('/api/ubicacion', methods=['POST'])
def agregar_ubicacion():
    datos = cargar_datos()
    payload = request.get_json()
    nombre = payload.get('nombre')
    emoji = payload.get('emoji')
    ruta = payload.get('ruta', '')
    ruta_padre = payload.get('ruta_padre', '')

    if not nombre or not emoji:
        return jsonify({'msg': 'Faltan campos obligatorios'}), 400

    exito = agregar_nodo(datos, nombre, emoji, ruta, ruta_padre)
    if not exito:
        return jsonify({'msg': 'No se encontró el padre para agregar el ítem'}), 400

    guardar_datos(datos)
    return jsonify({'msg': 'Ubicación agregada correctamente'})


@ubicacion_bp.route('/api/ubicacion', methods=['PUT'])
def editar_ubicacion():
    datos = cargar_datos()
    payload = request.get_json()
    ruta_original = payload.get('ruta')
    nombre = payload.get('nombre')
    emoji = payload.get('emoji')
    ruta_ubicacion = payload.get('ruta_ubicacion', '')

    if not ruta_original or not nombre or not emoji:
        return jsonify({'msg': 'Faltan campos obligatorios'}), 400

    partes = ruta_original.split('-')
    nueva_ruta = '-'.join(partes[:-1] + [nombre])

    nuevos_datos = {
        'nombre': nombre,
        'emoji': emoji,
        'ruta': ruta_ubicacion,
        'ruta_jerarquia': nueva_ruta
    }

    exito = buscar_y_actualizar(datos, ruta_original, nuevos_datos)
    if not exito:
        return jsonify({'msg': 'No se encontró la ubicación a editar'}), 400

    guardar_datos(datos)
    return jsonify({'msg': 'Ubicación actualizada correctamente'})


@ubicacion_bp.route('/api/ubicacion', methods=['DELETE'])
def eliminar_ubicacion():
    datos = cargar_datos()
    payload = request.get_json()
    ruta = payload.get('ruta')

    if not ruta:
        return jsonify({'msg': 'Ruta no proporcionada'}), 400

    exito = eliminar_nodo(datos, ruta)
    if not exito:
        return jsonify({'msg': 'No se encontró la ubicación a eliminar'}), 400

    guardar_datos(datos)
    return jsonify({'msg': 'Ubicación eliminada correctamente'})
