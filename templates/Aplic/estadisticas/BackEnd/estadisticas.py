# Archivo backend generado automáticamente

from flask_login import login_required, current_user
from menu import cargar_menu
from login import roles_required
from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, current_app
import json, re, os
from glob import glob
from datetime import datetime

estadisticas_bp = Blueprint('indexestadisticas', __name__)

GASTOSMES = 'DataBase/hogar'

@estadisticas_bp.route('/estadisticas')
@login_required
@roles_required('viewer')
def indexestadisticas():
    nemu = cargar_menu()
    return render_template('Aplic/estadisticas/FrontEnd/estadisticas.html', nemu=nemu, roles=current_user.roles)

@estadisticas_bp.route('/api/estadisticas')
@login_required
def api_estadisticas():
    archivos = sorted(glob(os.path.join(GASTOSMES, 'GASTO_*.json')))
    rubros = {}
    items = {}

    for archivo in archivos:
        nombre = os.path.basename(archivo)
        fecha = nombre.replace("GASTO_", "").replace(".json", "")  # Ej: 2025_06
        try:
            fecha_fmt = datetime.strptime(fecha, "%Y_%m").strftime("%Y-%m")
        except:
            continue

        with open(archivo, 'r', encoding='utf-8') as f:
            pagos = json.load(f)
            for p in pagos:
                rubro = p.get("rubro", "Sin Rubro")
                descripcion = p.get("descripcion", "Sin Descripción")
                importe = p.get("importe", 0)

                # Sumar por rubro y fecha
                if rubro not in rubros:
                    rubros[rubro] = {}
                rubros[rubro][fecha_fmt] = rubros[rubro].get(fecha_fmt, 0) + importe

                # Sumar por ítem/descripción y fecha
                if descripcion not in items:
                    items[descripcion] = {}
                items[descripcion][fecha_fmt] = items[descripcion].get(fecha_fmt, 0) + importe

    return jsonify({
        "rubros": rubros,
        "items": items
    })
@estadisticas_bp.route('/estadisticas/gasto_mensual')
@login_required
def gasto_mensual():
    import calendar
    gastos_por_mes = {}
    archivos = glob(os.path.join(GASTOSMES, "GASTO_*.json"))

    for archivo in archivos:
        nombre = os.path.basename(archivo)
        match = re.match(r"GASTO_(\d{4})_(\d{2})\.json", nombre)
        if not match:
            continue
        anio, mes = match.groups()
        clave = f"{anio}-{mes}"
        with open(archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        total = sum(p.get('importe', 0) for p in datos)
        gastos_por_mes[clave] = round(total, 2)

    # Ordenar por fecha
    gastos_ordenados = dict(sorted(gastos_por_mes.items()))
    return jsonify(gastos_ordenados)

