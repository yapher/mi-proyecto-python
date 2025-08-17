# Archivo backend generado automáticamente

from flask_login import login_required, current_user
from menu import cargar_menu
from login import roles_required
from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, current_app
import json, re, os

crear_almacenes_bp = Blueprint('indexcrear_almacenes', __name__)
DATA_FILE = 'DataBase/dataRep/almacenes.json'


@crear_almacenes_bp.route('/crear_almacenes')
@login_required
@roles_required('viewer')
def indexcrear_almacenes():
    nemu = cargar_menu()
    return render_template('Aplic/crearalmacenes/FrontEnd/crear_almacenes.html',nemu=nemu, roles=current_user.roles)


def cargar_datos():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def guardar_datos(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def agregar_nodo(crear_almaceneses, nombre, emoji, ruta_crear_almacenes, ruta_padre):
    partes = ruta_padre.split('-') if ruta_padre else []
    actual = crear_almaceneses

    for parte in partes:
        nodo = next((u for u in actual if u['nombre'] == parte), None)
        if not nodo:
            return False
        if 'subcrear_almacenes' not in nodo:
            nodo['subcrear_almacenes'] = []
        actual = nodo['subcrear_almacenes']

    nuevo = {
        'nombre': nombre,
        'emoji': emoji,
        'ruta': ruta_crear_almacenes,
        'ruta_jerarquia': f"{ruta_padre + '-' if ruta_padre else ''}{nombre}",
        'subcrear_almacenes': []
    }

    actual.append(nuevo)
    return True


def buscar_y_actualizar(crear_almaceneses, ruta, nuevos_datos):
    for crear_almacenes in crear_almaceneses:
        if crear_almacenes['ruta_jerarquia'] == ruta:
            crear_almacenes.update(nuevos_datos)
            return True
        if 'subcrear_almacenes' in crear_almacenes:
            if buscar_y_actualizar(crear_almacenes['subcrear_almacenes'], ruta, nuevos_datos):
                return True
    return False


def eliminar_nodo(crear_almaceneses, ruta):
    for i, crear_almacenes in enumerate(crear_almaceneses):
        if crear_almacenes['ruta_jerarquia'] == ruta:
            crear_almaceneses.pop(i)
            return True
        if 'subcrear_almacenes' in crear_almacenes:
            if eliminar_nodo(crear_almacenes['subcrear_almacenes'], ruta):
                return True
    return False


@crear_almacenes_bp.route('/crear_almacenes')
def vista_crear_almaceneses():
    return render_template('crear_almacenes.html')


@crear_almacenes_bp.route('/api/crear_almacenes_arbol')
def api_arbol_crear_almacenes():
    datos = cargar_datos()
    return jsonify(datos)


@crear_almacenes_bp.route('/api/crear_almacenes', methods=['POST'])
def agregar_crear_almacenes():
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


@crear_almacenes_bp.route('/api/crear_almacenes', methods=['PUT'])
def editar_crear_almacenes():
    datos = cargar_datos()
    payload = request.get_json()
    ruta_original = payload.get('ruta')
    nombre = payload.get('nombre')
    emoji = payload.get('emoji')
    ruta_crear_almacenes = payload.get('ruta_crear_almacenes', '')

    if not ruta_original or not nombre or not emoji:
        return jsonify({'msg': 'Faltan campos obligatorios'}), 400

    partes = ruta_original.split('-')
    nueva_ruta = '-'.join(partes[:-1] + [nombre])

    nuevos_datos = {
        'nombre': nombre,
        'emoji': emoji,
        'ruta': ruta_crear_almacenes,
        'ruta_jerarquia': nueva_ruta
    }

    exito = buscar_y_actualizar(datos, ruta_original, nuevos_datos)
    if not exito:
        return jsonify({'msg': 'No se encontró el almacén a editar'}), 400

    guardar_datos(datos)
    return jsonify({'msg': 'Almacén actualizado correctamente'})


@crear_almacenes_bp.route('/api/crear_almacenes', methods=['DELETE'])
def eliminar_crear_almacenes():
    datos = cargar_datos()
    payload = request.get_json()
    ruta = payload.get('ruta')

    if not ruta:
        return jsonify({'msg': 'Ruta no proporcionada'}), 400

    exito = eliminar_nodo(datos, ruta)
    if not exito:
        return jsonify({'msg': 'No se encontró el almacén a eliminar'}), 400

    guardar_datos(datos)
    return jsonify({'msg': 'Almacén eliminado correctamente'})

