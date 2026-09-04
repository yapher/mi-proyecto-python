"""
Rutas HTTP del módulo de Estados de Repuestos.
Responsabilidad ÚNICA: manejar peticiones HTTP (request/response).
"""
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from auth.login import roles_required
from core.menu import cargar_menu

# ✅ IMPORTS DIRECTOS DESDE CORE (más limpio y reutilizable)
from core.data_loaders import (
    cargar_tabs,
    cargar_almacenes,
    obtener_nombres_almacenes,
    cargar_estados,
    cargar_ubicaciones,
)
from core.image import procesar_imagen

# Importaciones locales del módulo
from .models import leer_repuestos, crear_repuesto, actualizar_repuesto, guardar_repuestos
from .export_pdf import exportar_pdf_reportlab

estadoRep_bp = Blueprint('indexEstadoRep', __name__)


def _redirigir(return_to, tab_activo):
    """Redirección dinámica según return_to."""
    if return_to == 'indexlista_repuestos.indexlista_repuestos':
        return redirect(url_for('indexlista_repuestos.indexlista_repuestos'))
    return redirect(url_for('indexEstadoRep.indexEstadoRep', active_tab=tab_activo))


@estadoRep_bp.route("/estadosRep")
@login_required
@roles_required('viewer')
def indexEstadoRep():
    nemu = cargar_menu()
    tabs = cargar_tabs()
    repuestos = leer_repuestos()
    almacenes = cargar_almacenes()
    estados = cargar_estados()
    ubicaciones = cargar_ubicaciones()
    nombres_almacenes = obtener_nombres_almacenes(almacenes)

    buscar = request.args.get('buscar', '').strip().lower()
    active_tab = request.args.get('active_tab') or (tabs[0]['sanitized_id'] if tabs else '')

    for tab in tabs:
        ruta = tab.get('ruta_jerarquia', '').strip().lower()
        repuestos_filtrados = [
            r for r in repuestos
            if any(ruta_jer.strip().lower() == ruta for ruta_jer in r.get('ruta_jerarquia', []))
        ]
        if buscar:
            repuestos_filtrados = [
                r for r in repuestos_filtrados
                if buscar in str(r.get('nombre', '')).lower()
                or buscar in str(r.get('codigo', '')).lower()
                or buscar in str(r.get('equipo', '')).lower()
                or buscar in str(r.get('cantidad', '')).lower()
                or buscar in ','.join(r.get('ruta_jerarquia', [])).lower()
            ]
        tab['repuestos_filtrados'] = repuestos_filtrados

    return render_template(
        'Aplic/estadosderepuestos/FrontEnd/estados_de_repuestos.html',
        tabs=tabs, nemu=nemu, roles=current_user.roles,
        active_tab=active_tab, buscar=buscar,
        nombres_almacenes=nombres_almacenes,
        estados=estados, ubicaciones=ubicaciones
    )


@estadoRep_bp.route('/api/repuestos')
def api_repuestos():
    ruta_jerarquia = request.args.get('ruta_jerarquia', '').lower()
    repuestos = leer_repuestos()
    repuestos_filtrados = [
        r for r in repuestos
        if any(ruta.lower() == ruta_jerarquia for ruta in r.get('ruta_jerarquia', []))
    ]
    return jsonify({'repuestos': repuestos_filtrados})


@estadoRep_bp.route("/exportar_pdf", methods=["POST"])
@login_required
@roles_required('viewer')
def exportar_pdf():
    ruta_jerarquia = request.form.get("ruta_jerarquia", "").strip().lower()
    buscar = request.form.get("buscar", "").strip().lower()

    repuestos = leer_repuestos()
    repuestos_filtrados = [
        r for r in repuestos
        if any(ruta_jer.strip().lower() == ruta_jerarquia for ruta_jer in r.get('ruta_jerarquia', []))
    ]
    if buscar:
        repuestos_filtrados = [
            r for r in repuestos_filtrados
            if buscar in str(r.get('nombre', '')).lower()
            or buscar in str(r.get('codigo', '')).lower()
            or buscar in str(r.get('equipo', '')).lower()
            or buscar in str(r.get('estado', '')).lower()
            or buscar in str(r.get('cantidad', '')).lower()
            or buscar in ','.join(r.get('ruta_jerarquia', [])).lower()
        ]
    return exportar_pdf_reportlab(repuestos_filtrados)


@estadoRep_bp.route('/agregar_repuesto', methods=['POST'])
@login_required
@roles_required('viewer')
def agregar_repuesto():
    return_to = request.form.get('return_to', 'indexEstadoRep.indexEstadoRep')
    tab_activo = request.form.get('tab_activo', '')

    datos = {
        "nombre": request.form.get('nombre', '').strip(),
        "codigo": request.form.get('codigo', '').strip(),
        "cantidad": request.form.get('cantidad', '').strip(),
        "equipo": request.form.get('equipo', '').strip(),
        "ruta_jerarquia": request.form.getlist('ruta_jerarquia[]'),
        "fecha_creacion": request.form.get('fecha_creacion', '').strip(),
        "fecha_fin": request.form.get('fecha_fin', '').strip(),
        "link": request.form.get('link', '').strip(),
        "estado": request.form.get('estado', '').strip(),
        "imagen": None
    }

    if not all([datos['nombre'], datos['codigo'], datos['cantidad'], datos['fecha_creacion'], datos['estado']]):
        flash("Por favor completa los campos obligatorios.", "danger")
        return _redirigir(return_to, tab_activo)

    try:
        datos['cantidad'] = int(datos['cantidad'])
    except ValueError:
        flash("Cantidad debe ser un número entero.", "danger")
        return _redirigir(return_to, tab_activo)

    filename, error = procesar_imagen(request.files.get('imagen'))
    if error:
        flash(error, "danger")
        return _redirigir(return_to, tab_activo)
    if filename:
        datos['imagen'] = filename

    exito, mensaje = crear_repuesto(datos)
    flash(mensaje, "success" if exito else "warning")
    return _redirigir(return_to, tab_activo)


@estadoRep_bp.route('/editar_repuesto', methods=['POST'])
@login_required
@roles_required('viewer')
def editar_repuesto():
    return_to = request.form.get('return_to', 'indexEstadoRep.indexEstadoRep')
    tab_activo = request.form.get('tab_activo', '')
    codigo_original = request.form.get('codigo_original', '').strip()

    nuevos_datos = {
        "nombre": request.form.get('nombre', '').strip(),
        "codigo": request.form.get('codigo', '').strip(),
        "cantidad": request.form.get('cantidad', '').strip(),
        "equipo": request.form.get('equipo', '').strip(),
        "ruta_jerarquia": request.form.getlist('ruta_jerarquia[]'),
        "fecha_creacion": request.form.get('fecha_creacion', '').strip(),
        "fecha_fin": request.form.get('fecha_fin', '').strip(),
        "link": request.form.get('link', '').strip(),
        "estado": request.form.get('estado', '').strip()
    }

    try:
        nuevos_datos['cantidad'] = int(nuevos_datos['cantidad'])
    except ValueError:
        nuevos_datos['cantidad'] = 0

    filename, error = procesar_imagen(request.files.get('imagen'))
    if error:
        flash(error, "danger")
        return _redirigir(return_to, tab_activo)
    if filename:
        nuevos_datos['imagen'] = filename

    exito, mensaje = actualizar_repuesto(codigo_original, nuevos_datos)
    flash(mensaje, "success" if exito else "warning")
    return _redirigir(return_to, tab_activo)


@estadoRep_bp.route('/eliminar_repuesto', methods=['POST'])
@login_required
@roles_required('viewer')
def eliminar_repuesto():
    return_to = request.form.get('return_to', 'indexEstadoRep.indexEstadoRep')
    tab_activo = request.form.get('tab_activo', '')
    codigo = request.form.get('codigo', '').strip()

    repuestos = leer_repuestos()
    repuestos_nuevos = [r for r in repuestos if str(r.get('codigo', '')) != str(codigo)]
    if len(repuestos_nuevos) < len(repuestos):
        guardar_repuestos(repuestos_nuevos)
        flash("Repuesto eliminado correctamente.", "success")
    else:
        flash("No se encontró el repuesto a eliminar.", "danger")

    return _redirigir(return_to, tab_activo)


@estadoRep_bp.route('/filtrar_por_estado', methods=['GET'])
@login_required
@roles_required('viewer')
def estado_filter():
    estado = request.args.get('estado')
    pestañas = cargar_tabs()
    pestaña_activa = pestañas[0] if pestañas else {}

    repuestos = leer_repuestos()
    estados_disponibles = sorted(set(r.get('estado', '') for r in repuestos if r.get('estado')))

    if estado:
        repuestos_filtrados = [r for r in repuestos if r.get('estado') == estado]
    else:
        repuestos_filtrados = repuestos

    ubicaciones = cargar_ubicaciones()
    almacenes = cargar_almacenes()
    nombres_almacenes = obtener_nombres_almacenes(almacenes)
    estados = cargar_estados()

    return render_template(
        'Aplic/estadosderepuestos/FrontEnd/estados_de_repuestos.html',
        repuestos=repuestos_filtrados,
        estados_disponibles=estados_disponibles,
        estado_actual=estado,
        pestañas=pestañas,
        tab=pestaña_activa,
        active_tab=pestaña_activa.get('sanitized_id', ''),
        ubicaciones=ubicaciones,
        nombres_almacenes=nombres_almacenes,
        estados=estados
    )