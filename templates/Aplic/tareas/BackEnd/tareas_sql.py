"""
Blueprint de Tareas - VERSIÓN SQL
Reemplaza a tareas.py (que usa JSON)
"""
from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from auth.login import roles_required
from core.menu import cargar_menu
from core.db_sql_store import tarea_store

tareas_bp_sql = Blueprint(
    'indextareas_sql',
    __name__,
    static_folder='../static',
    static_url_path='/tareas/static'
)

# ============================================================
# VISTA PRINCIPAL
# ============================================================
@tareas_bp_sql.route('/tareas')
@login_required
@roles_required('viewer')
def indextareas():
    nemu = cargar_menu()
    return render_template(
        'Aplic/tareas/FrontEnd/tareas.html',
        nemu=nemu,
        roles=current_user.roles
    )

# ============================================================
# API REST: Listar todas las tareas
# ============================================================
@tareas_bp_sql.route('/api/tareas', methods=['GET'])
@login_required
def listar_tareas():
    tareas = tarea_store.cargar()
    tareas_sorted = sorted(
        tareas,
        key=lambda t: t.get('fecha', ''),
        reverse=True
    )
    return jsonify(tareas_sorted)

# ============================================================
# API REST: Crear tarea
# ============================================================
@tareas_bp_sql.route('/api/tareas', methods=['POST'])
@login_required
@roles_required('viewer')
def crear_tarea():
    data = request.get_json() or {}
    titulo = (data.get('titulo') or '').strip()
    fecha = (data.get('fecha') or '').strip()
    if not titulo or not fecha:
        return jsonify({
            'status': 'error',
            'msg': 'Título y fecha son obligatorios'
        }), 400
    nueva_tarea = {
        'titulo': titulo,
        'fecha': fecha,
        'descripcion': (data.get('descripcion') or '').strip()
    }
    tarea_creada = tarea_store.agregar(nueva_tarea)
    return jsonify({
        'status': 'ok',
        'msg': 'Tarea creada correctamente',
        'item': tarea_creada
    }), 201

# ============================================================
# API REST: Actualizar tarea
# ============================================================
@tareas_bp_sql.route('/api/tareas/<int:tarea_id>', methods=['PUT'])
@login_required
@roles_required('viewer')
def actualizar_tarea(tarea_id):
    if not tarea_store.existe(tarea_id):
        return jsonify({
            'status': 'error',
            'msg': 'Tarea no encontrada'
        }), 404
    data = request.get_json() or {}
    nuevos_datos = {
        'titulo': (data.get('titulo') or '').strip(),
        'fecha': (data.get('fecha') or '').strip(),
        'descripcion': (data.get('descripcion') or '').strip()
    }
    if not nuevos_datos['titulo'] or not nuevos_datos['fecha']:
        return jsonify({
            'status': 'error',
            'msg': 'Título y fecha son obligatorios'
        }), 400
    tarea_store.editar(tarea_id, nuevos_datos)
    return jsonify({
        'status': 'ok',
        'msg': 'Tarea actualizada correctamente'
    })

# ============================================================
# API REST: Eliminar tarea
# ============================================================
@tareas_bp_sql.route('/api/tareas/<int:tarea_id>', methods=['DELETE'])
@login_required
@roles_required('viewer')
def eliminar_tarea(tarea_id):
    if not tarea_store.existe(tarea_id):
        return jsonify({
            'status': 'error',
            'msg': 'Tarea no encontrada'
        }), 404
    tarea_store.eliminar(tarea_id)
    return jsonify({
        'status': 'ok',
        'msg': 'Tarea eliminada correctamente'
    })