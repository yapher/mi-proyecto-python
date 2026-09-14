"""
Blueprint de Planos - VERSIÓN SQL
"""
from flask_login import login_required, current_user
from core.menu import cargar_menu
from auth.login import roles_required
from flask import (
    Blueprint, jsonify, request, render_template,
    redirect, url_for, flash, current_app
)
import os
from datetime import datetime
from urllib.parse import unquote
from core.db_sql_store import plano_store, ubicacion_store

_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_STATIC_DIR = os.path.abspath(os.path.join(_APP_DIR, '..', 'static'))

planos_bp = Blueprint(
    'indeximagenes',
    __name__,
    static_folder=_STATIC_DIR,
    static_url_path='/imagenes/static'
)


def get_planos_folder():
    folder = os.path.join(current_app.root_path, 'static', 'uploads', 'planos')
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder


def cargar_ubicaciones():
    return ubicacion_store.cargar_arbol()


def extraer_rutas(ubicaciones):
    rutas = []

    def recorrer(items):
        if items is None:
            return
        if isinstance(items, dict):
            items = [items]
        for u in items:
            if not isinstance(u, dict):
                continue
            ruta = u.get('ruta') or u.get('nombre')
            if ruta:
                rutas.append(ruta)
            subs = (
                u.get('sububicaciones') or
                u.get('subUbicaciones') or
                u.get('sububicacion') or
                []
            )
            if subs:
                recorrer(subs)

    try:
        recorrer(ubicaciones)
    except Exception as e:
        current_app.logger.error(f'Error extrayendo rutas: {e}')

    return sorted(list(dict.fromkeys(rutas)))


# ============================================================
# RUTAS
# ============================================================

@planos_bp.route('/planos')
@login_required
@roles_required('viewer')
def listar_planos():
    nemu = cargar_menu()
    planos = plano_store.cargar_todos()
    ubicaciones = cargar_ubicaciones()
    rutas = extraer_rutas(ubicaciones)
    return render_template(
        'Aplic/imagenes/FrontEnd/planos.html',
        nemu=nemu,
        roles=current_user.roles,
        planos=planos,
        rutas=rutas
    )


@planos_bp.route('/planos/agregar', methods=['POST'])
@login_required
@roles_required('viewer')
def agregar_plano():
    nombre_linea = request.form.get('nombre_linea')
    descripcion = request.form.get('descripcion', '')
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

    try:
        plano_store.agregar({
            'nombre_linea': nombre_linea,
            'descripcion': descripcion,
            'nombre_archivo': filename,
            'usuario_carga': current_user.username,
            'fecha_carga': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        flash('Plano agregado correctamente', 'success')
    except Exception as e:
        current_app.logger.error(f'Error agregando plano: {e}')
        flash(f'Error al agregar el plano: {str(e)}', 'danger')

    return redirect(url_for('indeximagenes.listar_planos'))


@planos_bp.route('/planos/eliminar/<nombre_linea>/<path:archivo>', methods=['POST'])
@login_required
@roles_required('viewer')
def eliminar_plano(nombre_linea, archivo):
    nombre_linea = unquote(nombre_linea)
    archivo = unquote(archivo)

    try:
        plano_store.eliminar(nombre_linea, archivo)
        ruta_archivo = os.path.join(get_planos_folder(), nombre_linea, archivo)
        if os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)
        flash('Plano eliminado correctamente', 'success')
    except Exception as e:
        current_app.logger.error(f'Error eliminando plano: {e}')
        flash(f'Error al eliminar el plano: {str(e)}', 'danger')

    return redirect(url_for('indeximagenes.listar_planos'))


@planos_bp.route('/planos/editar/<nombre_linea>/<path:archivo>', methods=['POST'])
@login_required
@roles_required('viewer')
def editar_plano(nombre_linea, archivo):
    nombre_linea = unquote(nombre_linea)
    archivo = unquote(archivo)
    nueva_descripcion = request.form.get('descripcion', '')
    plano_store.editar_descripcion(nombre_linea, archivo, nueva_descripcion)
    flash('Descripción actualizada', 'success')
    return redirect(url_for('indeximagenes.listar_planos'))