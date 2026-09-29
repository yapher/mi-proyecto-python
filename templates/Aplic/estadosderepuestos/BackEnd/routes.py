# templates/Aplic/estadosderepuestos/BackEnd/routes.py
"""
Rutas HTTP del módulo de Estados de Repuestos.

✅ Importa directamente desde core/ (sin wrappers intermedios)
✅ Usa logging centralizado
✅ Corrección importante:
   _redirigir() ahora es dinámico y permite volver a graficos_repuestos,
   lista_repuestos, inventario y futuras aplicaciones sin hardcodear cada caso.
"""

import json
from urllib.parse import urlparse, urlunparse

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from werkzeug.routing import BuildError

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
    filtrar_repuestos,
    obtener_repuesto_por_codigo,
    existe_codigo,
    crear_repuesto as crear_repuesto_core,
    actualizar_repuesto as actualizar_repuesto_core,
    eliminar_repuesto as eliminar_repuesto_core,
    guardar_todos_repuestos,
)

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


# ============================================================
# Alias para mantener compatibilidad con el código existente
# ============================================================
leer_repuestos = cargar_todos_repuestos

estadoRep_bp = Blueprint(
    'indexEstadoRep',
    __name__,
    static_folder='../static',
    static_url_path='/estadosderepuestos/static'
)


# ============================================================
# HELPERS GENERALES
# ============================================================
def _normalizar_texto(valor):
    if valor is None:
        return ''
    return str(valor).strip()


def _parsear_lista_rutas(valor):
    """
    Normaliza ruta_jerarquia desde distintos formatos posibles:
    - list
    - tuple
    - set
    - dict
    - string
    - string JSON "[...]"
    """
    if valor is None:
        return []

    if isinstance(valor, (list, tuple, set)):
        resultado = []
        for item in valor:
            resultado.extend(_parsear_lista_rutas(item))
        return resultado

    if isinstance(valor, dict):
        for clave in ('ruta_jerarquia', 'rutas', 'ruta', 'nombre', 'value'):
            if clave in valor:
                return _parsear_lista_rutas(valor[clave])
        return []

    texto = _normalizar_texto(valor)
    if not texto:
        return []

    if texto.startswith('['):
        try:
            data = json.loads(texto)
            if isinstance(data, list):
                return _parsear_lista_rutas(data)
        except Exception:
            pass

    if texto.startswith('{'):
        try:
            data = json.loads(texto)
            return _parsear_lista_rutas(data)
        except Exception:
            pass

    if '\n' in texto:
        partes = texto.splitlines()
    elif '\r' in texto:
        partes = texto.split('\r')
    else:
        partes = [texto]

    return [_normalizar_texto(p) for p in partes if _normalizar_texto(p)]


def _obtener_rutas_jerarquia_from_form():
    """
    Lee rutas jerárquicas desde el formulario.
    Soporta:
    - multiple select: ruta_jerarquia=A&ruta_jerarquia=B
    - hidden JSON: ruta_jerarquia=["A","B"]
    - textarea con líneas
    """
    valores = []

    for clave in ('ruta_jerarquia', 'rutas_jerarquia', 'ubicaciones', 'ruta'):
        try:
            valores.extend(request.form.getlist(clave))
        except Exception:
            pass

    rutas = []
    for valor in valores:
        rutas.extend(_parsear_lista_rutas(valor))

    vistos = set()
    resultado = []
    for ruta in rutas:
        ruta = _normalizar_texto(ruta)
        if ruta and ruta not in vistos:
            vistos.add(ruta)
            resultado.append(ruta)

    return resultado


def _normalizar_lista_rutas_repuesto(repuesto):
    return _parsear_lista_rutas(repuesto.get('ruta_jerarquia', []))


def _obtener_datos_repuesto_from_form():
    """
    Extrae datos del repuesto desde el POST de forma tolerante.
    """
    cantidad_raw = request.form.get('cantidad', '0')
    try:
        cantidad = int(float(cantidad_raw or 0))
    except Exception:
        cantidad = 0

    estado = (
        request.form.get('estado')
        or request.form.get('estado1')
        or ''
    )

    fecha_creacion = (
        request.form.get('fecha_creacion')
        or request.form.get('fecha_alta')
        or ''
    )

    fecha_fin = (
        request.form.get('fecha_fin')
        or request.form.get('fecha_baja')
        or ''
    )

    return {
        'codigo': _normalizar_texto(request.form.get('codigo')),
        'nombre': _normalizar_texto(request.form.get('nombre')),
        'cantidad': cantidad,
        'equipo': _normalizar_texto(request.form.get('equipo')),
        'estado': _normalizar_texto(estado),
        'link': _normalizar_texto(request.form.get('link')),
        'comentario': _normalizar_texto(request.form.get('comentario')),
        'fecha_creacion': _normalizar_texto(fecha_creacion),
        'fecha_fin': _normalizar_texto(fecha_fin),
        'ruta_jerarquia': _obtener_rutas_jerarquia_from_form(),
    }


def _repuesto_coincide_ruta_jerarquia(repuesto, ruta_objetivo):
    ruta_objetivo = _normalizar_texto(ruta_objetivo).lower()
    if not ruta_objetivo:
        return True

    rutas = [
        _normalizar_texto(r).lower()
        for r in _normalizar_lista_rutas_repuesto(repuesto)
        if _normalizar_texto(r)
    ]

    return ruta_objetivo in rutas


def _filtro_buscar(repuestos, buscar):
    """
    Filtro global de texto para tablas/PDF.
    """
    buscar = _normalizar_texto(buscar).lower()
    if not buscar:
        return list(repuestos)

    resultado = []

    for r in repuestos:
        partes = [
            _normalizar_texto(r.get('nombre', '')),
            _normalizar_texto(r.get('codigo', '')),
            _normalizar_texto(r.get('equipo', '')),
            _normalizar_texto(r.get('estado', '')),
            str(r.get('cantidad', '')),
            _normalizar_texto(r.get('comentario', '')),
            _normalizar_texto(r.get('link', '')),
            _normalizar_texto(r.get('fecha_creacion', '')),
            _normalizar_texto(r.get('fecha_fin', '')),
        ]

        rutas = _normalizar_lista_rutas_repuesto(r)
        partes.extend(_normalizar_texto(x) for x in rutas if _normalizar_texto(x))

        texto = ' '.join(partes).lower()

        if buscar in texto:
            resultado.append(r)

    return resultado


# ============================================================
# REDIRECCIÓN DINÁMICA
# ============================================================
def _endpoint_existe(endpoint):
    """
    Verifica si el endpoint existe en la aplicación actual.
    Esto permite que futuras apps usen return_to sin modificar este archivo.
    """
    endpoint = _normalizar_texto(endpoint)
    if not endpoint:
        return False

    try:
        for rule in current_app.url_map.iter_rules():
            if rule.endpoint == endpoint:
                return True
    except Exception:
        return False

    return False


def _endpoint_desde_referrer():
    """
    Si el return_to vino vacío o inválido, intenta deducir el destino
    desde la URL que originó el POST.
    """
    referrer = request.referrer or ''
    if not referrer:
        return ''

    try:
        path = urlparse(referrer).path or ''
    except Exception:
        return ''

    if path.startswith('/graficos_repuestos'):
        return 'indexgraficos_repuestos.indexgraficos_repuestos'

    if path.startswith('/lista_repuestos'):
        return 'indexlista_repuestos.indexlista_repuestos'

    if path.startswith('/inventario'):
        return 'indexinventario.indexinventario'

    if path.startswith('/estadosRep'):
        return 'indexEstadoRep.indexEstadoRep'

    return ''


def _url_interna_desde_referrer(endpoint):
    """
    Si el referrer es una URL interna del mismo endpoint, la conserva.
    Esto ayuda a mantener filtros por querystring, por ejemplo:
    /graficos_repuestos?jerarquia=...
    """
    referrer = request.referrer or ''
    if not referrer:
        return None

    try:
        parsed = urlparse(referrer)

        if parsed.scheme and parsed.scheme not in ('http', 'https'):
            return None

        if parsed.netloc and parsed.netloc != request.host:
            return None

        expected_path = urlparse(url_for(endpoint)).path

        if parsed.path != expected_path:
            return None

        return urlunparse(parsed)
    except Exception:
        return None


def _redirigir(return_to, tab_activo):
    """
    Redirección dinámica según return_to.

    ✅ Corrige el problema de graficos_repuestos:
       antes, cualquier return_to desconocido caía siempre a estadosRep.

    Ahora:
    - si return_to es un endpoint válido, redirige ahí;
    - si no, intenta deducirlo del referrer;
    - si el referrer coincide con el endpoint, conserva queryparams;
    - si nada funciona, fallback seguro a estadosRep.
    """
    endpoint = _normalizar_texto(return_to)

    if not endpoint or not _endpoint_existe(endpoint):
        endpoint_from_referrer = _endpoint_desde_referrer()
        if endpoint_from_referrer and _endpoint_existe(endpoint_from_referrer):
            endpoint = endpoint_from_referrer
        else:
            endpoint = 'indexEstadoRep.indexEstadoRep'

    # Conservar URL exacta del referrer si es la misma página destino.
    referrer_url = _url_interna_desde_referrer(endpoint)
    if referrer_url:
        return redirect(referrer_url)

    kwargs = {}

    # Sólo estadosRep usa active_tab de forma nativa en este módulo.
    if endpoint == 'indexEstadoRep.indexEstadoRep' and tab_activo:
        kwargs['active_tab'] = tab_activo

    try:
        return redirect(url_for(endpoint, **kwargs))
    except BuildError:
        logger.warning(
            f"_redirigir: endpoint inválido '{endpoint}'. "
            f"Fallack a indexEstadoRep.indexEstadoRep"
        )

        if tab_activo:
            return redirect(url_for('indexEstadoRep.indexEstadoRep', active_tab=tab_activo))

        return redirect(url_for('indexEstadoRep.indexEstadoRep'))


# ============================================================
# RUTAS
# ============================================================
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

    buscar = _normalizar_texto(request.args.get('buscar', '')).lower()
    estado_actual = _normalizar_texto(request.args.get('estado', ''))

    active_tab = (
        request.args.get('active_tab')
        or (tabs[0].get('sanitized_id', '') if tabs else '')
    )

    for tab in tabs:
        ruta_tab = _normalizar_texto(tab.get('ruta_jerarquia', '')).lower()

        if ruta_tab:
            repuestos_filtrados = [
                r for r in repuestos
                if _repuesto_coincide_ruta_jerarquia(r, ruta_tab)
            ]
        else:
            repuestos_filtrados = list(repuestos)

        tab['repuestos_filtrados'] = _filtro_buscar(repuestos_filtrados, buscar)

    estados_disponibles = sorted(
        set(
            _normalizar_texto(r.get('estado', ''))
            for r in repuestos
            if _normalizar_texto(r.get('estado', ''))
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
        nombres_almacenes=nombres_almacenes,
        estados=estados,
        estados_disponibles=estados_disponibles,
        ubicaciones=ubicaciones
    )


@estadoRep_bp.route('/api/repuestos')
def api_repuestos():
    ruta_jerarquia = _normalizar_texto(request.args.get('ruta_jerarquia', '')).lower()
    repuestos = leer_repuestos()

    if ruta_jerarquia:
        repuestos_filtrados = [
            r for r in repuestos
            if _repuesto_coincide_ruta_jerarquia(r, ruta_jerarquia)
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

    ruta_jerarquia = _normalizar_texto(request.form.get("ruta_jerarquia", "")).lower()
    buscar = _normalizar_texto(request.form.get("buscar", "")).lower()

    repuestos = leer_repuestos()

    if ruta_jerarquia:
        repuestos_filtrados = [
            r for r in repuestos
            if _repuesto_coincide_ruta_jerarquia(r, ruta_jerarquia)
        ]
    else:
        repuestos_filtrados = list(repuestos)

    repuestos_filtrados = _filtro_buscar(repuestos_filtrados, buscar)

    return exportar_pdf_reportlab(repuestos_filtrados)


@estadoRep_bp.route('/agregar_repuesto', methods=['POST'])
@login_required
@roles_required('viewer')
def agregar_repuesto():
    return_to = request.form.get('return_to', 'indexEstadoRep.indexEstadoRep')
    tab_activo = request.form.get('tab_activo', '')

    datos = _obtener_datos_repuesto_from_form()

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

    codigo_original = _normalizar_texto(
        request.form.get('codigo_original')
        or request.form.get('sanitized_id')
        or request.form.get('codigo')
    )

    if not codigo_original:
        flash("No se identificó el repuesto a editar.", "danger")
        return _redirigir(return_to, tab_activo)

    nuevos_datos = _obtener_datos_repuesto_from_form()

    if not nuevos_datos.get('codigo'):
        nuevos_datos['codigo'] = codigo_original

    # Si no viene nombre, intentar conservar el original para no romper NOT NULL.
    if not nuevos_datos.get('nombre'):
        rep_actual = obtener_repuesto_por_codigo(codigo_original)
        if rep_actual:
            nuevos_datos['nombre'] = rep_actual.get('nombre', '')

    filename, error = procesar_imagen(request.files.get('imagen'))

    if error:
        flash(error, "danger")
        return _redirigir(return_to, tab_activo)

    if filename:
        nuevos_datos['imagen'] = filename

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

    codigo = _normalizar_texto(
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
    tab_activo = tabs[0] if tabs else {}

    repuestos = leer_repuestos()

    estados_disponibles = sorted(
        set(
            _normalizar_texto(r.get('estado', ''))
            for r in repuestos
            if _normalizar_texto(r.get('estado', ''))
        )
    )

    if estado:
        repuestos_filtrados = [
            r for r in repuestos
            if _normalizar_texto(r.get('estado', '')) == _normalizar_texto(estado)
        ]
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
        tabs=tabs,
        tab=tab_activo,
        active_tab=tab_activo.get('sanitized_id', '') if isinstance(tab_activo, dict) else '',
        ubicaciones=ubicaciones,
        nombres_almacenes=nombres_almacenes,
        estados=estados
    )