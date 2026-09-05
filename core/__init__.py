"""
Módulos centrales reutilizables del proyecto.
Contiene funcionalidad compartida por múltiples aplicaciones.
"""
from .db_json import JsonStore
from .json_crud import UniqueFieldStore, JsonCrudStore
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
from .mes_store import MesStore

__all__ = [
    # db_json
    'JsonStore',
    # json_crud
    'UniqueFieldStore',
    'JsonCrudStore',
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
    # mes_store
    'MesStore',
]