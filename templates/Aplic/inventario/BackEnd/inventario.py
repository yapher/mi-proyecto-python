# templates/Aplic/inventario/BackEnd/inventario.py
"""
Blueprint de Inventario — VERSIÓN SQL
Copia EXACTAMENTE la carga de datos de listarepuestos.py
"""
from flask_login import login_required, current_user
from core.menu import cargar_menu
from auth.login import roles_required
from flask import Blueprint, render_template
from core.repuestos import (
    cargar_todos_repuestos,
    construir_mapeo_repuestos_por_almacen,
)
from core.data_loaders import (
    cargar_ubicaciones,
    cargar_estados,
    cargar_almacenes,
    obtener_nombres_almacenes,
)

inventario_bp = Blueprint(
    'indexinventario',
    __name__,
    static_folder='../static',
    static_url_path='/inventario/static'
)


@inventario_bp.route('/inventario')
@login_required
@roles_required('viewer')
def indexinventario():
    nemu = cargar_menu()

    # ✅ CARGAR EXACTAMENTE IGUAL QUE listarepuestos.py
    repuestos = cargar_todos_repuestos()
    ubicaciones = cargar_ubicaciones()
    almacenes = cargar_almacenes()
    nombres_almacenes = obtener_nombres_almacenes(almacenes)
    estados = cargar_estados()

    repuestos_por_equipo = construir_mapeo_repuestos_por_almacen(
        repuestos=repuestos,
        almacenes=almacenes
    )

    return render_template(
        'Aplic/inventario/FrontEnd/inventario.html',
        nemu=nemu,
        roles=current_user.roles,
        almacenes=almacenes,
        repuestos_por_equipo=repuestos_por_equipo,
        # ✅ ESTAS 3 VARIABLES SON LAS QUE EL MODAL NECESITA
        ubicaciones=ubicaciones,
        estados=estados,
        nombres_almacenes=nombres_almacenes,
    )