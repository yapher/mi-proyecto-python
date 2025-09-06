from flask import Blueprint, request, jsonify, current_app
import os, json, unicodedata, re
from menu import cargar_menu, guardar_menu

menu_api = Blueprint('menu_api', __name__)


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

# --- Rutas API menú (tu código original) ---

@menu_api.route("/api/menu", methods=["GET"])
def listar_menus():
    data = cargar_menu()
    items = [{"nombre": v["nombre"], "emoji": v["emoji"], "ruta": v.get("ruta", "")} for v in data]
    return jsonify(items)

@menu_api.route("/api/menu_list", methods=["GET"])
def listar_menu():
    data = cargar_menu()
    return jsonify(data)

@menu_api.route("/api/menu", methods=["POST"])
def crear_menu():
    datos = request.get_json()
    nombre = datos.get("nombre")
    emoji = datos.get("emoji")
    ruta_menu = datos.get("ruta", "")
    ruta_padre = datos.get("ruta_padre", "")
    if not nombre or not emoji:
        return jsonify({"msg": "Faltan datos"}), 400

    data = cargar_menu()
    padre = buscar_nodo_por_ruta(data, ruta_padre)
    if padre is None:
        return jsonify({"msg": "Ruta padre inválida"}), 400

    nuevo_menu = {
        "nombre": nombre,
        "emoji": emoji,
        "ruta": ruta_menu,
        "submenues": []
    }

    if isinstance(padre, list):
        if any(item["nombre"] == nombre for item in padre):
            return jsonify({"msg": "El menú ya existe"}), 400
        padre.append(nuevo_menu)
    elif isinstance(padre, dict):
        if any(item["nombre"] == nombre for item in padre.get("submenues", [])):
            return jsonify({"msg": "El submenú ya existe"}), 400
        padre.setdefault("submenues", []).append(nuevo_menu)
    else:
        return jsonify({"msg": "Error inesperado"}), 400

    guardar_menu(data)
    return jsonify({"msg": "Menú creado correctamente"})

@menu_api.route("/api/menu", methods=["PUT"])
def editar_menu():
    datos = request.get_json()
    ruta_jerarquia = datos.get("ruta")
    nombre = datos.get("nombre")
    emoji = datos.get("emoji")
    ruta_menu = datos.get("ruta_menu", "")

    if not ruta_jerarquia or not nombre or not emoji:
        return jsonify({"msg": "Faltan datos"}), 400

    data = cargar_menu()
    partes = ruta_jerarquia.split('.')
    padre_ruta = '.'.join(partes[:-1])
    padre = buscar_nodo_por_ruta(data, padre_ruta)
    if padre is None:
        return jsonify({"msg": "Ruta inválida"}), 400

    if isinstance(padre, list):
        nodo = next((item for item in padre if item["nombre"] == partes[-1]), None)
    else:
        nodo = next((item for item in padre.get("submenues", []) if item["nombre"] == partes[-1]), None)

    if nodo is None:
        return jsonify({"msg": "Ítem no encontrado"}), 404

    nodo["nombre"] = nombre
    nodo["emoji"] = emoji
    nodo["ruta"] = ruta_menu
    guardar_menu(data)
    return jsonify({"msg": "Menú actualizado correctamente"})

@menu_api.route("/api/menu", methods=["DELETE"])
def eliminar_menu():
    datos = request.get_json()
    ruta = datos.get("ruta")
    if not ruta:
        return jsonify({"msg": "Ruta requerida"}), 400

    data = cargar_menu()
    partes = ruta.split('.')
    padre_ruta = '.'.join(partes[:-1])
    padre = buscar_nodo_por_ruta(data, padre_ruta)
    if padre is None:
        return jsonify({"msg": "Ruta inválida"}), 400

    if isinstance(padre, list):
        padre[:] = [item for item in padre if item["nombre"] != partes[-1]]
    else:
        padre["submenues"] = [item for item in padre.get("submenues", []) if item["nombre"] != partes[-1]]

    guardar_menu(data)
    return jsonify({"msg": "Menú eliminado correctamente"})

@menu_api.route("/api/menu_arbol", methods=["GET"])
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
    data = cargar_menu()
    return jsonify(construir_arbol(data))

# --- Nueva ruta para crear estructura de carpetas y archivos ---

def slugify(text):
    text = text.lower()
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'\s+', '', text)  # elimina espacios para carpeta
    return text

def snake_case(text):
    text = text.lower()
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'\s+', '_', text)
    text = re.sub(r'[^a-z0-9_]', '', text)
    return text

@menu_api.route('/crear_app', methods=['POST'])
def crear_app():
    data = request.get_json()
    nombre = data.get('nombre', '').strip()

    if not nombre:
        return jsonify({"msg": "El nombre es obligatorio"}), 400

    nombre_carpeta = slugify(nombre)
    nombre_archivo = snake_case(nombre)

    nomBreBlue  = f"{nombre_archivo}_bp"
    nombreIndex = f"index{nombre_archivo}"

    # Ruta base para crear carpetas dentro de templates/Aplic
    base_path = os.path.join(current_app.root_path, 'templates', 'Aplic')
    ruta_app = os.path.join(base_path, nombre_carpeta)
    ruta_backend = os.path.join(ruta_app, 'BackEnd')
    ruta_frontend = os.path.join(ruta_app, 'FrontEnd')
    
    # Ruta para archivos CSS en static/css/apps
    ruta_css = os.path.join(current_app.root_path, 'static', 'css', 'apps')

    try:
        os.makedirs(ruta_backend, exist_ok=True)
        os.makedirs(ruta_frontend, exist_ok=True)
        os.makedirs(ruta_css, exist_ok=True)

        # Archivo Python en BackEnd
        archivo_py = os.path.join(ruta_backend, f'{nombre_archivo}.py')
        if not os.path.exists(archivo_py):
            with open(archivo_py, 'w', encoding='utf-8') as f:
                f.write('# Archivo backend generado automáticamente\n\n')

                f.write('from flask_login import login_required, current_user\n')
                f.write('from menu import cargar_menu\n')
                f.write('from login import roles_required\n')
                f.write('from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, current_app\n')
                f.write('import json, re, os\n\n')
                f.write(f"{nomBreBlue} = Blueprint('{nombreIndex}', __name__)\n\n")
                f.write('# Copiar y pegar estas dos linea en app.py\n')
                f.write(f"#from templates.Aplic.{nombre_carpeta}.BackEnd.{nombre_archivo} import {nomBreBlue}\n")
                f.write(f"#app.register_blueprint({nomBreBlue})\n\n")
                f.write(f"@{nomBreBlue}.route('/{nombre_archivo}')\n")
                f.write('@login_required\n')
                f.write("@roles_required('viewer')\n")
                f.write(f'def {nombreIndex}():\n')
                f.write('    nemu = cargar_menu()\n')
                f.write(f"    return render_template('Aplic/{nombre_carpeta}/FrontEnd/{nombre_archivo}.html',nemu=nemu, roles=current_user.roles)\n")
               

        # Archivo HTML en FrontEnd
        archivo_html = os.path.join(ruta_frontend, f'{nombre_archivo}.html')
        if not os.path.exists(archivo_html):
            with open(archivo_html, 'w', encoding='utf-8') as f:
                f.write('{% extends \'layout.html\' %}\n')
                f.write('{% block head %}\n')
                f.write(f'<link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/apps/{nombre_archivo}.css\') }}">\n')
                f.write('{% endblock %}\n')
                f.write('{% block content %}\n')
                f.write(f'<div class="{nombre_archivo}-container">\n')
                f.write(f'    <div class="{nombre_archivo}-header">\n')
                f.write(f'        <h3 class="mb-3">{nombre}</h3>\n')
                f.write(f'    </div>\n')
                f.write(f'    <!-- Contenido de la aplicación -->\n')
                f.write(f'</div>\n')
                f.write('{% endblock %}\n')
                f.write('\n')
                f.write('{% block scripts %}\n')
                f.write(f'<script src="{{ url_for(\'static\', filename=\'js/apps/{nombre_archivo}.js\') }}"></script>\n')
                f.write('{% endblock %}\n')

        # Archivo CSS en static/css/apps
        archivo_css = os.path.join(ruta_css, f'{nombre_archivo}.css')
        if not os.path.exists(archivo_css):
            with open(archivo_css, 'w', encoding='utf-8') as f:
                f.write(f'/* Estilos para el componente {nombre} */\n\n')
                f.write(f'/* Contenedor principal */\n')
                f.write(f'.{nombre_archivo}-container {{\n')
                f.write(f'    max-width: 1200px;\n')
                f.write(f'    margin: 0 auto;\n')
                f.write(f'    padding: 1rem;\n')
                f.write(f'}}\n\n')
                f.write(f'/* Header de la aplicación */\n')
                f.write(f'.{nombre_archivo}-header {{\n')
                f.write(f'    margin-bottom: 2rem;\n')
                f.write(f'    text-align: center;\n')
                f.write(f'}}\n\n')
                f.write(f'.{nombre_archivo}-header h3 {{\n')
                f.write(f'    color: #343a40;\n')
                f.write(f'    font-weight: 600;\n')
                f.write(f'    margin-bottom: 0.5rem;\n')
                f.write(f'}}\n\n')
                f.write(f'/* Estilos para formularios */\n')
                f.write(f'.{nombre_archivo}-form {{\n')
                f.write(f'    background-color: #f8f9fa;\n')
                f.write(f'    padding: 1.5rem;\n')
                f.write(f'    border-radius: 0.5rem;\n')
                f.write(f'    margin-bottom: 2rem;\n')
                f.write(f'}}\n\n')
                f.write(f'/* Estilos para tablas */\n')
                f.write(f'.{nombre_archivo}-tabla {{\n')
                f.write(f'    background-color: #fff;\n')
                f.write(f'    border-radius: 0.5rem;\n')
                f.write(f'    overflow: hidden;\n')
                f.write(f'    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);\n')
                f.write(f'}}\n\n')
                f.write(f'/* Responsive design */\n')
                f.write(f'@media (max-width: 768px) {{\n')
                f.write(f'    .{nombre_archivo}-container {{\n')
                f.write(f'        padding: 0.5rem;\n')
                f.write(f'    }}\n')
                f.write(f'    \n')
                f.write(f'    .{nombre_archivo}-form {{\n')
                f.write(f'        padding: 1rem;\n')
                f.write(f'    }}\n')
                f.write(f'}}\n')

        # Archivo JavaScript en static/js/apps
        ruta_js = os.path.join(current_app.root_path, 'static', 'js', 'apps')
        os.makedirs(ruta_js, exist_ok=True)
        archivo_js = os.path.join(ruta_js, f'{nombre_archivo}.js')
        if not os.path.exists(archivo_js):
            with open(archivo_js, 'w', encoding='utf-8') as f:
                f.write(f'/**\n')
                f.write(f' * JavaScript para el componente {nombre}\n')
                f.write(f' * Maneja la funcionalidad específica de esta aplicación\n')
                f.write(f' */\n\n')
                f.write(f'// Inicialización cuando el DOM esté listo\n')
                f.write(f'document.addEventListener("DOMContentLoaded", function() {{\n')
                f.write(f'    console.log("Componente {nombre} inicializado");\n')
                f.write(f'    \n')
                f.write(f'    // Aquí puedes agregar la lógica específica de tu aplicación\n')
                f.write(f'    // Ejemplo:\n')
                f.write(f'    // const container = document.querySelector(".{nombre_archivo}-container");\n')
                f.write(f'    // if (container) {{\n')
                f.write(f'    //     // Tu código aquí\n')
                f.write(f'    // }}\n')
                f.write(f'}});\n\n')
                f.write(f'/**\n')
                f.write(f' * Función de ejemplo para manejar eventos\n')
                f.write(f' */\n')
                f.write(f'function handleExampleEvent() {{\n')
                f.write(f'    console.log("Evento manejado en {nombre}");\n')
                f.write(f'    // Implementar lógica específica\n')
                f.write(f'}}\n\n')
                f.write(f'/**\n')
                f.write(f' * Función para validar formularios\n')
                f.write(f' */\n')
                f.write(f'function validateForm() {{\n')
                f.write(f'    // Implementar validaciones específicas\n')
                f.write(f'    return true;\n')
                f.write(f'}}\n\n')
                f.write(f'/**\n')
                f.write(f' * Función para hacer peticiones a la API\n')
                f.write(f' */\n')
                f.write(f'async function fetchData() {{\n')
                f.write(f'    try {{\n')
                f.write(f'        const response = await fetch("/api/{nombre_archivo}");\n')
                f.write(f'        const data = await response.json();\n')
                f.write(f'        return data;\n')
                f.write(f'    }} catch (error) {{\n')
                f.write(f'        console.error("Error al obtener datos:", error);\n')
                f.write(f'        return null;\n')
                f.write(f'    }}\n')
                f.write(f'}}\n')

        return jsonify({"msg": f"Estructura creada para '{nombre}' correctamente."})

    except Exception as e:
        return jsonify({"msg": f"Error al crear la estructura: {str(e)}"}), 500
