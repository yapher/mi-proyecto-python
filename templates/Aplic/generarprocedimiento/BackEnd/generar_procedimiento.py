# Archivo backend generado automáticamente

from flask_login import login_required, current_user
from menu import cargar_menu
from login import roles_required
from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, current_app
import json, re, os
from datetime import datetime
from werkzeug.utils import secure_filename

generar_procedimiento_bp = Blueprint('indexgenerar_procedimiento', __name__)

ARCHIVO_ORIGINAL = "static/modelos/TextoEstandOperaciones.txt"

def leer_lineas():
    try:
        with open(ARCHIVO_ORIGINAL, "r", encoding="latin1") as f:
            return f.read().splitlines()
    except Exception as e:
        return [f"Error al leer el archivo: {e}"]


@generar_procedimiento_bp.route('/generar_procedimiento', methods=["GET", "POST"])
@login_required
@roles_required('viewer')
def indexgenerar_procedimiento():
    nemu = cargar_menu()
    lineas = leer_lineas()

    if request.method == "POST":
        nuevas_lineas = []

        for idx in range(len(lineas)):
            if not request.form.get(f"eliminar_{idx}"):
                nuevas_lineas.append(request.form.get(f"linea_{idx}", ""))

        nueva_linea = request.form.get("nueva_linea", "").strip()
        if nueva_linea:
            nuevas_lineas.append(nueva_linea)

        fecha = datetime.now().strftime("%d-%m-%Y")
        nombre_archivo = f"TextoEstandOperaciones_{fecha}.txt"
        ruta_guardado = os.path.join("static/modelos", secure_filename(nombre_archivo))

        with open(ruta_guardado, "w", encoding="latin1") as f:
            for linea in nuevas_lineas:
                f.write(linea + "\n")

        #return redirect(url_for('Aplic/generarprocedimiento/FrontEnd/generar_procedimiento.html'))
    return render_template('Aplic/generarprocedimiento/FrontEnd/generar_procedimiento.html',nemu=nemu, roles=current_user.roles, lineas=lineas)
