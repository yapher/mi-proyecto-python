"""Blueprint de Crear Almacenes.
Usa el módulo genérico arbol_bp para el CRUD jerárquico.
"""
import os
from core.arbol_bp import crear_blueprint_arbol

# Ruta absoluta al static local de ESTA app
_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_STATIC_DIR = os.path.abspath(os.path.join(_APP_DIR, '..', 'static'))

crear_almacenes_bp = crear_blueprint_arbol(
    nombre_bp='indexcrear_almacenes',
    data_file='DataBase/dataRep/almacenes.json',
    template='Aplic/crearalmacenes/FrontEnd/crear_almacenes.html',
    vista_url='/crear_almacenes',
    clave_hijos='subcrear_almacenes',
    api_arbol_url='/api/crear_almacenes_arbol',
    api_crud_url='/api/crear_almacenes',
    campo_ruta_payload='ruta_crear_almacenes',
    item_nombre='almacén',
    endpoint_vista='indexcrear_almacenes',
    static_folder=_STATIC_DIR,
    static_url_path='/crearalmacenes/static'
)