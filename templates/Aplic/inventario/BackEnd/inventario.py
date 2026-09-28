# templates/Aplic/inventario/BackEnd/inventario.py
"""
Blueprint de Inventario — VERSIÓN SQL
Incluye CRUD de almacenes (antes en crear_almacenes)
"""
from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from core.menu import cargar_menu
from auth.login import roles_required
from core.repuestos import (
    cargar_todos_repuestos,
    construir_mapeo_repuestos_por_almacen,
)
from core.data_loaders import (
    cargar_ubicaciones,
    cargar_estados,
    cargar_almacenes,
    obtener_nombres_almacenes,
)
from core.db_sql_store import almacen_store

inventario_bp = Blueprint(
    'indexinventario',
    __name__,
    static_folder='../static',
    static_url_path='/inventario/static'
)

# ============================================================
# VISTA PRINCIPAL
# ============================================================
@inventario_bp.route('/inventario')
@login_required
@roles_required('viewer')
def indexinventario():
    nemu = cargar_menu()
    repuestos = cargar_todos_repuestos()
    ubicaciones = cargar_ubicaciones()
    almacenes = cargar_almacenes()
    nombres_almacenes = obtener_nombres_almacenes(almacenes)
    estados = cargar_estados()
    repuestos_por_equipo = construir_mapeo_repuestos_por_almacen(
        repuestos=repuestos,
        almacenes=almacenes
    )
    return render_template(
        'Aplic/inventario/FrontEnd/inventario.html',
        nemu=nemu,
        roles=current_user.roles,
        almacenes=almacenes,
        repuestos_por_equipo=repuestos_por_equipo,
        ubicaciones=ubicaciones,
        estados=estados,
        nombres_almacenes=nombres_almacenes,
    )

# ============================================================
# API: CRUD DE ALMACENES (antes en crear_almacenes)
# ============================================================

@inventario_bp.route('/api/inventario/almacenes_arbol', methods=['GET'])
@login_required
@roles_required('viewer')
def api_almacenes_arbol():
    """Retorna el árbol completo de almacenes."""
    arbol = almacen_store.cargar_arbol()
    return jsonify(arbol)


@inventario_bp.route('/api/inventario/almacenes', methods=['POST'])
@login_required
@roles_required('viewer')
def api_almacenes_crear():
    """Crear un nuevo nodo de almacén."""
    payload = request.get_json() or {}
    nombre = (payload.get('nombre') or '').strip()
    emoji = (payload.get('emoji') or '').strip()
    ruta = payload.get('ruta', '')
    ruta_padre = payload.get('ruta_padre', '')

    if not nombre or not emoji:
        return jsonify({'msg': 'Faltan campos obligatorios', 'type': 'error'}), 400

    exito, msg = almacen_store.agregar(nombre, emoji, ruta, ruta_padre)
    if not exito:
        return jsonify({'msg': msg, 'type': 'error'}), 400

    return jsonify({'msg': 'Almacén agregado correctamente', 'type': 'success'})


@inventario_bp.route('/api/inventario/almacenes', methods=['PUT'])
@login_required
@roles_required('viewer')
def api_almacenes_editar():
    """Editar un nodo de almacén existente."""
    payload = request.get_json() or {}
    ruta_original = (
        payload.get('ruta_original') or
        payload.get('ruta') or
        payload.get('ruta_jerarquia')
    )
    nombre = (payload.get('nombre') or '').strip()
    emoji = (payload.get('emoji') or '').strip()
    ruta_item = payload.get('ruta_crear_almacenes', '')

    if not ruta_original:
        return jsonify({'msg': 'Falta ruta_original', 'type': 'error'}), 400
    if not nombre or not emoji:
        return jsonify({'msg': 'Faltan campos obligatorios', 'type': 'error'}), 400

    nuevos_datos = {
        'nombre': nombre,
        'emoji': emoji,
        'ruta': ruta_item
    }
    exito, msg = almacen_store.editar(ruta_original, nuevos_datos)
    if not exito:
        return jsonify({
            'msg': f'No se encontró el almacén con ruta "{ruta_original}"',
            'type': 'error'
        }), 404

    return jsonify({
        'msg': 'Almacén actualizado correctamente',
        'type': 'success'
    })


@inventario_bp.route('/api/inventario/almacenes', methods=['DELETE'])
@login_required
@roles_required('viewer')
def api_almacenes_eliminar():
    """Eliminar un nodo de almacén y sus descendientes."""
    payload = request.get_json() or {}
    ruta = payload.get('ruta') or payload.get('ruta_jerarquia')

    if not ruta:
        return jsonify({'msg': 'Ruta requerida', 'type': 'error'}), 400

    exito, msg = almacen_store.eliminar(ruta)
    if not exito:
        return jsonify({'msg': 'No se encontró el almacén', 'type': 'error'}), 404

    return jsonify({
        'msg': 'Almacén eliminado correctamente',
        'type': 'success'
    })