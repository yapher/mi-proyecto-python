"""
Blueprint de Estadística de Paradas.
Genera gráficos a partir de avisos de paradas.
"""
from flask_login import login_required, current_user
from core.menu import cargar_menu
from auth.login import roles_required
from flask import Blueprint, jsonify, request, render_template, session
import json, os, tempfile
from collections import Counter
from datetime import datetime

from .parser import (
    parse_date_to_dt,
    parsear_avisos_desde_texto,
    parsear_avisos_default,
    obtener_columnas
)

_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_STATIC_DIR = os.path.abspath(os.path.join(_APP_DIR, '..', 'static'))

estadistica_de_paradas_bp = Blueprint(
    'indexestadistica_de_paradas',
    __name__,
    static_folder=_STATIC_DIR,
    static_url_path='/estadisticadeparadas/static'
)

# ============================================================
# RUTAS
# ============================================================
@estadistica_de_paradas_bp.route('/estadistica_de_paradas')
@login_required
@roles_required('viewer')
def indexestadistica_de_paradas():
    nemu = cargar_menu()
    columnas = obtener_columnas()
    avisos = parsear_avisos_default()
    
    fechas_validas = [parse_date_to_dt(a.get('Fecha')) for a in avisos if parse_date_to_dt(a.get('Fecha'))]
    rango_fechas = {
        'min': min(fechas_validas).strftime('%d.%m.%Y') if fechas_validas else None,
        'max': max(fechas_validas).strftime('%d.%m.%Y') if fechas_validas else None
    }
    
    agrupacion = Counter([a['Texto_codigo'] for a in avisos if a.get('Texto_codigo')])
    items_ordenados = agrupacion.most_common(15)
    
    return render_template(
        'Aplic/estadisticadeparadas/FrontEnd/estadistica_de_paradas.html',
        nemu=nemu, roles=current_user.roles, columnas=columnas,
        datos_iniciales=json.dumps({'categorias': [i[0] for i in items_ordenados], 'valores': [i[1] for i in items_ordenados]}),
        rango_fechas=json.dumps(rango_fechas)
    )

@estadistica_de_paradas_bp.route('/estadistica_de_paradas/cargar_archivo', methods=['POST'])
@login_required
def cargar_archivo():
    try:
        archivo = request.files.get('archivo')
        if not archivo or archivo.filename == '':
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
            
        avisos = parsear_avisos_desde_texto(archivo.read().decode('utf-8'))
        for a in avisos:
            dt = parse_date_to_dt(a.get('Fecha'))
            a['_Fecha_iso'] = dt.date().isoformat() if dt else None
            
        if not avisos:
            return jsonify({'error': 'No se pudieron extraer datos del archivo.'}), 400
            
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode='w', encoding='utf-8')
        json.dump(avisos, tmp, ensure_ascii=False, indent=2)
        tmp.close()
        session['ruta_avisos_cargados'] = tmp.name
        
        fechas_validas = [parse_date_to_dt(a.get('Fecha')) for a in avisos if parse_date_to_dt(a.get('Fecha'))]
        rango_fechas = {
            'min': min(fechas_validas).strftime('%d.%m.%Y') if fechas_validas else None,
            'max': max(fechas_validas).strftime('%d.%m.%Y') if fechas_validas else None
        }
        
        agrupacion = Counter([a['Texto_codigo'] for a in avisos if a.get('Texto_codigo')])
        items_ordenados = agrupacion.most_common(15)
        
        return jsonify({
            'success': True, 'total_avisos': len(avisos),
            'categorias': [i[0] for i in items_ordenados],
            'valores': [i[1] for i in items_ordenados],
            'rango_fechas': rango_fechas
        })
    except Exception as e:
        return jsonify({'error': f'Error al procesar archivo: {str(e)}'}), 500

def _obtener_avisos_filtrados(fecha_inicio, fecha_fin):
    """Helper reutilizable para obtener avisos con filtro de fecha."""
    avisos = []
    ruta_tmp = session.get('ruta_avisos_cargados')
    try:
        if ruta_tmp and os.path.exists(ruta_tmp):
            with open(ruta_tmp, 'r', encoding='utf-8') as f:
                avisos = json.load(f)
        else:
            avisos = parsear_avisos_default()
    except Exception:
        avisos = parsear_avisos_default()
        
    start_dt = parse_date_to_dt(fecha_inicio) if fecha_inicio else None
    end_dt = parse_date_to_dt(fecha_fin) if fecha_fin else None
    
    if start_dt and end_dt and start_dt > end_dt:
        start_dt, end_dt = end_dt, start_dt
        
    if start_dt and end_dt:
        avisos_filtrados = []
        for a in avisos:
            fecha_dt = None
            if a.get('_Fecha_iso'):
                try: fecha_dt = datetime.fromisoformat(a['_Fecha_iso'])
                except Exception: pass
            if not fecha_dt:
                fecha_dt = parse_date_to_dt(a.get('Fecha', ''))
            if fecha_dt and start_dt.date() <= fecha_dt.date() <= end_dt.date():
                avisos_filtrados.append(a)
        return avisos_filtrados
    return avisos

@estadistica_de_paradas_bp.route('/estadistica_de_paradas/datos')
@login_required
def obtener_datos():
    columna = request.args.get('columna', 'Texto_codigo')
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    avisos = _obtener_avisos_filtrados(fecha_inicio, fecha_fin)
    valores_columna = [a.get(columna) for a in avisos if a.get(columna) and str(a.get(columna)).strip()]
    agrupacion = Counter(valores_columna)
    items_ordenados = agrupacion.most_common(15)
    
    return jsonify({
        'categorias': [str(i[0]) for i in items_ordenados],
        'valores': [i[1] for i in items_ordenados]
    })

@estadistica_de_paradas_bp.route('/estadistica_de_paradas/drilldown')
@login_required
def obtener_drilldown():
    categoria = request.args.get('categoria', '')
    columna_filtro = request.args.get('columna', 'Texto_codigo')
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    avisos = _obtener_avisos_filtrados(fecha_inicio, fecha_fin)
    avisos_filtrados = [a for a in avisos if a.get(columna_filtro) == categoria]
    columna_desglose = 'Ubicac_tecnica' if columna_filtro == 'Texto_codigo' else 'Texto_codigo'
    
    valores_desglose = [a.get(columna_desglose) for a in avisos_filtrados if a.get(columna_desglose) and str(a.get(columna_desglose)).strip()]
    agrupacion = Counter(valores_desglose)
    items_ordenados = agrupacion.most_common(10)
    
    return jsonify({
        'categorias': [str(i[0]) for i in items_ordenados],
        'valores': [i[1] for i in items_ordenados],
        'total_avisos': len(avisos_filtrados)
    })

@estadistica_de_paradas_bp.route('/estadistica_de_paradas/detalle')
@login_required
def obtener_detalle():
    categoria_principal = request.args.get('categoria_principal', '')
    categoria_secundaria = request.args.get('categoria_secundaria', '')
    columna_principal = request.args.get('columna_principal', 'Texto_codigo')
    columna_secundaria = request.args.get('columna_secundaria', 'Ubicac_tecnica')
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    avisos = _obtener_avisos_filtrados(fecha_inicio, fecha_fin)
    avisos_filtrados = [
        a for a in avisos
        if a.get(columna_principal) == categoria_principal and a.get(columna_secundaria) == categoria_secundaria
    ]
    
    return jsonify({'registros': avisos_filtrados, 'total': len(avisos_filtrados)})