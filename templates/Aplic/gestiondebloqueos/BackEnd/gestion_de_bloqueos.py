"""
Blueprint de Gestión de Bloqueos - VERSIÓN SQL
Ahora usa SQL en lugar de JSON.
"""
from flask import Blueprint, render_template, request, jsonify
from collections import defaultdict
from core.db_sql_store import nodo_bloqueo_store

gestion_de_bloqueos_bp = Blueprint('gestion_de_bloqueos', __name__)


def _construir_children_map():
    """Construye mapa de hijos desde los nodos en SQL."""
    interruptores = nodo_bloqueo_store.cargar_todos()
    children_map = defaultdict(list)
    for id_, n in interruptores.items():
        if n.get('padre'):
            children_map[n['padre']].append(id_)
    return interruptores, children_map


def get_root_id():
    """Obtiene el ID del nodo raíz."""
    interruptores = nodo_bloqueo_store.cargar_todos()
    roots = [i for i, data in interruptores.items() if data.get('padre') is None]
    return roots[0] if roots else None


def toggle_descendientes(id_, estado):
    """Apaga todos los descendientes si se apaga el nodo."""
    interruptores, children_map = _construir_children_map()
    nodo_bloqueo_store.actualizar(id_, {'estado': estado})
    if estado == 'apagado':
        for hijo in children_map.get(id_, []):
            toggle_descendientes(hijo, estado)


@gestion_de_bloqueos_bp.route('/gestion_de_bloqueos')
def indexgestion_de_bloqueos():
    interruptores = nodo_bloqueo_store.cargar_todos()
    root = get_root_id()
    return render_template(
        'Aplic/gestiondebloqueos/FrontEnd/gestion_de_bloqueos.html',
        interruptores=interruptores,
        root_id=root
    )


@gestion_de_bloqueos_bp.route('/toggle_estado/<id>', methods=['POST'])
def toggle_estado(id):
    nodo = nodo_bloqueo_store.obtener(id)
    if not nodo:
        return jsonify({'success': False, 'error': 'Nodo no encontrado'})

    nuevo_estado = 'encendido' if nodo['estado'] == 'apagado' else 'apagado'
    padre_id = nodo.get('padre')

    # Solo puede encender si es raíz o si el padre está encendido
    if nuevo_estado == 'encendido' and padre_id:
        padre = nodo_bloqueo_store.obtener(padre_id)
        if padre and padre['estado'] != 'encendido':
            return jsonify({
                'success': False,
                'error': 'No se puede encender porque el padre está apagado'
            })

    toggle_descendientes(id, nuevo_estado)
    actualizado = nodo_bloqueo_store.obtener(id)
    return jsonify({'success': True, 'estado': actualizado['estado']})


@gestion_de_bloqueos_bp.route('/agregar_interruptor', methods=['POST'])
def agregar_interruptor():
    data = request.json or {}
    nombre = data.get('nombre', 'Nuevo Nodo')
    padre = data.get('padre')
    nuevo_id, data_nodo = nodo_bloqueo_store.crear(nombre, padre)
    return jsonify({'success': True, 'id': nuevo_id, 'data': data_nodo})


@gestion_de_bloqueos_bp.route('/editar_interruptor/<id>', methods=['POST'])
def editar_interruptor(id):
    data = request.json or {}
    actualizado = nodo_bloqueo_store.actualizar(id, data)
    if not actualizado:
        return jsonify({'success': False, 'error': 'Nodo no encontrado'})
    return jsonify({'success': True, 'id': id, 'data': actualizado})


@gestion_de_bloqueos_bp.route('/borrar_interruptor/<id>', methods=['POST'])
def borrar_interruptor(id):
    if nodo_bloqueo_store.eliminar(id):
        return jsonify({'success': True, 'id': id})
    return jsonify({'success': False, 'error': 'Nodo no encontrado'})


@gestion_de_bloqueos_bp.route('/mover_interruptor', methods=['POST'])
def mover_interruptor():
    data = request.json or {}
    id_ = data.get('id')
    nuevo_padre = data.get('nuevo_padre') or None
    actualizado = nodo_bloqueo_store.actualizar(id_, {'padre': nuevo_padre})
    if not actualizado:
        return jsonify({'success': False, 'error': 'Nodo no encontrado'})
    return jsonify({'success': True, 'id': id_, 'nuevo_padre': nuevo_padre})