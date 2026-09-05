"""
core/arbol_bp.py
================
Módulo reutilizable para CRUD de árboles jerárquicos.
Usado por: rubros, almacenes, ubicaciones, menú, procedimientos.
"""
import json
import os
from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from core.menu import cargar_menu
from auth.login import roles_required

def _split_ruta(ruta, separador):
    if not ruta:
        return []
    if separador == '||':
        return [p for p in ruta.split('||') if p]
    return [p for p in ruta.split(separador) if p]

def _join_ruta(partes, separador):
    return separador.join(partes)

def agregar_nodo(nodos, nombre, emoji, ruta, ruta_padre, clave_hijos, separador='-'):
    partes = _split_ruta(ruta_padre, separador)
    actual = nodos
    for parte in partes:
        nodo = next((u for u in actual if u['nombre'] == parte), None)
        if not nodo:
            return False
        if clave_hijos not in nodo:
            nodo[clave_hijos] = []
        actual = nodo[clave_hijos]
    
    nuevo = {
        'nombre': nombre,
        'emoji': emoji,
        'ruta': ruta,
        'ruta_jerarquia': f"{ruta_padre}{separador if ruta_padre else ''}{nombre}",
        clave_hijos: []
    }
    actual.append(nuevo)
    return True

def buscar_y_actualizar(nodos, ruta, nuevos_datos, clave_hijos, separador='-'):
    for nodo in nodos:
        if nodo['ruta_jerarquia'] == ruta:
            if 'nombre' in nuevos_datos:
                partes = _split_ruta(ruta, separador)
                partes[-1] = nuevos_datos['nombre']
                nuevos_datos['ruta_jerarquia'] = _join_ruta(partes, separador)
            nodo.update(nuevos_datos)
            return True
        if clave_hijos in nodo:
            if buscar_y_actualizar(nodo[clave_hijos], ruta, nuevos_datos, clave_hijos, separador):
                return True
    return False

def eliminar_nodo(nodos, ruta, clave_hijos, separador='-'):
    for i, nodo in enumerate(nodos):
        if nodo['ruta_jerarquia'] == ruta:
            nodos.pop(i)
            return True
        if clave_hijos in nodo:
            if eliminar_nodo(nodo[clave_hijos], ruta, clave_hijos, separador):
                return True
    return False

def construir_arbol(menus, ruta_padre="", separador="."):
    resultado = []
    for menu in menus:
        ruta_actual = f"{ruta_padre}{separador}{menu['nombre']}" if ruta_padre else menu['nombre']
        clave_hijos = next(
            (k for k in menu.keys() if k.startswith('sub')),
            'submenues'
        )
        nodo = {
            'nombre': menu['nombre'],
            'emoji': menu['emoji'],
            'ruta': menu.get('ruta', ''),
            'ruta_jerarquia': ruta_actual,
            clave_hijos: construir_arbol(
                menu.get(clave_hijos, []), ruta_actual, separador
            )
        }
        resultado.append(nodo)
    return resultado

def crear_blueprint_arbol(
    nombre_bp,
    data_file,
    template,
    vista_url,
    clave_hijos,
    api_arbol_url,
    api_crud_url,
    item_nombre,
    campo_ruta_payload,
    endpoint_vista,
    msg_agregar='Elemento agregado correctamente',
    separador='-',
    static_folder=None,
    static_url_path=None,
):
    kwargs = {}
    if static_folder:
        kwargs['static_folder'] = static_folder
    if static_url_path:
        kwargs['static_url_path'] = static_url_path
        
    bp = Blueprint(nombre_bp, __name__, **kwargs)
    
    def cargar_datos():
        if not os.path.exists(data_file):
            return []
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def guardar_datos(data):
        os.makedirs(os.path.dirname(data_file) or '.', exist_ok=True)
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @bp.route(vista_url, endpoint=endpoint_vista)
    @login_required
    @roles_required('viewer', 'admin', 'editor')
    def vista_principal():
        nemu = cargar_menu()
        return render_template(
            template,
            nemu=nemu,
            roles=current_user.roles,
            separador=separador,
            item_nombre=item_nombre,
            titulo_padre='Seleccionar Padre',
            placeholder_nombre='Nombre del rubro',
            placeholder_emoji='Emoji (ej: 🛠️)',
            placeholder_ruta='Ruta (opcional)',
            col_emoji='Emoji',
            col_nombre='Nombre',
            col_ruta='Ruta',
            col_acciones='Acciones'
        )

    @bp.route(api_arbol_url, endpoint='api_arbol')
    @login_required
    @roles_required('viewer', 'admin', 'editor')
    def api_arbol():
        data = cargar_datos()
        return jsonify(construir_arbol(data, separador=separador))

    @bp.route(api_crud_url, methods=['POST'], endpoint='api_crear')
    @login_required
    @roles_required('viewer', 'admin', 'editor')
    def api_crear():
        datos = cargar_datos()
        payload = request.get_json() or {}
        nombre = (payload.get('nombre') or '').strip()
        emoji = (payload.get('emoji') or '').strip()
        ruta = payload.get('ruta', '')
        ruta_padre = payload.get('ruta_padre', '')
        
        if not nombre or not emoji:
            return jsonify({'msg': 'Faltan campos obligatorios', 'type': 'error'}), 400
            
        partes_padre = _split_ruta(ruta_padre, separador)
        actual = datos
        for parte in partes_padre:
            nodo = next((u for u in actual if u['nombre'] == parte), None)
            if not nodo:
                return jsonify({'msg': 'Ruta padre inválida', 'type': 'error'}), 400
            actual = nodo.get(clave_hijos, [])
            
        if any(item.get('nombre') == nombre for item in actual):
            return jsonify({'msg': f'Ya existe {item_nombre} con ese nombre', 'type': 'info'}), 400
            
        exito = agregar_nodo(datos, nombre, emoji, ruta, ruta_padre, clave_hijos, separador)
        if not exito:
            return jsonify({'msg': 'No se encontró el padre', 'type': 'error'}), 400
            
        guardar_datos(datos)
        return jsonify({'msg': msg_agregar, 'type': 'success'})

    @bp.route(api_crud_url, methods=['PUT'], endpoint='api_editar')
    @login_required
    @roles_required('viewer', 'admin', 'editor')
    def api_editar():
        datos = cargar_datos()
        payload = request.get_json() or {}
        ruta_original = payload.get('ruta') or payload.get('ruta_original')
        nombre = (payload.get('nombre') or '').strip()
        emoji = (payload.get('emoji') or '').strip()
        ruta_item = payload.get(campo_ruta_payload, '')
        
        if not ruta_original or not nombre or not emoji:
            return jsonify({'msg': 'Faltan campos obligatorios', 'type': 'error'}), 400
            
        nuevos_datos = {
            'nombre': nombre,
            'emoji': emoji,
            'ruta': ruta_item
        }
        
        exito = buscar_y_actualizar(datos, ruta_original, nuevos_datos, clave_hijos, separador)
        if not exito:
            return jsonify({'msg': f'No se encontró el {item_nombre}', 'type': 'error'}), 404
            
        guardar_datos(datos)
        return jsonify({
            'msg': f'{item_nombre.capitalize()} actualizado correctamente',
            'type': 'success'
        })

    @bp.route(api_crud_url, methods=['DELETE'], endpoint='api_eliminar')
    @login_required
    @roles_required('viewer', 'admin', 'editor')
    def api_eliminar():
        datos = cargar_datos()
        payload = request.get_json() or {}
        ruta = payload.get('ruta')
        
        if not ruta:
            return jsonify({'msg': 'Ruta requerida', 'type': 'error'}), 400
            
        exito = eliminar_nodo(datos, ruta, clave_hijos, separador)
        if not exito:
            return jsonify({'msg': f'No se encontró el {item_nombre}', 'type': 'error'}), 404
            
        guardar_datos(datos)
        return jsonify({
            'msg': f'{item_nombre.capitalize()} eliminado correctamente',
            'type': 'success'
        })

    return bp