# Archivo backend generado automáticamente

from flask_login import login_required, current_user
from menu import cargar_menu
from login import roles_required
from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, current_app
import json, re, os
from datetime import datetime

cargar_procedimiento_bp = Blueprint('indexcargar_procedimiento', __name__)

# Ruta al archivo JSON
JSON_PATH = os.path.join('DataBase', 'dataOT', 'procedimiento.json')
# Carpeta para exportar los archivos de texto
EXPORT_FOLDER = os.path.join('static', 'exports')
os.makedirs(EXPORT_FOLDER, exist_ok=True)

# Copiar y pegar estas dos linea en app.py
#from templates.Aplic.cargarprocedimiento.BackEnd.cargar_procedimiento import cargar_procedimiento_bp
#app.register_blueprint(cargar_procedimiento_bp)

@cargar_procedimiento_bp.route('/cargar_procedimiento', methods=['GET', 'POST'])
@login_required
@roles_required('viewer')
def indexcargar_procedimiento():
    nemu = cargar_menu()
    data = cargar_json()
    if request.method == 'POST':
        # Obtener las selecciones del formulario
        selecciones = request.form.getlist('seleccion')
        # Generar el nombre del archivo con la fecha actual
        fecha = datetime.now().strftime('%Y-%m-%d')
        nombre_archivo = f'procedimiento_{fecha}.txt'
        ruta_archivo = os.path.join(EXPORT_FOLDER, nombre_archivo)
        # Escribir las selecciones en el archivo
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            for item in selecciones:
                f.write(f'{item}\n')
        return redirect(url_for('indexcargar_procedimiento.indexcargar_procedimiento'))
    return render_template('Aplic/cargarprocedimiento/FrontEnd/cargar_procedimiento.html',nemu=nemu, roles=current_user.roles, data=data)







# Función para cargar el JSON
def cargar_json():
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)
