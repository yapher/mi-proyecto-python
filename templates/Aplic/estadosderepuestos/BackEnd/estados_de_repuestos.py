from flask_login import login_required, current_user
from menu import cargar_menu
from login import roles_required
from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, current_app
import json, re, os
from werkzeug.utils import secure_filename
from templates.Aplic.estadosderepuestos.BackEnd.export_pdf import exportar_pdf_reportlab

PATHTABS = 'DataBase/tabs.json'
PATHREPUESTOS = 'DataBase/dataRep/REPUESTOS.json'
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
DATA_FILE = 'DataBase/dataRep/almacenes.json'
DATA_ESTADOS = 'DataBase/dataRep/estados.json'
UBI_TEC = 'DataBase/dataRep/ubicacion_tecnica.json'

estadoRep_bp = Blueprint('indexEstadoRep', __name__)

# Función recursiva para extraer todas las rutas jerárquicas (robusta)
def extraer_rutas(data, rutas):
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                ruta = item.get("ruta_jerarquia")
                if ruta:
                    rutas.append(ruta)
                # Intentar diferentes nombres de sublistas por compatibilidad
                sub = item.get("sububicaciones") or item.get("subcrear_almacenes") or item.get("subalmacenes") or []
                if sub:
                    extraer_rutas(sub, rutas)
    elif isinstance(data, dict):
        ruta = data.get("ruta_jerarquia")
        if ruta:
            rutas.append(ruta)
        sub = data.get("sububicaciones") or data.get("subcrear_almacenes") or data.get("subalmacenes") or []
        if sub:
            extraer_rutas(sub, rutas)

def cargar_ubicaciones():
    if not os.path.exists(UBI_TEC):
        print(f"[WARN] No existe el archivo de ubicaciones: {UBI_TEC}")
        return []
    try:
        with open(UBI_TEC, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[ERROR] Al leer {UBI_TEC}: {e}")
        return []
    rutas = []
    extraer_rutas(data, rutas)
    # eliminar duplicados manteniendo orden
    seen = set()
    rutas_unicas = []
    for r in rutas:
        if r not in seen:
            rutas_unicas.append(r)
            seen.add(r)
    print(f"[DEBUG] cargadas {len(rutas_unicas)} ubicaciones técnicas")
    return rutas_unicas


def cargar_estados():
    if not os.path.exists(DATA_ESTADOS):
        print(f"[WARN] No existe {DATA_ESTADOS}")
        return []
    try:
        with open(DATA_ESTADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] leyendo estados: {e}")
        return []

def cargar_almacenes():
    if not os.path.exists(DATA_FILE):
        print(f"[WARN] No existe {DATA_FILE}")
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] leyendo almacenes: {e}")
        return []

def obtener_nombres_almacenes(almacenes):
    nombres = []
    for almacen in (almacenes or []):
        nombre = almacen.get('ruta_jerarquia') or almacen.get('nombre')
        if nombre:
            nombres.append(nombre)
        # soporte por si hay sublistas con nombre distinto
        sub = almacen.get('subcrear_almacenes') or almacen.get('sububicaciones') or almacen.get('subalmacenes') or []
        if sub:
            nombres.extend(obtener_nombres_almacenes(sub))
    return nombres


def cargar_tabs():
    if not os.path.exists(PATHTABS):
        print(f"[WARN] No existe {PATHTABS}")
        return []
    try:
        with open(PATHTABS, "r", encoding="utf-8") as f:
            tabs = json.load(f)
    except Exception as e:
        print(f"[ERROR] leyendo tabs: {e}")
        return []
    # Sanitizar los IDs de los tabs para que sean válidos en HTML
    for tab in tabs:
        original_id = str(tab.get('id', ''))
        sanitized_id = re.sub(r'\s+', '-', original_id.strip())  # Reemplaza espacios por guiones
        sanitized_id = re.sub(r'[^\w\-]', '', sanitized_id)      # Elimina caracteres no válidos
        tab['sanitized_id'] = sanitized_id
    return tabs

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def leer_repuestos():
    if not os.path.exists(PATHREPUESTOS):
        return []
    with open(PATHREPUESTOS, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def guardar_repuestos(repuestos):
    with open(PATHREPUESTOS, 'w', encoding='utf-8') as f:
        json.dump(repuestos, f, indent=4, ensure_ascii=False)

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

    return render_template('Aplic/estadosderepuestos/FrontEnd/estados_de_repuestos.html',
                           tabs=tabs, nemu=nemu, roles=current_user.roles, active_tab=active_tab, buscar=buscar,
                           nombres_almacenes=nombres_almacenes, estados=estados, ubicaciones=ubicaciones)

@estadoRep_bp.route('/api/repuestos')
def api_repuestos():
    ruta_jerarquia = request.args.get('ruta_jerarquia', '').lower()
    repuestos = leer_repuestos()
    repuestos_filtrados = [
        r for r in repuestos
        if any(ruta.lower() == ruta_jerarquia for ruta in r.get('ruta_jerarquia', []))
    ]
    return jsonify({'repuestos': repuestos_filtrados})


# Esta función exporta a un Archivo PDF la tabla de repuestos
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
    repuestos = leer_repuestos()

    nombre = request.form.get('nombre', '').strip()
    codigo = request.form.get('codigo', '').strip()
    cantidad = request.form.get('cantidad', '').strip()
    equipo = request.form.get('equipo', '').strip()
    ruta_jerarquia = request.form.getlist('ruta_jerarquia[]')
    fecha_creacion = request.form.get('fecha_creacion', '').strip()
    fecha_fin = request.form.get('fecha_fin', '').strip()
    link = request.form.get('link', '').strip()
    estado = request.form.get('estado', '').strip()
    tab_activo = request.form.get('tab_activo', '')

    # Validar campos obligatorios
    if not nombre or not codigo or not cantidad or not fecha_creacion or not estado:
        flash("Por favor completa los campos obligatorios.", "danger")
        return redirect(url_for('indexEstadoRep.indexEstadoRep', active_tab=tab_activo))

    try:
        cantidad = int(cantidad)
    except ValueError:
        flash("Cantidad debe ser un número entero.", "danger")
        return redirect(url_for('indexEstadoRep.indexEstadoRep', active_tab=tab_activo))

    # Verificar si el código ya existe
    for repuesto in repuestos:
        if repuesto.get('codigo') == codigo:
            flash("Ya existe un repuesto con el mismo código.", "warning")
            return redirect(url_for('indexEstadoRep.indexEstadoRep', active_tab=tab_activo))

    # Procesar imagen
    imagen_file = request.files.get('imagen')
    filename = None
    if imagen_file and imagen_file.filename != '':
        if allowed_file(imagen_file.filename):
            filename = secure_filename(imagen_file.filename)
            save_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            imagen_file.save(save_path)
        else:
            flash("Formato de imagen no permitido.", "danger")
            return redirect(url_for('indexEstadoRep.indexEstadoRep', active_tab=tab_activo))

    # Construir nuevo repuesto
    nuevo_repuesto = {
        "nombre": nombre,
        "codigo": codigo,
        "cantidad": cantidad,
        "equipo": equipo,
        "ruta_jerarquia": ruta_jerarquia,
        "imagen": filename,
        "fecha_creacion": fecha_creacion,
        "fecha_fin": fecha_fin,
        "link": link,
        "estado": estado
    }

    repuestos.append(nuevo_repuesto)
    guardar_repuestos(repuestos)

    flash("Repuesto agregado correctamente.", "success")
    return redirect(url_for('indexEstadoRep.indexEstadoRep', active_tab=tab_activo))

@estadoRep_bp.route('/eliminar_repuesto', methods=['POST'])
@login_required
@roles_required('viewer')
def eliminar_repuesto():
    codigo = request.form.get('codigo', '').strip()
    tab_activo = request.form.get('tab_activo', '')
    repuestos = leer_repuestos()
    repuestos_nuevos = [r for r in repuestos if str(r.get('codigo', '')) != codigo]
    if len(repuestos_nuevos) < len(repuestos):
        guardar_repuestos(repuestos_nuevos)
        flash("Repuesto eliminado correctamente.", "success")
    else:
        flash("No se encontró el repuesto a eliminar.", "danger")
    return redirect(url_for('indexEstadoRep.indexEstadoRep', active_tab=tab_activo))

@estadoRep_bp.route('/editar_repuesto', methods=['POST'])
@login_required
@roles_required('viewer')
def editar_repuesto():
    repuestos = leer_repuestos()
    
    codigo_original = request.form.get('codigo_original', '').strip()  # Código viejo
    codigo_nuevo = request.form.get('codigo', '').strip()  # Código nuevo (editable)

    tab_activo = request.form.get('tab_activo', '')

    for r in repuestos:
        if str(r.get('codigo', '')) == codigo_original:
            r['codigo'] = codigo_nuevo  # Actualiza el código
            r['nombre'] = request.form.get('nombre', '').strip()
            try:
                r['cantidad'] = int(request.form.get('cantidad', '').strip())
            except Exception:
                r['cantidad'] = r.get('cantidad', 0)
            r['equipo'] = request.form.get('equipo', '').strip()
            r['ruta_jerarquia'] = request.form.getlist('ruta_jerarquia[]')
            r['fecha_creacion'] = request.form.get('fecha_creacion', '').strip()
            r['fecha_fin'] = request.form.get('fecha_fin', '').strip()
            r['link'] = request.form.get('link', '').strip()
            r['estado'] = request.form.get('estado', '').strip()
            imagen_file = request.files.get('imagen')
            if imagen_file and imagen_file.filename != '':
                if allowed_file(imagen_file.filename):
                    filename = secure_filename(imagen_file.filename)
                    save_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    imagen_file.save(save_path)
                    r['imagen'] = filename
                else:
                    flash("Formato de imagen no permitido.", "danger")
                    return redirect(url_for('indexEstadoRep.indexEstadoRep', active_tab=tab_activo))
            break

    guardar_repuestos(repuestos)
    flash("Repuesto editado correctamente.", "success")
    return redirect(url_for('indexEstadoRep.indexEstadoRep', active_tab=tab_activo))


@estadoRep_bp.route('/filtrar_por_estado', methods=['GET'])
@login_required
@roles_required('viewer')
def estado_filter():
    estado = request.args.get('estado')
    ruta_jerarquia = request.args.get('ruta_jerarquia')

    # Usamos cargar_tabs para garantizar sanitized_id
    pestañas = cargar_tabs()
    pestaña_activa = pestañas[0] if pestañas else {}

    try:
        repuestos = leer_repuestos()
    except Exception:
        repuestos = []

    estados_disponibles = sorted(set(r.get('estado', '') for r in repuestos if r.get('estado')))

    if estado:
        repuestos_filtrados = [r for r in repuestos if r.get('estado') == estado]
    else:
        repuestos_filtrados = repuestos

    # ✅ Pasar siempre ubicaciones y otros datos que usa el modal
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
