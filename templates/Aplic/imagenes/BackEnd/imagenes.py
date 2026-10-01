"""
Blueprint de Planos - VERSIÓN SQL
Cada plano queda vinculado a una ubicación técnica por clave foránea.
"""
from flask_login import login_required, current_user
from core.menu import cargar_menu
from auth.login import roles_required
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, current_app
)
import os
from werkzeug.utils import secure_filename
from core.db_sql import db
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
    os.makedirs(folder, exist_ok=True)
    return folder


def listar_rutas_ubicaciones():
    """Todas las ruta_jerarquia (únicas) para el select del modal."""
    rutas = []

    def recorrer(items):
        for u in items or []:
            if not isinstance(u, dict):
                continue
            ruta = u.get('ruta_jerarquia')
            if ruta:
                rutas.append(ruta)
            recorrer(u.get('sububicaciones'))

    recorrer(ubicacion_store.cargar_arbol())
    return sorted(dict.fromkeys(rutas))


def _ruta_pdf(plano):
    return os.path.join(get_planos_folder(), plano.carpeta_disco, plano.nombre_archivo)


# ============================================================
# RUTAS
# ============================================================

@planos_bp.route('/planos')
@login_required
@roles_required('viewer')
def listar_planos():
    nemu = cargar_menu()
    return render_template(
        'Aplic/imagenes/FrontEnd/planos.html',
        nemu=nemu,
        roles=current_user.roles,
        planos=plano_store.cargar_todos(),
        rutas=listar_rutas_ubicaciones()
    )


@planos_bp.route('/planos/agregar', methods=['POST'])
@login_required
@roles_required('viewer')
def agregar_plano():
    ruta_jerarquia = (request.form.get('nombre_linea') or '').strip()
    descripcion = request.form.get('descripcion', '')
    archivo = request.files.get('archivo')

    if not archivo or not archivo.filename.lower().endswith('.pdf'):
        flash('Solo se permiten archivos PDF', 'danger')
        return redirect(url_for('indeximagenes.listar_planos'))

    ubicacion = ubicacion_store.buscar_por_ruta(ruta_jerarquia)
    if not ubicacion:
        flash('La ubicación seleccionada no existe', 'danger')
        return redirect(url_for('indeximagenes.listar_planos'))

    filename = secure_filename(archivo.filename)
    if not filename.lower().endswith('.pdf'):
        flash('Nombre de archivo inválido', 'danger')
        return redirect(url_for('indeximagenes.listar_planos'))

    if plano_store.existe(ubicacion.id, filename):
        flash('Ya existe un plano con ese nombre en esa ubicación', 'warning')
        return redirect(url_for('indeximagenes.listar_planos'))

    carpeta = f"u{ubicacion.id}"
    carpeta_abs = os.path.join(get_planos_folder(), carpeta)
    os.makedirs(carpeta_abs, exist_ok=True)
    ruta_archivo = os.path.join(carpeta_abs, filename)
    archivo.save(ruta_archivo)

    try:
        plano_store.agregar(
            ubicacion=ubicacion,
            carpeta=carpeta,
            nombre_archivo=filename,
            descripcion=descripcion,
            usuario=current_user.username,
        )
        flash('Plano agregado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        if os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)
        current_app.logger.error(f'Error agregando plano: {e}')
        flash(f'Error al agregar el plano: {str(e)}', 'danger')

    return redirect(url_for('indeximagenes.listar_planos'))


@planos_bp.route('/planos/eliminar/<int:plano_id>', methods=['POST'])
@login_required
@roles_required('viewer')
def eliminar_plano(plano_id):
    plano = plano_store.obtener(plano_id)
    if not plano:
        flash('El plano no existe', 'warning')
        return redirect(url_for('indeximagenes.listar_planos'))

    ruta_pdf = _ruta_pdf(plano)

    try:
        plano_store.eliminar(plano_id)
        if os.path.exists(ruta_pdf):
            os.remove(ruta_pdf)
        flash('Plano eliminado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error eliminando plano: {e}')
        flash(f'Error al eliminar el plano: {str(e)}', 'danger')

    return redirect(url_for('indeximagenes.listar_planos'))


@planos_bp.route('/planos/editar/<int:plano_id>', methods=['POST'])
@login_required
@roles_required('viewer')
def editar_plano(plano_id):
    nueva_descripcion = request.form.get('descripcion', '')
    if plano_store.editar_descripcion(plano_id, nueva_descripcion):
        flash('Descripción actualizada', 'success')
    else:
        flash('El plano no existe', 'warning')
    return redirect(url_for('indeximagenes.listar_planos'))