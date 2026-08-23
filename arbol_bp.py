"""
Módulo genérico: CRUD de árboles jerárquicos en JSON.

Reutilizado por: crear_almacenes y crear_ubicacion_tecnica.
(crear_rubros usa lógica diferente y NO usa este módulo.)

Uso:
    from arbol_bp import crear_blueprint_arbol
    bp = crear_blueprint_arbol(nombre_bp=..., data_file=..., ...)
"""
import json
import os

from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from menu import cargar_menu
from login import roles_required


# =========================================================
# Operaciones genéricas sobre el árbol (lista anidada)
# =========================================================
def agregar_nodo(nodos, nombre, emoji, ruta, ruta_padre, clave_hijos):
    """Agrega un nodo bajo 'ruta_padre'. Retorna True si tuvo éxito."""
    partes = ruta_padre.split('-') if ruta_padre else []
    actual = nodos
    for parte in partes:
        nodo = next((u for u in actual if u['nombre'] == parte), None)
        if not nodo:
            return False
        if clave_hijos not in nodo:
            nodo[clave_hijos] = []
        actual = nodo[clave_hijos]

    nuevo = {
        'nombre': nombre,
        'emoji': emoji,
        'ruta': ruta,
        'ruta_jerarquia': f"{ruta_padre + '-' if ruta_padre else ''}{nombre}",
        clave_hijos: []
    }
    actual.append(nuevo)
    return True


def buscar_y_actualizar(nodos, ruta, nuevos_datos, clave_hijos):
    """Busca el nodo con 'ruta_jerarquia' == ruta y lo actualiza."""
    for nodo in nodos:
        if nodo['ruta_jerarquia'] == ruta:
            nodo.update(nuevos_datos)
            return True
        if clave_hijos in nodo:
            if buscar_y_actualizar(nodo[clave_hijos], ruta, nuevos_datos, clave_hijos):
                return True
    return False


def eliminar_nodo(nodos, ruta, clave_hijos):
    """Elimina el nodo con 'ruta_jerarquia' == ruta."""
    for i, nodo in enumerate(nodos):
        if nodo['ruta_jerarquia'] == ruta:
            nodos.pop(i)
            return True
        if clave_hijos in nodo:
            if eliminar_nodo(nodo[clave_hijos], ruta, clave_hijos):
                return True
    return False


# =========================================================
# Factory de Blueprint CRUD jerárquico
# =========================================================
def crear_blueprint_arbol(
    nombre_bp,
    data_file,
    template,
    vista_url,
    clave_hijos,
    api_arbol_url,
    api_crud_url,
    item_nombre,
    campo_ruta_payload,
    endpoint_vista,
    msg_agregar='Ubicación agregada correctamente',
):
    """Crea un blueprint con vista + API (GET arbol, POST, PUT, DELETE).

    Mantiene las mismas URLs y comportamiento que los blueprints originales.
    """
    bp = Blueprint(nombre_bp, __name__)

    # ----- Persistencia (captura data_file) -----
    def cargar_datos():
        if not os.path.exists(data_file):
            return []
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def guardar_datos(data):
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # ----- Vista principal -----
    @bp.route(vista_url, endpoint=endpoint_vista)
    @login_required
    @roles_required('viewer')
    def vista_principal():
        nemu = cargar_menu()
        return render_template(template, nemu=nemu, roles=current_user.roles)

    # ----- API: leer árbol -----
    @bp.route(api_arbol_url, endpoint='api_arbol')
    @login_required
    @roles_required('viewer')
    def api_arbol():
        return jsonify(cargar_datos())

    # ----- API: crear -----
    @bp.route(api_crud_url, methods=['POST'], endpoint='api_crear')
    @login_required
    @roles_required('viewer')
    def api_crear():
        datos = cargar_datos()
        payload = request.get_json()
        nombre = payload.get('nombre')
        emoji = payload.get('emoji')
        ruta = payload.get('ruta', '')
        ruta_padre = payload.get('ruta_padre', '')

        if not nombre or not emoji:
            return jsonify({'msg': 'Faltan campos obligatorios'}), 400

        exito = agregar_nodo(datos, nombre, emoji, ruta, ruta_padre, clave_hijos)
        if not exito:
            return jsonify({'msg': 'No se encontró el padre para agregar el ítem'}), 400

        guardar_datos(datos)
        return jsonify({'msg': msg_agregar})

    # ----- API: editar -----
    @bp.route(api_crud_url, methods=['PUT'], endpoint='api_editar')
    @login_required
    @roles_required('viewer')
    def api_editar():
        datos = cargar_datos()
        payload = request.get_json()
        ruta_original = payload.get('ruta')
        nombre = payload.get('nombre')
        emoji = payload.get('emoji')
        ruta_item = payload.get(campo_ruta_payload, '')

        if not ruta_original or not nombre or not emoji:
            return jsonify({'msg': 'Faltan campos obligatorios'}), 400

        partes = ruta_original.split('-')
        nueva_ruta = '-'.join(partes[:-1] + [nombre])
        nuevos_datos = {
            'nombre': nombre,
            'emoji': emoji,
            'ruta': ruta_item,
            'ruta_jerarquia': nueva_ruta
        }

        exito = buscar_y_actualizar(datos, ruta_original, nuevos_datos, clave_hijos)
        if not exito:
            return jsonify({'msg': f'No se encontró el {item_nombre} a editar'}), 400

        guardar_datos(datos)
        return jsonify({'msg': f'{item_nombre.capitalize()} actualizado correctamente'})

    # ----- API: eliminar -----
    @bp.route(api_crud_url, methods=['DELETE'], endpoint='api_eliminar')
    @login_required
    @roles_required('viewer')
    def api_eliminar():
        datos = cargar_datos()
        payload = request.get_json()
        ruta = payload.get('ruta')

        if not ruta:
            return jsonify({'msg': 'Ruta no proporcionada'}), 400

        exito = eliminar_nodo(datos, ruta, clave_hijos)
        if not exito:
            return jsonify({'msg': f'No se encontró el {item_nombre} a eliminar'}), 400

        guardar_datos(datos)
        return jsonify({'msg': f'{item_nombre.capitalize()} eliminado correctamente'})

    return bp