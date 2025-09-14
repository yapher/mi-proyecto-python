from flask import Blueprint, jsonify, request, render_template, current_app
from flask_login import login_required, current_user
from login import roles_required
from menu import cargar_menu
from datetime import datetime
from zoneinfo import ZoneInfo

# Importa tus funciones del manager
from templates.Aplic.agenda.BackEnd.db_manager import (
    cargar_eventos, agregar_evento, editar_evento,
    eliminar_evento
)

agenda_bp = Blueprint('agenda_bp', __name__, url_prefix='/agenda')

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
    return jsonify(cargar_eventos())


@agenda_bp.route('/evento', methods=['POST'])
@login_required
@roles_required('viewer')
def crear_evento():
    data = request.json
    agregar_evento(data)
    return jsonify({"status": "ok"})


@agenda_bp.route('/evento/<int:evento_id>', methods=['PUT'])
@login_required
@roles_required('viewer')
def actualizar_evento(evento_id):
    data = request.json
    editar_evento(evento_id, data)
    return jsonify({"status": "ok"})


@agenda_bp.route('/evento/<int:evento_id>', methods=['DELETE'])
@login_required
@roles_required('viewer')
def borrar_evento(evento_id):
    eliminar_evento(evento_id)
    return jsonify({"status": "ok"})
