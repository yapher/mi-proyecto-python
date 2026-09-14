# templates/Aplic/inventario/BackEnd/inventario.py
"""
Blueprint de Inventario — VERSIÓN SQL CORREGIDA
Usa el módulo reutilizable core/repuestos.py para el mapeo.
"""
from flask_login import login_required, current_user
from core.menu import cargar_menu
from auth.login import roles_required
from flask import Blueprint, render_template
from core.repuestos import (
    cargar_todos_repuestos,
    cargar_arbol_almacenes,
    construir_mapeo_repuestos_por_almacen,
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
    almacenes = cargar_arbol_almacenes()
    repuestos = cargar_todos_repuestos()

    # ✅ Mapeo robusto que cubre TODOS los casos de asignación
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
    )