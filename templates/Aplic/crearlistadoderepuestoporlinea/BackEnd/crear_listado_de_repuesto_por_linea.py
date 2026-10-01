"""
Blueprint de Crear Listado de Repuesto por Línea — VERSIÓN SQL
Cada pestaña queda vinculada a una ubicación técnica por clave foránea.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from auth.login import roles_required
from core.db_sql import db
from core.models import Tab
from core.db_sql_store import ubicacion_store

crear_listado_bp = Blueprint('crear_listado', __name__, url_prefix='/crear-listado')


def obtener_rutas():
    """Obtiene todas las ubicaciones técnicas desde SQL."""
    arbol = ubicacion_store.cargar_arbol()
    rutas = []

    def extraer(items):
        for item in items:
            rutas.append({
                "ruta": item.get("ruta", ""),
                "ruta_jerarquia": item.get("ruta_jerarquia", "")
            })
            if item.get("sububicaciones"):
                extraer(item["sububicaciones"])

    extraer(arbol)
    return rutas


def guardar_tab(ruta_jerarquia):
    """Crea la pestaña vinculada a la ubicación. Retorna (ok, mensaje)."""
    ubicacion = ubicacion_store.buscar_por_ruta(ruta_jerarquia)
    if not ubicacion:
        return False, "La ubicación seleccionada no existe."

    if Tab.query.filter_by(ubicacion_id=ubicacion.id).first():
        return False, "Ya existe una pestaña para esa ubicación."

    etiqueta = ubicacion.ruta or ubicacion.nombre
    clave = f"ubic-{ubicacion.id}"   # estable y válido como id HTML

    db.session.add(Tab(
        tab_id=clave,
        title_legacy=f"{etiqueta} 🏬",   # respaldo; el título real se calcula
        ubicacion_id=ubicacion.id,
        sanitized_id=clave
    ))
    db.session.commit()
    return True, f"Pestaña creada para {ubicacion.ruta_jerarquia}"


@crear_listado_bp.route('/', methods=['GET', 'POST'])
@login_required
@roles_required('viewer')
def crear_listado():
    if request.method == 'POST':
        ruta_jerarquia = (request.form.get('ruta') or '').strip()
        if not ruta_jerarquia:
            flash("Seleccioná una línea.", "warning")
        else:
            ok, msg = guardar_tab(ruta_jerarquia)
            flash(msg, "success" if ok else "warning")
        return redirect(url_for('crear_listado.crear_listado'))

    return render_template(
        'Aplic/crearlistadoderepuestoporlinea/FrontEnd/crear_listado_de_repuesto_por_linea.html',
        rutas=obtener_rutas()
    )