# templates/Aplic/estadosderepuestos/BackEnd/routes.py
"""
Rutas HTTP del módulo de Estados de Repuestos.
"""

from flask import (
    Blueprint,
    flash,
    jsonify,
    render_template,
    request,
)
from flask_login import current_user, login_required

from auth.login import roles_required
from core.menu import cargar_menu

from core.data_loaders import (
    cargar_tabs,
    cargar_almacenes,
    obtener_nombres_almacenes,
    cargar_estados,
    cargar_ubicaciones,
)

from core.repuestos import (
    cargar_todos_repuestos,
    obtener_repuesto_por_codigo,
    existe_codigo,
    crear_repuesto as crear_repuesto_core,
    actualizar_repuesto as actualizar_repuesto_core,
    eliminar_repuesto as eliminar_repuesto_core,
)

from core.repuestos_filtros import (
    normalizar_texto,
    coincide_jerarquia,
    filtro_buscar,
    obtener_datos_repuesto_from_form,
    filtrar_repuestos_por_estado,
)

from core.redirecciones import redirigir_return_to

try:
    from core.image import procesar_imagen
except ImportError:
    try:
        from .services import procesar_imagen
    except ImportError:
        def procesar_imagen(file_storage):
            return None, None

try:
    from .export_pdf import exportar_pdf_reportlab
except ImportError:
    try:
        from templates.Aplic.estadosderepuestos.BackEnd.export_pdf import exportar_pdf_reportlab
    except ImportError:
        exportar_pdf_reportlab = None

try:
    from core.logging_config import get_logger
    logger = get_logger(__name__)
except Exception:
    import logging
    logger = logging.getLogger(__name__)


leer_repuestos = cargar_todos_repuestos

estadoRep_bp = Blueprint(
    'indexEstadoRep',
    __name__,
    static_folder='../static',
    static_url_path='/estadosderepuestos/static'
)


def _redirigir(return_to, tab_activo=''):
    return redirigir_return_to(
        return_to=return_to,
        tab_activo=tab_activo,
        default_endpoint='indexEstadoRep.indexEstadoRep'
    )


@estadoRep_bp.route("/estadosRep")
@login_required
@roles_required('viewer')
def indexEstadoRep():
    logger.info(f"Acceso a estadosRep - Usuario: {current_user.username}")

    nemu = cargar_menu()
    tabs = cargar_tabs()
    repuestos = leer_repuestos()

    almacenes = cargar_almacenes()
    estados = cargar_estados()
    ubicaciones = cargar_ubicaciones()
    nombres_almacenes = obtener_nombres_almacenes(almacenes)

    buscar = normalizar_texto(request.args.get('buscar', '')).lower()
    estado_actual = normalizar_texto(request.args.get('estado', ''))

    active_tab = (
        request.args.get('active_tab')
        or (tabs[0].get('sanitized_id', '') if tabs else '')
    )

    for tab in tabs:
        ruta_tab = normalizar_texto(tab.get('ruta_jerarquia', '')).lower()

        if ruta_tab:
            repuestos_filtrados = [
                r for r in repuestos
                if coincide_jerarquia(r, ruta_tab)
            ]
        else:
            repuestos_filtrados = list(repuestos)

        tab['repuestos_filtrados'] = filtro_buscar(repuestos_filtrados, buscar)

    tab_actual = None
    for tab in tabs:
        if normalizar_texto(tab.get('sanitized_id', '')) == normalizar_texto(active_tab):
            tab_actual = tab
            break

    if tab_actual is None and tabs:
        tab_actual = tabs[0]
        active_tab = normalizar_texto(tab_actual.get('sanitized_id', ''))

    repuestos_activos = tab_actual.get('repuestos_filtrados', repuestos) if tab_actual else repuestos

    estados_disponibles = sorted(
        set(
            normalizar_texto(r.get('estado', ''))
            for r in repuestos
            if normalizar_texto(r.get('estado', ''))
        )
    )

    return render_template(
        'Aplic/estadosderepuestos/FrontEnd/estados_de_repuestos.html',
        tabs=tabs,
        nemu=nemu,
        roles=getattr(current_user, 'roles', []),
        active_tab=active_tab,
        buscar=buscar,
        estado_actual=estado_actual,
        repuestos=repuestos_activos,
        nombres_almacenes=nombres_almacenes,
        estados=estados,
        estados_disponibles=estados_disponibles,
        ubicaciones=ubicaciones
    )


@estadoRep_bp.route('/api/repuestos')
def api_repuestos():
    ruta_jerarquia = normalizar_texto(request.args.get('ruta_jerarquia', '')).lower()
    repuestos = leer_repuestos()

    if ruta_jerarquia:
        repuestos_filtrados = [
            r for r in repuestos
            if coincide_jerarquia(r, ruta_jerarquia)
        ]
    else:
        repuestos_filtrados = repuestos

    return jsonify({'repuestos': repuestos_filtrados})


@estadoRep_bp.route("/exportar_pdf", methods=["POST"])
@login_required
@roles_required('viewer')
def exportar_pdf():
    if exportar_pdf_reportlab is None:
        logger.error("No se pudo importar exportar_pdf_reportlab.")
        return jsonify({"error": "Exportador PDF no disponible"}), 500

    ruta_jerarquia = normalizar_texto(request.form.get("ruta_jerarquia", "")).lower()
    buscar = normalizar_texto(request.form.get("buscar", "")).lower()

    repuestos = leer_repuestos()

    if ruta_jerarquia:
        repuestos_filtrados = [
            r for r in repuestos
            if coincide_jerarquia(r, ruta_jerarquia)
        ]
    else:
        repuestos_filtrados = list(repuestos)

    repuestos_filtrados = filtro_buscar(repuestos_filtrados, buscar)

    return exportar_pdf_reportlab(repuestos_filtrados)


@estadoRep_bp.route('/agregar_repuesto', methods=['POST'])
@login_required
@roles_required('viewer')
def agregar_repuesto():
    return_to = request.form.get('return_to', 'indexEstadoRep.indexEstadoRep')
    tab_activo = request.form.get('tab_activo', '')

    datos = obtener_datos_repuesto_from_form()

    if not datos.get('codigo'):
        flash("El campo 'codigo' es obligatorio.", "danger")
        return _redirigir(return_to, tab_activo)

    if not datos.get('nombre'):
        flash("El campo 'nombre' es obligatorio.", "danger")
        return _redirigir(return_to, tab_activo)

    if existe_codigo(datos['codigo']):
        flash(f"Ya existe un repuesto con codigo='{datos['codigo']}'.", "warning")
        return _redirigir(return_to, tab_activo)

    filename, error = procesar_imagen(request.files.get('imagen'))

    if error:
        flash(error, "danger")
        return _redirigir(return_to, tab_activo)

    if filename:
        datos['imagen'] = filename

    exito, mensaje = crear_repuesto_core(datos)

    if exito:
        logger.info(f"✅ Repuesto creado: {datos['codigo']} por {current_user.username}")
        flash(mensaje, "success")
    else:
        logger.warning(f"⚠️ Error creando repuesto: {mensaje}")
        flash(mensaje, "warning")

    return _redirigir(return_to, tab_activo)


@estadoRep_bp.route('/editar_repuesto', methods=['POST'])
@login_required
@roles_required('viewer')
def editar_repuesto():
    return_to = request.form.get('return_to', 'indexEstadoRep.indexEstadoRep')
    tab_activo = request.form.get('tab_activo', '')

    codigo_original = normalizar_texto(
        request.form.get('codigo_original')
        or request.form.get('sanitized_id')
        or request.form.get('codigo')
    )

    if not codigo_original:
        flash("No se identificó el repuesto a editar.", "danger")
        return _redirigir(return_to, tab_activo)

    nuevos_datos = obtener_datos_repuesto_from_form()

    if not nuevos_datos.get('codigo'):
        nuevos_datos['codigo'] = codigo_original

    if not nuevos_datos.get('nombre'):
        rep_actual = obtener_repuesto_por_codigo(codigo_original)
        if rep_actual:
            nuevos_datos['nombre'] = rep_actual.get('nombre', '')

    filename, error = procesar_imagen(request.files.get('imagen'))

    if error:
        flash(error, "danger")
        return _redirigir(return_to, tab_activo)

    if filename:
        # Se subió una imagen nueva: reemplaza a la anterior
        nuevos_datos['imagen'] = filename
    elif request.form.get('eliminar_imagen', '').strip().lower() == 'true':
        # ✅ Se quitó la imagen y no se subió otra.
        # Solo se desvincula del repuesto: el archivo NO se borra del disco
        # porque otros repuestos pueden estar usando el mismo archivo.
        nuevos_datos['imagen'] = ''

    exito, mensaje = actualizar_repuesto_core(codigo_original, nuevos_datos)

    if exito:
        logger.info(
            f"✅ Repuesto actualizado: {nuevos_datos.get('codigo')} "
            f"por {current_user.username}"
        )
        flash(mensaje, "success")
    else:
        logger.warning(f"⚠️ Error actualizando repuesto: {mensaje}")
        flash(mensaje, "warning")

    return _redirigir(return_to, tab_activo)


@estadoRep_bp.route('/eliminar_repuesto', methods=['POST'])
@login_required
@roles_required('viewer')
def eliminar_repuesto():
    return_to = request.form.get('return_to', 'indexEstadoRep.indexEstadoRep')
    tab_activo = request.form.get('tab_activo', '')

    codigo = normalizar_texto(
        request.form.get('codigo')
        or request.form.get('sanitized_id')
    )

    if not codigo:
        flash("No se identificó el repuesto a eliminar.", "danger")
        return _redirigir(return_to, tab_activo)

    exito, mensaje = eliminar_repuesto_core(codigo)

    if exito:
        logger.info(f"✅ Repuesto eliminado: {codigo} por {current_user.username}")
        flash(mensaje or "Repuesto eliminado correctamente.", "success")
    else:
        logger.warning(f"⚠️ No se encontró repuesto para eliminar: {codigo}")
        flash(mensaje or "No se encontró el repuesto a eliminar.", "danger")

    return _redirigir(return_to, tab_activo)


@estadoRep_bp.route('/filtrar_por_estado', methods=['GET'])
@login_required
@roles_required('viewer')
def estado_filter():
    estado = request.args.get('estado')

    tabs = cargar_tabs()
    repuestos = leer_repuestos()

    estados_disponibles = sorted(
        set(
            normalizar_texto(r.get('estado', ''))
            for r in repuestos
            if normalizar_texto(r.get('estado', ''))
        )
    )

    repuestos_filtrados = filtrar_repuestos_por_estado(
        repuestos=repuestos,
        estado_nombre=estado
    )

    active_tab = tabs[0].get('sanitized_id', '') if tabs else ''

    for tab in tabs:
        tab['repuestos_filtrados'] = repuestos_filtrados if tab.get('sanitized_id') == active_tab else []

    ubicaciones = cargar_ubicaciones()
    almacenes = cargar_almacenes()
    nombres_almacenes = obtener_nombres_almacenes(almacenes)
    estados = cargar_estados()

    return render_template(
        'Aplic/estadosderepuestos/FrontEnd/estados_de_repuestos.html',
        repuestos=repuestos_filtrados,
        estados_disponibles=estados_disponibles,
        estado_actual=estado,
        tabs=tabs,
        active_tab=active_tab,
        ubicaciones=ubicaciones,
        nombres_almacenes=nombres_almacenes,
        estados=estados
    )