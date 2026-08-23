# Archivo backend generado automáticamente

from flask_login import login_required, current_user
from core.menu import cargar_menu
from auth.login import roles_required
from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, current_app, session
import json, re, os
from collections import Counter
from werkzeug.utils import secure_filename

estadistica_de_paradas_bp = Blueprint('indexestadistica_de_paradas', __name__)

# Copiar y pegar estas dos linea en app.py
#from templates.Aplic.estadisticadeparadas.BackEnd.estadistica_de_paradas import estadistica_de_paradas_bp
#app.register_blueprint(estadistica_de_paradas_bp)

from datetime import datetime

def _parse_date_to_dt(s):
    """
    Intenta convertir s a datetime. Acepta:
      - 'DD.MM.YYYY'
      - 'DD/MM/YYYY'
      - 'YYYY-MM-DD'
    Devuelve datetime o None si no puede parsear.
    """
    if not s:
        return None
    s = s.strip()
    # limpiar caracteres invisibles
    s = s.replace('\ufeff', '').strip()
    fmts = ('%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d')
    for fmt in fmts:
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            pass
    # intentar extraer primera coincidencia tipo DD.MM.YYYY
    m = re.search(r'(\d{1,2}[./]\d{1,2}[./]\d{4})', s)
    if m:
        candidate = m.group(1)
        for fmt in ('%d.%m.%Y', '%d/%m/%Y'):
            try:
                return datetime.strptime(candidate, fmt)
            except:
                pass
    return None


def parsear_avisos_desde_texto(texto):
    """
    Parser robusto para ambos formatos:
      - acepta líneas que empiezan con '|' (con o sin 'X')
      - mantiene columnas vacías (no eliminar tokens vacíos)
      - busca el encabezado de forma flexible
      - devuelve una lista de dicts con las 12 columnas esperadas
    """
    avisos = []
    lineas = texto.splitlines()

    # Buscar encabezado de forma flexible (ej: contiene "Cl." y "Aviso")
    inicio_datos = 0
    for i, linea in enumerate(lineas):
        if re.search(r'\bCl\.?\b', linea, re.IGNORECASE) and re.search(r'\bAviso\b', linea, re.IGNORECASE):
            inicio_datos = i + 2  # saltar encabezado + separador
            break

    for linea in lineas[inicio_datos:]:
        if not linea or not linea.strip():
            continue
        # ignorar líneas de separador tipo "-----"
        if set(linea.strip()) <= set('- '):
            continue
        # requerir que empiece con '|' (la mayoría de filas válidas)
        if not linea.strip().startswith('|'):
            continue

        # NO eliminar tokens vacíos: split preserva la posición de columnas
        partes = linea.split('|')

        # necesitamos al menos Aviso (índice 2) con algún dígito
        if len(partes) < 3:
            continue
        aviso_token = partes[2].strip() if len(partes) > 2 else ''
        if not re.search(r'\d', aviso_token):  # si no hay número, probablemente no es fila de datos
            continue

        # helper: obtener token seguro por índice
        def g(i):
            return partes[i].strip() if i < len(partes) else ''

        aviso = {
            'Cl': g(1).replace('X', '').strip(),
            'Aviso': g(2),
            'Fecha': g(3),
            'Descripcion': g(4),
            'Equipo': g(5),
            'Ubicac_tecnica': g(6),
            'DurParada': g(7),
            'Aut_aviso': g(8),
            'Por': g(9),
            'Orden': g(10),
            'Fin_desead': g(11),
            'Texto_codigo': g(12)
        }
        avisos.append(aviso)

    print(f"✔ Total de avisos parseados: {len(avisos)}")
    return avisos


def parsear_avisos_default():
    ruta_archivo = os.path.join(current_app.static_folder, 'modelos', 'avisos.txt')
    try:
        with open(ruta_archivo, 'r', encoding='utf-8-sig') as f:
            texto = f.read()
        return parsear_avisos_desde_texto(texto)
    except Exception as e:
        print(f"Error al leer archivo por defecto: {e}")
        return []


def obtener_columnas():
    """Retorna lista de columnas disponibles para filtrar con nombres legibles"""
    return [
        {'key': 'Cl', 'nombre': 'Clase'},
        {'key': 'Aviso', 'nombre': 'Aviso'},
        {'key': 'Fecha', 'nombre': 'Fecha'},
        {'key': 'Descripcion', 'nombre': 'Descripción'},
        {'key': 'Equipo', 'nombre': 'Equipo'},
        {'key': 'Ubicac_tecnica', 'nombre': 'Ubicación Técnica'},
        {'key': 'DurParada', 'nombre': 'Duración Parada'},
        {'key': 'Aut_aviso', 'nombre': 'Autor Aviso'},
        {'key': 'Por', 'nombre': 'Por'},
        {'key': 'Orden', 'nombre': 'Orden'},
        {'key': 'Fin_desead', 'nombre': 'Fin Deseado'},
        {'key': 'Texto_codigo', 'nombre': 'Texto Código'}
    ]

@estadistica_de_paradas_bp.route('/estadistica_de_paradas')
@login_required
@roles_required('viewer')
def indexestadistica_de_paradas():
    nemu = cargar_menu()
    columnas = obtener_columnas()
    
    # Cargar datos por defecto
    avisos = parsear_avisos_default()
    
    print(f"Total de avisos cargados (default): {len(avisos)}")
    
    # Obtener rango de fechas (convertido correctamente)
    from datetime import datetime
    fechas_validas = []
    for a in avisos:
        f = a.get('Fecha')
        try:
            if f:
                fechas_validas.append(datetime.strptime(f, '%d.%m.%Y'))
        except:
            pass

    if fechas_validas:
        rango_fechas = {
            'min': min(fechas_validas).strftime('%d.%m.%Y'),
            'max': max(fechas_validas).strftime('%d.%m.%Y')
        }
    else:
        rango_fechas = {'min': None, 'max': None}
    
    # Datos iniciales agrupados por Texto_codigo
    from collections import Counter
    agrupacion = Counter([a['Texto_codigo'] for a in avisos if a.get('Texto_codigo')])
    items_ordenados = agrupacion.most_common(15)
    
    categorias = [item[0] for item in items_ordenados]
    valores = [item[1] for item in items_ordenados]
    
    datos_iniciales = {
        'categorias': categorias,
        'valores': valores
    }
    
    return render_template(
        'Aplic/estadisticadeparadas/FrontEnd/estadistica_de_paradas.html',
        nemu=nemu, 
        roles=current_user.roles,
        columnas=columnas,
        datos_iniciales=json.dumps(datos_iniciales),
        rango_fechas=json.dumps(rango_fechas)
    )


import tempfile, json, os
from collections import Counter

@estadistica_de_paradas_bp.route('/estadistica_de_paradas/cargar_archivo', methods=['POST'])
@login_required
def cargar_archivo():
    try:
        if 'archivo' not in request.files:
            return jsonify({'error': 'No se envió ningún archivo'}), 400
        
        archivo = request.files['archivo']
        if archivo.filename == '':
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
        contenido = archivo.read().decode('utf-8')
        avisos = parsear_avisos_desde_texto(contenido)

        # normalizar/dejar una fecha ISO por registro para acelerar filtros
        for a in avisos:
            dt = _parse_date_to_dt(a.get('Fecha'))
            a['_Fecha_iso'] = dt.date().isoformat() if dt else None

        if not avisos:
            return jsonify({'error': 'No se pudieron extraer datos del archivo. Verifica el formato.'}), 400

        # Guardar en archivo temporal
        import tempfile, json
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode='w', encoding='utf-8')
        json.dump(avisos, tmp, ensure_ascii=False, indent=2)
        tmp.close()

        session['ruta_avisos_cargados'] = tmp.name

        print(f"Archivo cargado exitosamente. Total de avisos: {len(avisos)}")

        # Obtener rango de fechas (convertido correctamente)
        from datetime import datetime
        fechas_validas = []
        for a in avisos:
            f = a.get('Fecha')
            try:
                if f:
                    fechas_validas.append(datetime.strptime(f, '%d.%m.%Y'))
            except:
                pass

        if fechas_validas:
            rango_fechas = {
                'min': min(fechas_validas).strftime('%d.%m.%Y'),
                'max': max(fechas_validas).strftime('%d.%m.%Y')
            }
        else:
            rango_fechas = {'min': None, 'max': None}

        # Agrupar por Texto_codigo
        from collections import Counter
        agrupacion = Counter([a['Texto_codigo'] for a in avisos if a.get('Texto_codigo')])
        items_ordenados = agrupacion.most_common(15)

        categorias = [item[0] for item in items_ordenados]
        valores = [item[1] for item in items_ordenados]

        return jsonify({
            'success': True,
            'total_avisos': len(avisos),
            'categorias': categorias,
            'valores': valores,
            'rango_fechas': rango_fechas
        })

    except Exception as e:
        print(f"Error al cargar archivo: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al procesar archivo: {str(e)}'}), 500



@estadistica_de_paradas_bp.route('/estadistica_de_paradas/datos')
@login_required
def obtener_datos():
    columna = request.args.get('columna', 'Texto_codigo')
    fecha_inicio = request.args.get('fecha_inicio')  # espera 'DD.MM.YYYY'
    fecha_fin = request.args.get('fecha_fin')        # espera 'DD.MM.YYYY'
    
    print(f"Solicitando datos: columna={columna}, desde={fecha_inicio}, hasta={fecha_fin}")

    # Cargar avisos (desde archivo temporal si existe, sino por defecto)
    avisos = []
    ruta_tmp = session.get('ruta_avisos_cargados')
    try:
        if ruta_tmp and os.path.exists(ruta_tmp):
            with open(ruta_tmp, 'r', encoding='utf-8') as f:
                avisos = json.load(f)
        else:
            avisos = parsear_avisos_default()
    except Exception as e:
        print(f"Error leyendo avisos: {e}")
        avisos = parsear_avisos_default()

    total_antes = len(avisos)

    # Preparar fechas de filtro
    start_dt = _parse_date_to_dt(fecha_inicio) if fecha_inicio else None
    end_dt = _parse_date_to_dt(fecha_fin) if fecha_fin else None

    if start_dt and end_dt and start_dt > end_dt:
        # si el usuario invirtió fechas, las permutamos
        start_dt, end_dt = end_dt, start_dt

    # Si existen fechas, filtrar usando datetime (comparar solo date() para ser inclusivo)
    if start_dt and end_dt:
        avisos_filtrados = []
        parse_errors = 0
        for a in avisos:
            # Preferir campo preprocesado si existe (opcional)
            fecha_iso = a.get('_Fecha_iso')
            fecha_dt = None
            if fecha_iso:
                try:
                    fecha_dt = datetime.fromisoformat(fecha_iso)
                except:
                    fecha_dt = None
            if not fecha_dt:
                fecha_dt = _parse_date_to_dt(a.get('Fecha', ''))
            if not fecha_dt:
                parse_errors += 1
                continue
            if start_dt.date() <= fecha_dt.date() <= end_dt.date():
                avisos_filtrados.append(a)
        avisos = avisos_filtrados
        print(f"Avisos antes: {total_antes}, después filter fechas: {len(avisos)}, parse_errors: {parse_errors}")
    else:
        print(f"No se aplicó filtro por fechas. Total avisos usados: {total_antes}")

    # Agrupar por columna solicitada
    valores_columna = [a.get(columna) for a in avisos if a.get(columna) and str(a.get(columna)).strip()]
    agrupacion = Counter(valores_columna)
    items_ordenados = agrupacion.most_common(15)

    categorias = [str(item[0]) for item in items_ordenados]
    valores = [item[1] for item in items_ordenados]

    resultado = {
        'categorias': categorias,
        'valores': valores
    }

    print(f"Resultado: {len(categorias)} categorías (top).")
    return jsonify(resultado)


@estadistica_de_paradas_bp.route('/estadistica_de_paradas/drilldown')
@login_required
def obtener_drilldown():
    """Endpoint para obtener datos drill-down cuando se hace clic en una categoría"""
    from datetime import datetime
    categoria = request.args.get('categoria', '')
    columna_filtro = request.args.get('columna', 'Texto_codigo')
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')

    print(f"Drill-down: Categoría={categoria}, Columna={columna_filtro}, desde={fecha_inicio}, hasta={fecha_fin}")

    # Obtener avisos
    avisos = []
    ruta_tmp = session.get('ruta_avisos_cargados')

    try:
        if ruta_tmp and os.path.exists(ruta_tmp):
            with open(ruta_tmp, 'r', encoding='utf-8') as f:
                avisos = json.load(f)
        else:
            avisos = parsear_avisos_default()
    except Exception as e:
        print(f"Error al leer datos: {e}")
        avisos = parsear_avisos_default()

    # --- NUEVO: aplicar filtro por fechas si está definido ---
    start_dt = _parse_date_to_dt(fecha_inicio) if fecha_inicio else None
    end_dt = _parse_date_to_dt(fecha_fin) if fecha_fin else None
    if start_dt and end_dt and start_dt > end_dt:
        start_dt, end_dt = end_dt, start_dt

    if start_dt and end_dt:
        avisos_filtrados = []
        for a in avisos:
            dt = _parse_date_to_dt(a.get('Fecha'))
            if dt and start_dt.date() <= dt.date() <= end_dt.date():
                avisos_filtrados.append(a)
        avisos = avisos_filtrados
        print(f"Avisos filtrados por fecha: {len(avisos)}")

    # Filtrar avisos por la categoría seleccionada
    avisos_filtrados = [a for a in avisos if a.get(columna_filtro) == categoria]

    # Determinar columna para desglose
    columna_desglose = 'Ubicac_tecnica' if columna_filtro == 'Texto_codigo' else 'Texto_codigo'

    # Agrupar
    valores_desglose = [a.get(columna_desglose) for a in avisos_filtrados if a.get(columna_desglose) and str(a.get(columna_desglose)).strip()]
    agrupacion = Counter(valores_desglose)

    items_ordenados = agrupacion.most_common(10)

    categorias = [str(item[0]) for item in items_ordenados]
    valores = [item[1] for item in items_ordenados]

    return jsonify({
        'categorias': categorias,
        'valores': valores,
        'total_avisos': len(avisos_filtrados)
    })


@estadistica_de_paradas_bp.route('/estadistica_de_paradas/detalle')
@login_required
def obtener_detalle():
    """Endpoint para obtener datos detallados para la tabla"""
    categoria_principal = request.args.get('categoria_principal', '')
    categoria_secundaria = request.args.get('categoria_secundaria', '')
    columna_principal = request.args.get('columna_principal', 'Texto_codigo')
    columna_secundaria = request.args.get('columna_secundaria', 'Ubicac_tecnica')
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')

    print(f"Detalle: Principal={categoria_principal}, Secundaria={categoria_secundaria}, Fechas={fecha_inicio}→{fecha_fin}")

    avisos = []
    ruta_tmp = session.get('ruta_avisos_cargados')

    try:
        if ruta_tmp and os.path.exists(ruta_tmp):
            with open(ruta_tmp, 'r', encoding='utf-8') as f:
                avisos = json.load(f)
        else:
            avisos = parsear_avisos_default()
    except Exception as e:
        print(f"Error: {e}")
        avisos = parsear_avisos_default()

    # --- NUEVO: aplicar filtro por fechas ---
    start_dt = _parse_date_to_dt(fecha_inicio) if fecha_inicio else None
    end_dt = _parse_date_to_dt(fecha_fin) if fecha_fin else None
    if start_dt and end_dt and start_dt > end_dt:
        start_dt, end_dt = end_dt, start_dt

    if start_dt and end_dt:
        avisos_filtrados_fecha = []
        for a in avisos:
            dt = _parse_date_to_dt(a.get('Fecha'))
            if dt and start_dt.date() <= dt.date() <= end_dt.date():
                avisos_filtrados_fecha.append(a)
        avisos = avisos_filtrados_fecha
        print(f"Avisos filtrados por fecha: {len(avisos)}")

    # Filtrar por ambas categorías
    avisos_filtrados = [
        a for a in avisos 
        if a.get(columna_principal) == categoria_principal 
        and a.get(columna_secundaria) == categoria_secundaria
    ]
    
    print(f"Total registros detalle (filtrados): {len(avisos_filtrados)}")

    return jsonify({
        'registros': avisos_filtrados,
        'total': len(avisos_filtrados)
    })
