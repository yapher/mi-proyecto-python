"""
Blueprint de Crear Rubros.
Usa el módulo genérico arbol_bp para el CRUD jerárquico.
"""
import os
from core.arbol_bp import crear_blueprint_arbol

# Ruta absoluta al static de ESTA app
_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_STATIC_DIR = os.path.abspath(os.path.join(_APP_DIR, '..', 'static'))

crear_rubros_bp = crear_blueprint_arbol(
    nombre_bp='indexcrear_rubros',
    data_file='DataBase/hogar/rubro.json',
    template='Aplic/crearrubros/FrontEnd/crear_rubros.html',
    vista_url='/crear_rubros',
    clave_hijos='submenues',
    api_arbol_url='/api/rubro_arbol',
    api_crud_url='/api/rubro',
    campo_ruta_payload='ruta_menu',
    item_nombre='rubro',
    endpoint_vista='indexcrear_rubros',
    msg_agregar='Rubro agregado correctamente',
    separador='.',
    static_folder=_STATIC_DIR,
    static_url_path='/crearrubros/static',
)