"""
Módulos centrales reutilizables del proyecto.
Versión SQL - todos los stores JSON legacy fueron migrados.
"""
from .arbol_bp import crear_blueprint_arbol
from .menu import cargar_menu, guardar_menu
from .data_loaders import (
    cargar_almacenes,
    cargar_estados,
    cargar_ubicaciones,
    cargar_tabs,
    obtener_nombres_almacenes,
    extraer_rutas,
)
from .image import (
    procesar_imagen,
    allowed_file,
    calcular_hash_archivo,
    calcular_hash_bytes,
    obtener_ruta_absoluta,
    url_para_imagen,
    DEFAULT_UPLOAD_FOLDER,
    DEFAULT_ALLOWED_EXTENSIONS,
)

# Stores SQL (reemplazan a los JSON stores legacy)
from .db_sql_store import (
    menu_store,
    rubro_store,
    almacen_store,
    ubicacion_store,
    tab_store,
    estado_store,
    repuesto_store,
    pago_store,
    nodo_bloqueo_store,
    evento_store,
    tarea_store,
)

__all__ = [
    # arbol_bp
    'crear_blueprint_arbol',
    # menu
    'cargar_menu',
    'guardar_menu',
    # data_loaders
    'cargar_almacenes',
    'cargar_estados',
    'cargar_ubicaciones',
    'cargar_tabs',
    'obtener_nombres_almacenes',
    'extraer_rutas',
    # image
    'procesar_imagen',
    'allowed_file',
    'calcular_hash_archivo',
    'calcular_hash_bytes',
    'obtener_ruta_absoluta',
    'url_para_imagen',
    'DEFAULT_UPLOAD_FOLDER',
    'DEFAULT_ALLOWED_EXTENSIONS',
    # Stores SQL
    'menu_store',
    'rubro_store',
    'almacen_store',
    'ubicacion_store',
    'tab_store',
    'estado_store',
    'repuesto_store',
    'pago_store',
    'nodo_bloqueo_store',
    'evento_store',
    'tarea_store',
]