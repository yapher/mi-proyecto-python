"""
Blueprint de Instalaciones - VERSIÓN SQL
Ahora usa SQL en lugar de JSON.
"""
from flask import Blueprint, jsonify, render_template, request, current_app
from flask_login import current_user
from core.menu import cargar_menu
from auth.login import roles_required
import os
from functools import wraps
from core.image import (
    procesar_imagen as _core_procesar_imagen,
    allowed_file,
    calcular_hash_archivo,
    calcular_hash_bytes,
    DEFAULT_ALLOWED_EXTENSIONS,
)
from core.db_sql_store import ubicacion_store

__all__ = [
    'procesar_imagen', 'allowed_file',
    'calcular_hash_archivo', 'calcular_hash_bytes',
    'UPLOAD_FOLDER', 'ALLOWED_EXTENSIONS',
]

UPLOAD_FOLDER = os.path.join('templates', 'Aplic', 'instalaciones', 'static', 'img')
UPLOAD_FOLDER_INSTALACIONES = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = DEFAULT_ALLOWED_EXTENSIONS


def procesar_imagen(archivo):
    return _core_procesar_imagen(archivo, destino=UPLOAD_FOLDER)


instalaciones_bp = Blueprint(
    'indexinstalaciones', __name__,
    static_folder='../static',
    static_url_path='/instalaciones/static'
)


def login_required_json(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'status': 'error', 'msg': 'No autenticado'}), 401
        return f(*args, **kwargs)
    return decorated


@instalaciones_bp.route('/instalaciones')
@login_required_json
@roles_required('viewer')
def indexinstalaciones():
    nemu = cargar_menu()
    return render_template(
        'Aplic/instalaciones/FrontEnd/instalaciones.html',
        nemu=nemu, roles=current_user.roles
    )


@instalaciones_bp.route('/api/ubicaciones')
@login_required_json
@roles_required('viewer')
def api_ubicaciones():
    return jsonify(ubicacion_store.cargar_arbol())


@instalaciones_bp.route('/api/ubicacion_tecnica_json')
@login_required_json
@roles_required('viewer')
def ubicacion_tecnica_json():
    return jsonify(ubicacion_store.cargar_arbol())


@instalaciones_bp.route('/api/subir_imagen', methods=['POST'])
@login_required_json
def subir_imagen():
    if 'imagen' not in request.files:
        return jsonify({'status': 'error', 'msg': 'No se envió ningún archivo'}), 400
    archivo = request.files['imagen']
    filename, error = procesar_imagen(archivo)
    if error:
        return jsonify({'status': 'error', 'msg': error}), 400
    if not filename:
        return jsonify({'status': 'error', 'msg': 'No se pudo procesar la imagen'}), 400
    return jsonify({
        'status': 'ok',
        'filename': filename,
        'url': f"/instalaciones/static/img/{filename}"
    })


@instalaciones_bp.route('/api/editar_ubicacion', methods=['PUT'])
@login_required_json
@roles_required('viewer')
def editar_ubicacion():
    if request.content_type and 'multipart/form-data' in request.content_type:
        modificado = request.form.to_dict()
        archivo_imagen = request.files.get('imagen')
        eliminar_imagen = modificado.get('eliminar_imagen', '').lower() == 'true'
    else:
        modificado = request.get_json() or {}
        archivo_imagen = None
        eliminar_imagen = modificado.get('eliminar_imagen', False)

    if not modificado:
        return jsonify({'status': 'error', 'msg': 'Datos inválidos'}), 400

    ruta_jerarquia = modificado.get('ruta_jerarquia')
    if not ruta_jerarquia:
        return jsonify({'status': 'error', 'msg': 'Falta ruta_jerarquia'}), 400

    nueva_imagen = None
    imagen_eliminada = False

    if eliminar_imagen:
        nueva_imagen = ''
        imagen_eliminada = True
    elif archivo_imagen and archivo_imagen.filename:
        filename, error = procesar_imagen(archivo_imagen)
        if error:
            return jsonify({'status': 'error', 'msg': error}), 400
        if filename:
            nueva_imagen = filename

    # Calcular nueva ruta_jerarquia si cambió el nombre
    partes = ruta_jerarquia.split('-')
    nuevo_nombre = modificado.get('nombre', partes[-1])
    nueva_ruta = '-'.join(partes[:-1] + [nuevo_nombre])

    nuevos_datos = {
        'nombre': modificado.get('nombre', ''),
        'emoji': modificado.get('emoji', ''),
        'ruta': modificado.get('ruta', ''),
        'ruta_jerarquia': nueva_ruta
    }

    if eliminar_imagen:
        nuevos_datos['imagen'] = ''
    elif nueva_imagen:
        nuevos_datos['imagen'] = nueva_imagen
    elif modificado.get('imagen'):
        nuevos_datos['imagen'] = modificado.get('imagen')

    exito, msg = ubicacion_store.editar(ruta_jerarquia, nuevos_datos)
    if exito:
        return jsonify({
            'status': 'ok',
            'msg': 'Ubicación actualizada correctamente',
            'imagen_eliminada': imagen_eliminada
        })
    return jsonify({'status': 'no encontrado', 'msg': msg}), 404


@instalaciones_bp.route('/api/borrar_ubicacion', methods=['DELETE'])
@login_required_json
@roles_required('viewer')
def borrar_ubicacion():
    data = request.json or {}
    ruta_jerarquia = data.get('ruta_jerarquia')
    if not ruta_jerarquia:
        return jsonify({'status': 'error', 'msg': 'Falta ruta_jerarquia'}), 400

    exito, msg = ubicacion_store.eliminar(ruta_jerarquia)
    if exito:
        return jsonify({'status': 'ok', 'msg': 'Ubicación eliminada correctamente'})
    return jsonify({'status': 'no encontrado', 'msg': msg}), 404


@instalaciones_bp.route('/api/agregar_sububicacion', methods=['POST'])
@login_required_json
@roles_required('viewer')
def agregar_sububicacion():
    if request.content_type and 'multipart/form-data' in request.content_type:
        ruta_padre = request.form.get('ruta_padre')
        nombre = request.form.get('nombre', 'nuevo')
        emoji = request.form.get('emoji', '')
        ruta = request.form.get('ruta', '')
        archivo_imagen = request.files.get('imagen')
    else:
        req_json = request.get_json() or {}
        ruta_padre = req_json.get('ruta_padre')
        nuevo_hijo = req_json.get('nuevo_hijo', {})
        nombre = nuevo_hijo.get('nombre', 'nuevo')
        emoji = nuevo_hijo.get('emoji', '')
        ruta = nuevo_hijo.get('ruta', '')
        archivo_imagen = None

    if not ruta_padre:
        return jsonify({'status': 'error', 'msg': 'Falta ruta_padre'}), 400

    imagen_filename = None
    if archivo_imagen and archivo_imagen.filename:
        filename, error = procesar_imagen(archivo_imagen)
        if error:
            return jsonify({'status': 'error', 'msg': error}), 400
        if filename:
            imagen_filename = filename

    nuevos_datos = {
        'nombre': nombre,
        'emoji': emoji,
        'ruta': ruta,
    }
    if imagen_filename:
        nuevos_datos['imagen'] = imagen_filename

    exito, msg = ubicacion_store.agregar(nombre, emoji, ruta, ruta_padre)
    if exito:
        return jsonify({'status': 'ok', 'msg': 'Sububicación agregada correctamente'})
    return jsonify({'status': 'no encontrado', 'msg': msg}), 404