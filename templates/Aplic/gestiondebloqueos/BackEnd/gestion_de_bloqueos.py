from flask import Blueprint, render_template, request, jsonify
import json, os
from collections import defaultdict

gestion_de_bloqueos_bp = Blueprint('gestion_de_bloqueos', __name__)

# Archivo JSON
NODO_JSON = "Database/planos/nodo.json"

# -----------------------------
# Cargar / Guardar JSON
# -----------------------------
def cargar_nodos():
    if os.path.exists(NODO_JSON):
        with open(NODO_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Asegurar campo descripción en nodos existentes
            for n in data.values():
                if "descripcion" not in n:
                    n["descripcion"] = ""
            return data
    return {}

def guardar_nodos():
    with open(NODO_JSON, "w", encoding="utf-8") as f:
        json.dump(interruptores, f, ensure_ascii=False, indent=2)

# -----------------------------
# Estado en memoria
# -----------------------------
interruptores = cargar_nodos()
children_map = defaultdict(list)
for id_, n in interruptores.items():
    if n.get("padre"):
        children_map[n["padre"]].append(id_)

def get_root_id():
    roots = [i for i, data in interruptores.items() if data.get('padre') is None]
    return roots[0] if roots else None

def toggle_descendientes(id_, estado):
    """Apaga todos los descendientes si se apaga el nodo"""
    interruptores[id_]['estado'] = estado
    if estado == 'apagado':
        for hijo in children_map.get(id_, []):
            toggle_descendientes(hijo, estado)

# -----------------------------
# Rutas
# -----------------------------
@gestion_de_bloqueos_bp.route('/gestion_de_bloqueos')
def indexgestion_de_bloqueos():
    root = get_root_id()
    return render_template(
        'Aplic/gestiondebloqueos/FrontEnd/gestion_de_bloqueos.html',
        interruptores=interruptores,
        root_id=root
    )

@gestion_de_bloqueos_bp.route('/toggle_estado/<id>', methods=['POST'])
def toggle_estado(id):
    if id not in interruptores:
        return jsonify({'success': False, 'error': 'Nodo no encontrado'})
    nodo = interruptores[id]
    nuevo_estado = 'encendido' if nodo['estado'] == 'apagado' else 'apagado'

    # Solo puede encender si es raíz o si el padre está encendido
    padre_id = nodo.get('padre')
    if nuevo_estado == 'encendido' and padre_id and interruptores[padre_id]['estado'] != 'encendido':
        return jsonify({'success': False, 'error': 'No se puede encender porque el padre está apagado'})

    toggle_descendientes(id, nuevo_estado)
    guardar_nodos()
    return jsonify({'success': True, 'estado': interruptores[id]['estado']})

@gestion_de_bloqueos_bp.route('/agregar_interruptor', methods=['POST'])
def agregar_interruptor():
    data = request.json or {}
    nombre = data.get('nombre', 'Nuevo Nodo')
    padre = data.get('padre')
    nuevo_id = str(len(interruptores) + 1)
    interruptores[nuevo_id] = {'id': nuevo_id, 'nombre': nombre, 'estado': 'apagado', 'padre': padre, 'descripcion': ''}
    if padre:
        children_map[padre].append(nuevo_id)
    guardar_nodos()
    return jsonify({'success': True, 'id': nuevo_id, 'data': interruptores[nuevo_id]})

@gestion_de_bloqueos_bp.route('/editar_interruptor/<id>', methods=['POST'])
def editar_interruptor(id):
    if id not in interruptores:
        return jsonify({'success': False, 'error': 'Nodo no encontrado'})
    data = request.json or {}
    interruptores[id]['nombre'] = data.get('nombre', interruptores[id]['nombre'])
    interruptores[id]['estado'] = data.get('estado', interruptores[id]['estado'])
    interruptores[id]['padre'] = data.get('padre', interruptores[id]['padre'])
    interruptores[id]['descripcion'] = data.get('descripcion', interruptores[id]['descripcion'])
    guardar_nodos()
    return jsonify({'success': True, 'id': id, 'data': interruptores[id]})

@gestion_de_bloqueos_bp.route('/borrar_interruptor/<id>', methods=['POST'])
def borrar_interruptor(id):
    if id not in interruptores:
        return jsonify({'success': False, 'error': 'Nodo no encontrado'})
    padre = interruptores[id].get('padre')
    if padre and id in children_map[padre]:
        children_map[padre].remove(id)
    del interruptores[id]
    if id in children_map:
        del children_map[id]
    guardar_nodos()
    return jsonify({'success': True, 'id': id})

@gestion_de_bloqueos_bp.route('/mover_interruptor', methods=['POST'])
def mover_interruptor():
    data = request.json or {}
    id_ = data.get('id')
    nuevo_padre = data.get('nuevo_padre') or None
    if id_ not in interruptores:
        return jsonify({'success': False, 'error': 'Nodo no encontrado'})
    viejo_padre = interruptores[id_].get('padre')
    if viejo_padre and id_ in children_map[viejo_padre]:
        children_map[viejo_padre].remove(id_)
    interruptores[id_]['padre'] = nuevo_padre
    if nuevo_padre:
        children_map[nuevo_padre].append(id_)
    guardar_nodos()
    return jsonify({'success': True, 'id': id_, 'nuevo_padre': nuevo_padre})
