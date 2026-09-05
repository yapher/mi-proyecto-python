"""
Blueprint de Agenda - VERSIÓN SQL
Ahora usa SQL en lugar de JSON.
"""
from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from auth.login import roles_required
from core.menu import cargar_menu
from core.db_sql_store import evento_store
from datetime import datetime
from zoneinfo import ZoneInfo

# Blueprint con static_folder apuntando a la carpeta local de la app
agenda_bp = Blueprint(
    'agenda_bp',
    __name__,
    url_prefix='/agenda',
    static_folder='../static',
    static_url_path='/agenda/static'
)

# ========== VISTA PRINCIPAL ==========
@agenda_bp.route('/')
@login_required
@roles_required('viewer')
def indexagenda():
    nemu = cargar_menu()
    hoy = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))
    return render_template(
        'Aplic/agenda/FrontEnd/agenda.html',
        nemu=nemu,
        roles=current_user.roles,
        mes=hoy.month,
        año=hoy.year
    )

# ========== API EVENTOS ==========
@agenda_bp.route('/eventos', methods=['GET'])
@login_required
def listar_eventos():
    return jsonify(evento_store.listar())

@agenda_bp.route('/evento', methods=['POST'])
@login_required
@roles_required('viewer')
def crear_evento():
    try:
        data = request.get_json()
        evento = evento_store.agregar(data)
        return jsonify({"status": "ok", "evento": evento}), 201
    except ValueError as e:
        return jsonify({"status": "error", "msg": str(e)}), 400

@agenda_bp.route('/evento/<int:evento_id>', methods=['PUT'])
@login_required
@roles_required('viewer')
def actualizar_evento(evento_id):
    try:
        data = request.get_json()
        if evento_store.editar(evento_id, data):
            return jsonify({"status": "ok"})
        return jsonify({"status": "error", "msg": "Evento no encontrado"}), 404
    except ValueError as e:
        return jsonify({"status": "error", "msg": str(e)}), 400

@agenda_bp.route('/evento/<int:evento_id>', methods=['DELETE'])
@login_required
@roles_required('viewer')
def borrar_evento(evento_id):
    if evento_store.eliminar(evento_id):
        return jsonify({"status": "ok"})
    return jsonify({"status": "error", "msg": "Evento no encontrado"}), 404

@agenda_bp.route('/evento/<int:evento_id>/toggle', methods=['PATCH'])
@login_required
def toggle_realizado(evento_id):
    nuevo_estado = evento_store.toggle_realizado(evento_id)
    if nuevo_estado is not None:
        return jsonify({"status": "ok", "realizado": nuevo_estado})
    return jsonify({"status": "error", "msg": "Evento no encontrado"}), 404