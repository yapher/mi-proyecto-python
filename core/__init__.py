# core/__init__.py
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
from .repuestos import (
    cargar_todos_repuestos,
    cargar_arbol_almacenes,
    construir_mapeo_repuestos_por_almacen,
    obtener_repuestos_para_almacen,
    contar_repuestos_por_estado,
    filtrar_repuestos,
    obtener_repuesto_por_codigo,
    existe_codigo,
    crear_repuesto,
    actualizar_repuesto,
    eliminar_repuesto,
    guardar_todos_repuestos,
)

# Stores SQL
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
    plano_store,
)

__all__ = [
    'crear_blueprint_arbol',
    'cargar_menu',
    'guardar_menu',
    'cargar_almacenes',
    'cargar_estados',
    'cargar_ubicaciones',
    'cargar_tabs',
    'obtener_nombres_almacenes',
    'extraer_rutas',
    'procesar_imagen',
    'allowed_file',
    'calcular_hash_archivo',
    'calcular_hash_bytes',
    'obtener_ruta_absoluta',
    'url_para_imagen',
    'DEFAULT_UPLOAD_FOLDER',
    'DEFAULT_ALLOWED_EXTENSIONS',
    # repuestos
    'cargar_todos_repuestos',
    'cargar_arbol_almacenes',
    'construir_mapeo_repuestos_por_almacen',
    'obtener_repuestos_para_almacen',
    'contar_repuestos_por_estado',
    'filtrar_repuestos',
    'obtener_repuesto_por_codigo',
    'existe_codigo',
    'crear_repuesto',
    'actualizar_repuesto',
    'eliminar_repuesto',
    'guardar_todos_repuestos',
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
    'plano_store',
]