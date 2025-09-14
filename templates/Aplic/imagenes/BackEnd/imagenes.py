# Redirigir /imagenes a /planos
from flask_login import login_required, current_user
from menu import cargar_menu
from login import roles_required
from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, current_app
import json, re, os


@login_required
@roles_required('viewer')
def redirect_imagenes():
    return redirect(url_for('indeximagenes.listar_planos'))
# Archivo backend generado automáticamente


planos_bp = Blueprint('indeximagenes', __name__)


def get_planos_folder():
    folder = os.path.join(current_app.root_path, 'static', 'uploads', 'planos')
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder

def get_planos_json():
    return os.path.join(current_app.root_path, 'DataBase', 'planos.json')

def cargar_planos():
    PLANOS_JSON = get_planos_json()
    if os.path.exists(PLANOS_JSON):
        with open(PLANOS_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def guardar_planos(data):
    PLANOS_JSON = get_planos_json()
    with open(PLANOS_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 🔹 NUEVO: cargar ubicaciones desde ubicacion_tecnica.json (más robusto y con logging)
def cargar_ubicaciones():
    UBICACION_JSON = os.path.join(current_app.root_path, 'DataBase', 'dataRep', 'ubicacion_tecnica.json')
    if os.path.exists(UBICACION_JSON):
        with open(UBICACION_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def extraer_rutas(ubicaciones):
    """
    Extrae recursivamente todos los valores del campo 'ruta' desde la estructura
    (acepta list o dict como entrada). Devuelve lista única y ordenada.
    """
    rutas = []
    def recorrer(items):
        if items is None:
            return
        if isinstance(items, dict):
            items = [items]
        for u in items:
            if not isinstance(u, dict):
                continue
            # intentar campo 'ruta', sino 'nombre' como fallback
            ruta = u.get('ruta') or u.get('nombre')
            if ruta:
                rutas.append(ruta)
            subs = u.get('sububicaciones') or u.get('sububicaciones', [])
            # algunos JSON pueden usar otra clave, chequeamos también 'subUbicaciones' por si acaso
            if not subs:
                subs = u.get('subUbicaciones') or u.get('sububicacion') or []
            if subs:
                recorrer(subs)
    try:
        recorrer(ubicaciones)
    except Exception as e:
        current_app.logger.error(f'Error extrayendo rutas: {e}')
    # eliminar duplicados y ordenar para consistencia
    rutas_unicas = sorted(list(dict.fromkeys(rutas)))
    return rutas_unicas

# Ruta para listar planos
@planos_bp.route('/planos')
@login_required
@roles_required('viewer')
def listar_planos():
    nemu = cargar_menu()
    planos = cargar_planos()
    ubicaciones = cargar_ubicaciones()
    rutas = extraer_rutas(ubicaciones)
    # log para debug
    current_app.logger.debug(f'RUTAS encontradas: {rutas}')
    return render_template(
        'Aplic/imagenes/FrontEnd/planos.html',
        nemu=nemu,
        roles=current_user.roles,
        planos=planos,
        rutas=rutas
    )

# Ruta para subir plano
@planos_bp.route('/planos/agregar', methods=['POST'])
@login_required
@roles_required('viewer')
def agregar_plano():
    nombre_linea = request.form.get('nombre_linea')
    descripcion = request.form.get('descripcion')
    archivo = request.files.get('archivo')
    if not archivo or not archivo.filename.lower().endswith('.pdf'):
        flash('Solo se permiten archivos PDF', 'danger')
        return redirect(url_for('indeximagenes.listar_planos'))
    filename = archivo.filename
    PLANOS_FOLDER = get_planos_folder()
    carpeta_linea = os.path.join(PLANOS_FOLDER, nombre_linea)
    if not os.path.exists(carpeta_linea):
        os.makedirs(carpeta_linea)
    ruta_archivo = os.path.join(carpeta_linea, filename)
    archivo.save(ruta_archivo)
    planos = cargar_planos()
    planos.append({
        'nombre_linea': nombre_linea,
        'descripcion': descripcion,
        'archivo': filename,
        'carpeta': nombre_linea
    })
    guardar_planos(planos)
    flash('Plano PDF subido correctamente', 'success')
    return redirect(url_for('indeximagenes.listar_planos'))

# Ruta para eliminar plano
@planos_bp.route('/planos/eliminar/<nombre_linea>/<archivo>', methods=['POST'])
@login_required
@roles_required('viewer')
def eliminar_plano(nombre_linea, archivo):
    PLANOS_FOLDER = get_planos_folder()
    carpeta_linea = os.path.join(PLANOS_FOLDER, nombre_linea)
    ruta_archivo = os.path.join(carpeta_linea, archivo)
    if os.path.exists(ruta_archivo):
        os.remove(ruta_archivo)
    planos = cargar_planos()
    planos = [p for p in planos if not (p['nombre_linea'] == nombre_linea and p['archivo'] == archivo)]
    guardar_planos(planos)
    flash('Plano eliminado correctamente', 'success')
    return redirect(url_for('indeximagenes.listar_planos'))

# Ruta para editar plano (solo descripción)
@planos_bp.route('/planos/editar/<nombre_linea>/<archivo>', methods=['POST'])
@login_required
@roles_required('viewer')
def editar_plano(nombre_linea, archivo):
    nueva_descripcion = request.form.get('descripcion')
    planos = cargar_planos()
    for p in planos:
        if p['nombre_linea'] == nombre_linea and p['archivo'] == archivo:
            p['descripcion'] = nueva_descripcion
    guardar_planos(planos)
    flash('Descripción actualizada', 'success')
    return redirect(url_for('indeximagenes.listar_planos'))
