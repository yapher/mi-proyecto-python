"""Blueprint de Crear Ubicación Técnica.

Usa el módulo genérico arbol_bp para el CRUD jerárquico.
"""
from arbol_bp import crear_blueprint_arbol

ubicacion_bp = crear_blueprint_arbol(
    nombre_bp='ubicacion',
    data_file='DataBase/dataRep/ubicacion_tecnica.json',
    template='Aplic/crearubicaciontecnica/FrontEnd/crear_ubicacion_tecnica.html',
    vista_url='/creaUbTec',
    clave_hijos='sububicaciones',
    api_arbol_url='/api/ubicacion_arbol',
    api_crud_url='/api/ubicacion',
    campo_ruta_payload='ruta_ubicacion',
    item_nombre='ubicación',
    endpoint_vista='creaUbiTec',
)