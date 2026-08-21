# Aplic/modelos3d/BackEnd/modelos_3d.py

from flask_login import login_required, current_user
from menu import cargar_menu
from login import roles_required
from flask import Blueprint, jsonify, request, render_template, current_app, send_from_directory
import json, os

modelos_3d_bp = Blueprint('modelos_3d', __name__)

def ensure_sensores_dir():
    """Asegura que el directorio de sensores existe"""
    sensores_path = os.path.join(current_app.static_folder, "sensores")
    os.makedirs(sensores_path, exist_ok=True)
    return sensores_path

@modelos_3d_bp.route('/modelos_3d')
@login_required
@roles_required('viewer')
def index():
    nemu = cargar_menu()
    
    # Obtener lista de modelos disponibles
    modelos_dir = os.path.join(current_app.static_folder, "models")
    archivos = []
    
    if os.path.exists(modelos_dir):
        archivos = [f for f in os.listdir(modelos_dir) if f.lower().endswith((".gltf", ".glb"))]
    
    return render_template('Aplic/modelos3d/FrontEnd/modelos_3d.html',
                         nemu=nemu, 
                         roles=current_user.roles,
                         archivos=archivos)

@modelos_3d_bp.route('/modelos_3d/model/<path:filename>')
@login_required
@roles_required('viewer')
def serve_model(filename):
    """Sirve los archivos de modelos 3D"""
    models_path = os.path.join(current_app.static_folder, 'models')
    return send_from_directory(models_path, filename)

@modelos_3d_bp.route('/modelos_3d/guardar_sensores/<modelo>', methods=['POST'])
@login_required
@roles_required('viewer')
def guardar_sensores(modelo):
    """Guarda los sensores de un modelo"""
    try:
        data = request.json
        sensores_dir = ensure_sensores_dir()
        path = os.path.join(sensores_dir, f"{modelo}.json")
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@modelos_3d_bp.route('/modelos_3d/cargar_sensores/<modelo>')
@login_required
@roles_required('viewer')
def cargar_sensores(modelo):
    """Carga los sensores guardados de un modelo"""
    try:
        sensores_dir = ensure_sensores_dir()
        path = os.path.join(sensores_dir, f"{modelo}.json")
        
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify(data)
        return jsonify([])
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500