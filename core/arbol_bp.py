"""
core/arbol_bp.py
================
Módulo reutilizable para CRUD de árboles jerárquicos.
AHORA USA SQL en lugar de JSON.
"""
import os
from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from core.menu import cargar_menu
from auth.login import roles_required
from core.db_sql_store import (
    menu_store, rubro_store, almacen_store, ubicacion_store
)
from core.db_sql import db


# ============================================================
# MAPEO: data_file → store SQL
# ============================================================
_STORE_MAP = {
    'DataBase/Config/menu.json': menu_store,
    'DataBase/hogar/rubro.json': rubro_store,
    'DataBase/dataRep/almacenes.json': almacen_store,
    'DataBase/dataRep/ubicacion_tecnica.json': ubicacion_store,
}


def _get_store(data_file):
    """Obtiene el store SQL correspondiente al archivo JSON original."""
    store = _STORE_MAP.get(data_file)
    if store:
        return store
    
    # Fallback por nombre de archivo
    basename = os.path.basename(data_file).lower()
    if 'menu' in basename:
        return menu_store
    elif 'rubro' in basename:
        return rubro_store
    elif 'almacen' in basename:
        return almacen_store
    elif 'ubicacion' in basename:
        return ubicacion_store
    
    raise ValueError(f"No se encontró store SQL para: {data_file}")


# ============================================================
# FACTORY: crear_blueprint_arbol
# ============================================================
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
    """
    Factory que crea un Blueprint con CRUD jerárquico usando SQL.
    """
    kwargs = {}
    if static_folder:
        kwargs['static_folder'] = static_folder
    if static_url_path:
        kwargs['static_url_path'] = static_url_path

    bp = Blueprint(nombre_bp, __name__, **kwargs)
    
    # Obtener el store SQL
    store = _get_store(data_file)
    separador_real = store.separador
    
    print(f"[arbol_bp] Registrando blueprint '{nombre_bp}' para '{data_file}'")
    print(f"  → Store: {store.model.__name__}, separador: '{separador_real}', clave_hijos: '{clave_hijos}'")

    # ========================================================
    # VISTA PRINCIPAL
    # ========================================================
    @bp.route(vista_url, endpoint=endpoint_vista)
    @login_required
    @roles_required('viewer', 'admin', 'editor')
    def vista_principal():
        nemu = cargar_menu()
        return render_template(
            template,
            nemu=nemu,
            roles=current_user.roles,
            separador=separador_real,
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

    # ========================================================
    # API: Obtener árbol completo
    # ========================================================
    @bp.route(api_arbol_url, endpoint='api_arbol')
    @login_required
    @roles_required('viewer', 'admin', 'editor')
    def api_arbol():
        arbol = store.cargar_arbol()
        print(f"[{nombre_bp}] api_arbol → {len(arbol)} raíces")
        return jsonify(arbol)

    # ========================================================
    # API: Crear nodo
    # ========================================================
    @bp.route(api_crud_url, methods=['POST'], endpoint='api_crear')
    @login_required
    @roles_required('viewer', 'admin', 'editor')
    def api_crear():
        payload = request.get_json() or {}
        nombre = (payload.get('nombre') or '').strip()
        emoji = (payload.get('emoji') or '').strip()
        ruta = payload.get('ruta', '')
        ruta_padre = payload.get('ruta_padre', '')

        print(f"[{nombre_bp}] CREAR: nombre='{nombre}', emoji='{emoji}', ruta='{ruta}', padre='{ruta_padre}'")

        if not nombre or not emoji:
            return jsonify({'msg': 'Faltan campos obligatorios', 'type': 'error'}), 400

        exito, msg = store.agregar(nombre, emoji, ruta, ruta_padre)
        print(f"[{nombre_bp}] CREAR resultado: exito={exito}, msg='{msg}'")
        
        if not exito:
            return jsonify({'msg': msg, 'type': 'error'}), 400

        return jsonify({'msg': msg_agregar, 'type': 'success'})

    # ========================================================
    # API: Editar nodo
    # ========================================================
    @bp.route(api_crud_url, methods=['PUT'], endpoint='api_editar')
    @login_required
    @roles_required('viewer', 'admin', 'editor')
    def api_editar():
        payload = request.get_json() or {}
        print(f"[{nombre_bp}] EDITAR payload completo: {payload}")
        
        # Buscar la ruta original en múltiples campos posibles
        ruta_original = (
            payload.get('ruta_original') or 
            payload.get('ruta') or 
            payload.get('ruta_jerarquia')
        )
        
        nombre = (payload.get('nombre') or '').strip()
        emoji = (payload.get('emoji') or '').strip()
        ruta_item = payload.get(campo_ruta_payload, '')

        print(f"[{nombre_bp}] EDITAR: ruta_original='{ruta_original}', nombre='{nombre}', emoji='{emoji}', campo_ruta='{ruta_item}'")

        if not ruta_original:
            return jsonify({'msg': 'Falta ruta_original', 'type': 'error'}), 400
        if not nombre or not emoji:
            return jsonify({'msg': 'Faltan campos obligatorios', 'type': 'error'}), 400

        nuevos_datos = {
            'nombre': nombre,
            'emoji': emoji,
            'ruta': ruta_item
        }
        
        exito, msg = store.editar(ruta_original, nuevos_datos)
        print(f"[{nombre_bp}] EDITAR resultado: exito={exito}, msg='{msg}'")
        
        if not exito:
            return jsonify({'msg': f'No se encontró el {item_nombre} con ruta "{ruta_original}"', 'type': 'error'}), 404

        return jsonify({
            'msg': f'{item_nombre.capitalize()} actualizado correctamente',
            'type': 'success'
        })

    # ========================================================
    # API: Eliminar nodo
    # ========================================================
    @bp.route(api_crud_url, methods=['DELETE'], endpoint='api_eliminar')
    @login_required
    @roles_required('viewer', 'admin', 'editor')
    def api_eliminar():
        payload = request.get_json() or {}
        ruta = payload.get('ruta') or payload.get('ruta_jerarquia')
        
        print(f"[{nombre_bp}] ELIMINAR: ruta='{ruta}'")
        
        if not ruta:
            return jsonify({'msg': 'Ruta requerida', 'type': 'error'}), 400

        exito, msg = store.eliminar(ruta)
        print(f"[{nombre_bp}] ELIMINAR resultado: exito={exito}, msg='{msg}'")
        
        if not exito:
            return jsonify({'msg': f'No se encontró el {item_nombre}', 'type': 'error'}), 404

        return jsonify({
            'msg': f'{item_nombre.capitalize()} eliminado correctamente',
            'type': 'success'
        })

    return bp