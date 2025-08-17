from flask_login import login_required, current_user
from menu import cargar_menu
from login import roles_required
from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, current_app
import json, re, os


procedim_bp = Blueprint('indexProcedim', __name__)
DATA_FILE = 'DataBase/dataOT/procedimiento.json'


@procedim_bp.route("/crearProc")
@login_required
@roles_required('viewer')
def indexProcedim():
    nemu = cargar_menu()
    return render_template('Aplic/crearprocedimiento/FrontEnd/crearprocedimiento.html',nemu=nemu, roles=current_user.roles)


###################################
#      CRUD DE PROCEDIMIENTO      #
###################################


# Función crear procedimiento
@procedim_bp.route("/api/proce", methods=["POST"])
def crear_proce():
    datos = request.get_json()
    nombre = datos.get("nombre")
    emoji = datos.get("emoji")
    ruta_menu = datos.get("ruta", "")
    ruta_padre = datos.get("ruta_padre", "")
    if not nombre or not emoji:
        return jsonify({"msg": "Faltan datos"}), 400

    data = cargar_procedim()
    padre = buscar_nodo_por_ruta(data, ruta_padre)
    if padre is None:
        return jsonify({"msg": "Ruta padre inválida"}), 400

    nuevo_proce= {
        "nombre": nombre,
        "emoji": emoji,
        "ruta": ruta_menu,
        "submenues": []
    }

    if isinstance(padre, list):
        if any(item["nombre"] == nombre for item in padre):
            return jsonify({"msg": "El menú ya existe"}), 400
        padre.append(nuevo_proce)
    elif isinstance(padre, dict):
        if any(item["nombre"] == nombre for item in padre.get("submenues", [])):
            return jsonify({"msg": "El submenú ya existe"}), 400
        padre.setdefault("submenues", []).append(nuevo_proce)
    else:
        return jsonify({"msg": "Error inesperado"}), 400

    guardar_procedim(data)
    return jsonify({"msg": "Menú creado correctamente"})

# Función listar procedimiento
@procedim_bp.route("/api/proce_arbol", methods=["GET"])
def obtener_arbol_menu():
    def construir_arbol(menus, ruta_padre=""):
        resultado = []
        for menu in menus:
            ruta_actual = f"{ruta_padre}||{menu['nombre']}" if ruta_padre else menu['nombre']
            nodo = {
                "nombre": menu['nombre'],
                "emoji": menu['emoji'],
                "ruta": menu.get("ruta", ""),
                "ruta_jerarquia": ruta_actual,
                "submenues": construir_arbol(menu.get('submenues', []), ruta_actual)
            }
            resultado.append(nodo)
        return resultado
    data = cargar_procedim()
    return jsonify(construir_arbol(data))

# Función editar procedimiento
@procedim_bp.route("/api/proce", methods=["PUT"])
def editar_proce():
    datos = request.get_json()
    ruta_jerarquia = datos.get("ruta")
    nombre = datos.get("nombre")
    emoji = datos.get("emoji")
    ruta_menu = datos.get("ruta_menu", "")

    if not ruta_jerarquia or not nombre or not emoji:
        return jsonify({"msg": "Faltan datos"}), 400

    data = cargar_procedim()
    partes = ruta_jerarquia.split("||")
    padre_ruta = "||".join(partes[:-1])
    nombre_a_buscar = normalizar_nombre(partes[-1])

    padre = buscar_nodo_por_ruta(data, padre_ruta)
    if padre is None:
        return jsonify({"msg": "Ruta inválida"}), 400

    if isinstance(padre, list):
        nodo = next((item for item in padre if normalizar_nombre(item.get("nombre", "")) == nombre_a_buscar), None)
    else:
        nodo = next((item for item in padre.get("submenues", []) if normalizar_nombre(item.get("nombre", "")) == nombre_a_buscar), None)

    if nodo is None:
        return jsonify({"msg": "Ítem no encontrado"}), 404

    # Validar nombre duplicado
    nombre_normalizado = normalizar_nombre(nombre)
    coleccion = padre.get("submenues", []) if isinstance(padre, dict) else padre
    for item in coleccion:
        if normalizar_nombre(item.get("nombre", "")) == nombre_normalizado and item is not nodo:
            return jsonify({"msg": "Ya existe un menú con ese nombre en este nivel"}), 400

    nodo["nombre"] = nombre
    nodo["emoji"] = emoji
    nodo["ruta"] = ruta_menu
    guardar_procedim(data)
    return jsonify({"msg": "Menú actualizado correctamente"})



# Función eliminar procedimiento
# Función eliminar procedimiento
@procedim_bp.route("/api/proce", methods=["DELETE"])
def eliminar_proce():
    datos = request.get_json()
    ruta = datos.get("ruta")

    if not ruta:
        return jsonify({"msg": "Ruta requerida"}), 400

    data = cargar_procedim()
    eliminado = eliminar_nodo_recursivo(data, ruta)

    if eliminado:
        guardar_procedim(data)
        return jsonify({"msg": "Ítem eliminado correctamente"}), 200
    else:
        return jsonify({"msg": "Ítem no encontrado"}), 404





###################################
#    FIN DE CRUD                  #
###################################


# Funciones de procedimiento

def cargar_procedim():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []
    
def guardar_procedim(proce):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(proce, f, ensure_ascii=False, indent=4)

def buscar_nodo_por_ruta(data, ruta):
    if not ruta:
        return data
    partes = ruta.split('||')
    nodo = data
    for parte in partes:
        nombre_normalizado = normalizar_nombre(parte)
        if isinstance(nodo, list):
            nodo = next(
                (item for item in nodo if normalizar_nombre(item.get('nombre', '')) == nombre_normalizado),
                None
            )
        elif isinstance(nodo, dict):
            nodo = next(
                (item for item in nodo.get('submenues', []) if normalizar_nombre(item.get('nombre', '')) == nombre_normalizado),
                None
            )
        else:
            return None
        if nodo is None:
            return None
    return nodo



def normalizar_nombre(texto):
    if not isinstance(texto, str):
        return ''
    return ' '.join(texto.strip().replace('\n', ' ').replace('\r', ' ').split()).lower()



def buscar_nodo_por_ruta(data, ruta):
    if not ruta:
        return data
    partes = ruta.split('||')
    nodo = data
    for parte in partes:
        parte_norm = normalizar_nombre(parte)
        if isinstance(nodo, list):
            nodo = next((item for item in nodo if normalizar_nombre(item.get("nombre", "")) == parte_norm), None)
        elif isinstance(nodo, dict):
            nodo = next((item for item in nodo.get("submenues", []) if normalizar_nombre(item.get("nombre", "")) == parte_norm), None)
        else:
            return None
        if nodo is None:
            return None
    return nodo


def eliminar_nodo_recursivo(lista_nodos, ruta_completa):
    partes = ruta_completa.split("||")
    if not partes:
        return False

    nombre_objetivo = normalizar_nombre(partes[0])

    for i, nodo in enumerate(lista_nodos):
        nombre_nodo = normalizar_nombre(nodo.get("nombre", ""))
        if nombre_nodo == nombre_objetivo:
            if len(partes) == 1:
                # Nodo a eliminar encontrado
                del lista_nodos[i]
                return True
            else:
                # Buscar en submenues recursivamente con la ruta restante
                if "submenues" in nodo:
                    eliminado = eliminar_nodo_recursivo(nodo["submenues"], "||".join(partes[1:]))
                    if eliminado:
                        return True
    return False

