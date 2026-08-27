from flask import Blueprint, jsonify, render_template, request, current_app
from flask_login import current_user
from core.menu import cargar_menu
from auth.login import roles_required
import json, os, hashlib, time
from functools import wraps
from werkzeug.utils import secure_filename

UBI_TEC = 'DataBase/dataRep/ubicacion_tecnica.json'

# ============================================================
# CONFIGURACIÓN DE IMÁGENES (reutilizable)
# ============================================================
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
UPLOAD_FOLDER = os.path.join('templates', 'Aplic', 'instalaciones', 'static', 'img')


def allowed_file(filename):
    """Verifica si la extensión del archivo es permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def asegurar_directorio_upload():
    """Asegura que el directorio de uploads exista."""
    ruta_completa = os.path.join(current_app.root_path, UPLOAD_FOLDER)
    os.makedirs(ruta_completa, exist_ok=True)
    return ruta_completa


def calcular_hash_archivo(ruta_archivo):
    """Calcula el hash MD5 de un archivo existente en disco."""
    hash_md5 = hashlib.md5()
    try:
        with open(ruta_archivo, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except (OSError, IOError):
        return None


def calcular_hash_bytes(data_bytes):
    """Calcula el hash MD5 de datos en memoria (bytes)."""
    return hashlib.md5(data_bytes).hexdigest()


def procesar_imagen(archivo):
    """
    Procesa y guarda una imagen con reutilización inteligente.
    - Si existe archivo con mismo hash → NO duplica
    - Si existe con hash diferente → agrega timestamp
    Retorna (nombre_archivo, error).
    """
    if not archivo or archivo.filename == '':
        return None, None

    if not allowed_file(archivo.filename):
        return None, f"Formato no permitido. Use: {', '.join(ALLOWED_EXTENSIONS)}"

    filename = secure_filename(archivo.filename)
    directorio = asegurar_directorio_upload()
    ruta_completa = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)

    try:
        archivo.seek(0)
        contenido_nuevo = archivo.read()
        archivo.seek(0)
    except Exception as e:
        return None, f"Error al leer el archivo: {str(e)}"

    if os.path.exists(ruta_completa):
        hash_existente = calcular_hash_archivo(ruta_completa)
        hash_nuevo = calcular_hash_bytes(contenido_nuevo)

        if hash_existente == hash_nuevo:
            return filename, None
        else:
            nombre, extension = os.path.splitext(filename)
            filename = f"{nombre}_{int(time.time())}{extension}"
            ruta_completa = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)

    try:
        with open(ruta_completa, "wb") as f:
            f.write(contenido_nuevo)
        return filename, None
    except Exception as e:
        return None, f"Error al guardar imagen: {str(e)}"


# ============================================================
# BLUEPRINT
# ============================================================
instalaciones_bp = Blueprint(
    'indexinstalaciones',
    __name__,
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


# ============================================================
# RUTAS
# ============================================================
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


# ============================================================
# NUEVO ENDPOINT: Subir imagen (reutilizable)
# ============================================================
@instalaciones_bp.route('/api/subir_imagen', methods=['POST'])
@login_required_json
def subir_imagen():
    """Endpoint reutilizable para subir imágenes."""
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


# ============================================================
# API EDITAR (soporta FormData + eliminar_imagen)
# ============================================================
@instalaciones_bp.route('/api/editar_ubicacion', methods=['PUT'])
@login_required_json
@roles_required('viewer')
def editar_ubicacion():
    data = cargar_ubicaciones()

    # Aceptar tanto JSON como FormData
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

    partes = ruta_jerarquia.split('-')
    nueva_ruta = '-'.join(partes[:-1] + [modificado.get('nombre', partes[-1])])

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

    if encontrar_y_modificar(data, ruta_jerarquia, nuevos_datos):
        guardar_ubicaciones(data)
        return jsonify({
            'status': 'ok',
            'msg': 'Ubicación actualizada correctamente',
            'imagen_eliminada': imagen_eliminada
        })

    return jsonify({'status': 'no encontrado', 'msg': 'La ubicación no existe'}), 404


@instalaciones_bp.route('/api/borrar_ubicacion', methods=['DELETE'])
@login_required_json
@roles_required('viewer')
def borrar_ubicacion():
    data = cargar_ubicaciones()
    ruta_jerarquia = request.json.get('ruta_jerarquia') if request.json else None
    if not ruta_jerarquia:
        return jsonify({'status': 'error', 'msg': 'Falta ruta_jerarquia'}), 400
    if encontrar_y_borrar(data, ruta_jerarquia):
        guardar_ubicaciones(data)
        return jsonify({'status': 'ok', 'msg': 'Ubicación eliminada correctamente'})
    return jsonify({'status': 'no encontrado', 'msg': 'La ubicación no existe'}), 404


# ============================================================
# API AGREGAR SUBUBICACIÓN (soporta FormData)
# ============================================================
@instalaciones_bp.route('/api/agregar_sububicacion', methods=['POST'])
@login_required_json
@roles_required('viewer')
def agregar_sububicacion():
    data = cargar_ubicaciones()

    if request.content_type and 'multipart/form-data' in request.content_type:
        ruta_padre = request.form.get('ruta_padre')
        nuevo_hijo = {
            'nombre': request.form.get('nombre', 'nuevo'),
            'emoji': request.form.get('emoji', ''),
            'ruta': request.form.get('ruta', ''),
            'ruta_jerarquia': '',
            'sububicaciones': []
        }
        archivo_imagen = request.files.get('imagen')
    else:
        req_json = request.get_json() or {}
        ruta_padre = req_json.get('ruta_padre')
        nuevo_hijo = req_json.get('nuevo_hijo', {})
        archivo_imagen = None

    if not ruta_padre or not nuevo_hijo:
        return jsonify({'status': 'error', 'msg': 'Faltan datos'}), 400

    if archivo_imagen and archivo_imagen.filename:
        filename, error = procesar_imagen(archivo_imagen)
        if error:
            return jsonify({'status': 'error', 'msg': error}), 400
        if filename:
            nuevo_hijo['imagen'] = filename

    if not nuevo_hijo.get('ruta_jerarquia'):
        nuevo_hijo['ruta_jerarquia'] = f"{ruta_padre}-{nuevo_hijo.get('nombre', 'nuevo')}"

    if 'sububicaciones' not in nuevo_hijo:
        nuevo_hijo['sububicaciones'] = []

    if encontrar_y_agregar(data, ruta_padre, nuevo_hijo):
        guardar_ubicaciones(data)
        return jsonify({'status': 'ok', 'msg': 'Sububicación agregada correctamente'})

    return jsonify({'status': 'no encontrado', 'msg': 'El padre no existe'}), 404