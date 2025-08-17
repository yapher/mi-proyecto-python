from flask_login import login_required, current_user
from menu import cargar_menu
from login import roles_required
from flask import Blueprint, jsonify, request, render_template, abort, current_app
from datetime import datetime
import json, os, re


gestion_de_herramientas_bp = Blueprint('indexgestion_de_herramientas', __name__)
PLANO_DIR = 'DataBase/planos'


@gestion_de_herramientas_bp.route('/gestion_de_herramientas')
@login_required
@roles_required('viewer')
def indexgestion_de_herramientas():
    nemu = cargar_menu()
  
    return render_template('Aplic/gestiondeherramientas/FrontEnd/gestion_de_herramientas.html',
                           nemu=nemu, roles=current_user.roles)

@gestion_de_herramientas_bp.route('/guardar_plano', methods=['POST'])
@login_required
def guardar_plano():
    data = request.json
    nombre = data.get('nombre', 'croquis')
    path = os.path.join(PLANO_DIR, f"{nombre}.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data['data'], f, indent=4)
    return jsonify({"status": "ok"})

@gestion_de_herramientas_bp.route('/cargar_plano')
@login_required
def cargar_plano():
    nombre = request.args.get('nombre', 'croquis')
    path = os.path.join(PLANO_DIR, f"{nombre}.json")
    if not os.path.exists(path):
        abort(404)
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)
