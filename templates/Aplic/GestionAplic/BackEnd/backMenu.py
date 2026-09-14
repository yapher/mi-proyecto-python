"""
Blueprint de Gestión de Menú y Aplicaciones - VERSIÓN SQL
"""
from flask import Blueprint, request, jsonify, current_app
import os
import unicodedata
import re
from core.menu import cargar_menu, guardar_menu
from core.db_sql_store import menu_store

_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_STATIC_DIR = os.path.abspath(os.path.join(_APP_DIR, '..', 'static'))

menu_api = Blueprint(
    'menu_api',
    __name__,
    static_folder=_STATIC_DIR,
    static_url_path='/gestionaplic/static'
)


def buscar_nodo_por_ruta(data, ruta):
    """Busca un nodo en el árbol por su ruta jerárquica."""
    if not ruta:
        return data
    partes = ruta.split('.')
    nodo = data
    for parte in partes:
        if isinstance(nodo, list):
            nodo = next((item for item in nodo if item['nombre'] == parte), None)
        elif isinstance(nodo, dict):
            nodo = next(
                (item for item in nodo.get('submenues', []) if item['nombre'] == parte),
                None
            )
        else:
            return None
        if nodo is None:
            return None
    return nodo


@menu_api.route("/api/menu", methods=["GET"])
def listar_menus():
    data = cargar_menu()
    items = [
        {"nombre": v["nombre"], "emoji": v["emoji"], "ruta": v.get("ruta", "")}
        for v in data
    ]
    return jsonify(items)


@menu_api.route("/api/menu_list", methods=["GET"])
def listar_menu():
    return jsonify(cargar_menu())


@menu_api.route("/api/menu", methods=["POST"])
def crear_menu():
    datos = request.get_json() or {}
    nombre = (datos.get("nombre") or "").strip()
    emoji = (datos.get("emoji") or "").strip()
    ruta_menu = datos.get("ruta", "")
    ruta_padre = datos.get("ruta_padre", "")

    if not nombre or not emoji:
        return jsonify({"msg": "Faltan datos"}), 400

    exito, msg = menu_store.agregar(nombre, emoji, ruta_menu, ruta_padre)
    if not exito:
        return jsonify({"msg": msg}), 400
    return jsonify({"msg": "Menú creado correctamente"})


@menu_api.route("/api/menu", methods=["PUT"])
def editar_menu():
    datos = request.get_json() or {}
    ruta_jerarquia = datos.get("ruta")
    nombre = (datos.get("nombre") or "").strip()
    emoji = (datos.get("emoji") or "").strip()
    ruta_menu = datos.get("ruta_menu", "")

    if not ruta_jerarquia or not nombre or not emoji:
        return jsonify({"msg": "Faltan datos"}), 400

    nuevos_datos = {
        'nombre': nombre,
        'emoji': emoji,
        'ruta': ruta_menu,
    }

    exito, msg = menu_store.editar(ruta_jerarquia, nuevos_datos)
    if not exito:
        return jsonify({"msg": msg}), 404
    return jsonify({"msg": "Menú actualizado correctamente"})


@menu_api.route("/api/menu", methods=["DELETE"])
def eliminar_menu():
    datos = request.get_json() or {}
    ruta = datos.get("ruta")
    if not ruta:
        return jsonify({"msg": "Ruta requerida"}), 400

    exito, msg = menu_store.eliminar(ruta)
    if not exito:
        return jsonify({"msg": msg}), 404
    return jsonify({"msg": "Menú eliminado correctamente"})


@menu_api.route("/api/menu_arbol", methods=["GET"])
def obtener_arbol_menu():
    return jsonify(menu_store.cargar_arbol())


# ============================================================
# CREAR ESTRUCTURA DE NUEVA APP
# ============================================================

def slugify(text):
    text = text.lower()
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'\s+', '', text)
    return text


def snake_case(text):
    text = text.lower()
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'\s+', '_', text)
    text = re.sub(r'[^a-z0-9_]', '', text)
    return text


@menu_api.route('/crear_app', methods=['POST'])
def crear_app():
    data = request.get_json() or {}
    nombre = data.get('nombre', '').strip()
    if not nombre:
        return jsonify({"msg": "El nombre es obligatorio"}), 400

    nombre_carpeta = slugify(nombre)
    nombre_archivo = snake_case(nombre)
    nomBreBlue = f"{nombre_archivo}_bp"

    base_path = os.path.join(current_app.root_path, 'templates', 'Aplic')
    ruta_app = os.path.join(base_path, nombre_carpeta)
    ruta_backend = os.path.join(ruta_app, 'BackEnd')
    ruta_frontend = os.path.join(ruta_app, 'FrontEnd')
    ruta_static_css = os.path.join(ruta_app, 'static', 'css')
    ruta_static_js = os.path.join(ruta_app, 'static', 'js')

    try:
        os.makedirs(ruta_backend, exist_ok=True)
        os.makedirs(ruta_frontend, exist_ok=True)
        os.makedirs(ruta_static_css, exist_ok=True)
        os.makedirs(ruta_static_js, exist_ok=True)

        # === Archivo Python ===
        archivo_py = os.path.join(ruta_backend, f'{nombre_archivo}.py')
        if not os.path.exists(archivo_py):
            with open(archivo_py, 'w', encoding='utf-8') as f:
                f.write('# Archivo backend generado automáticamente\n')
                f.write('from flask_login import login_required, current_user\n')
                f.write('from core.menu import cargar_menu\n')
                f.write('from auth.login import roles_required\n')
                f.write('from flask import Blueprint, render_template\n')
                f.write('import os\n\n')
                f.write('_APP_DIR = os.path.dirname(os.path.abspath(__file__))\n')
                f.write("_STATIC_DIR = os.path.abspath(os.path.join(_APP_DIR, '..', 'static'))\n\n")
                f.write(f"{nomBreBlue} = Blueprint(\n")
                f.write(f"    'index{nombre_archivo}',\n")
                f.write(f"    __name__,\n")
                f.write(f"    static_folder=_STATIC_DIR,\n")
                f.write(f"    static_url_path='/{nombre_carpeta}/static'\n")
                f.write(f")\n\n")
                f.write(f"@{nomBreBlue}.route('/{nombre_archivo}')\n")
                f.write('@login_required\n')
                f.write("@roles_required('viewer')\n")
                f.write(f'def index{nombre_archivo}():\n')
                f.write('    nemu = cargar_menu()\n')
                f.write(f"    return render_template(\n")
                f.write(f"        'Aplic/{nombre_carpeta}/FrontEnd/{nombre_archivo}.html',\n")
                f.write(f"        nemu=nemu, roles=current_user.roles)\n")

        # === Archivo HTML ===
        archivo_html = os.path.join(ruta_frontend, f'{nombre_archivo}.html')
        if not os.path.exists(archivo_html):
            with open(archivo_html, 'w', encoding='utf-8') as f:
                f.write("{% extends 'layout.html' %}\n")
                f.write("{% block head %}\n")
                f.write('<link rel="stylesheet" href="')
                f.write("{{ url_for('index" + nombre_archivo + ".static', filename='css/")
                f.write(nombre_archivo)
                f.write(".css') }}\">\n")
                f.write("{% endblock %}\n")
                f.write("{% block content %}\n")
                f.write(f'<div class="{nombre_archivo}-container">\n')
                f.write(f'    <h3 class="mb-3">{nombre}</h3>\n')
                f.write('</div>\n')
                f.write("{% endblock %}\n")
                f.write("{% block scripts %}\n")
                f.write('<script src="')
                f.write("{{ url_for('index" + nombre_archivo + ".static', filename='js/")
                f.write(nombre_archivo)
                f.write(".js') }}\"></script>\n")
                f.write("{% endblock %}\n")

        # === Archivo CSS ===
        archivo_css = os.path.join(ruta_static_css, f'{nombre_archivo}.css')
        if not os.path.exists(archivo_css):
            with open(archivo_css, 'w', encoding='utf-8') as f:
                f.write(f'/* Estilos para {nombre} */\n')
                f.write(f'.{nombre_archivo}-container {{\n')
                f.write('    max-width: 1200px;\n')
                f.write('    margin: 0 auto;\n')
                f.write('    padding: 1rem;\n')
                f.write('}\n')

        # === Archivo JS ===
        archivo_js = os.path.join(ruta_static_js, f'{nombre_archivo}.js')
        if not os.path.exists(archivo_js):
            with open(archivo_js, 'w', encoding='utf-8') as f:
                f.write(f'// JavaScript para {nombre}\n')
                f.write('document.addEventListener("DOMContentLoaded", function() {\n')
                f.write(f'    console.log("Componente {nombre} inicializado");\n')
                f.write('});\n')

        return jsonify({"msg": f"Estructura creada para '{nombre}' correctamente."})
    except Exception as e:
        return jsonify({"msg": f"Error al crear la estructura: {str(e)}"}), 500