"""
Blueprint de Inventario — VERSIÓN SQL
Lee almacenes y repuestos desde SQL.
"""
from flask_login import login_required, current_user
from core.menu import cargar_menu
from auth.login import roles_required
from flask import Blueprint, render_template
from core.db_sql_store import almacen_store, repuesto_store

inventario_bp = Blueprint('indexinventario', __name__)


@inventario_bp.route('/inventario')
@login_required
@roles_required('viewer')
def indexinventario():
    nemu = cargar_menu()

    # ✅ Leer desde SQL
    almacenes = almacen_store.cargar_arbol()
    repuestos = repuesto_store.cargar()

    # Crear diccionario de repuestos por equipo (ruta_jerarquia del almacén)
    repuestos_por_equipo = {}
    for r in repuestos:
        equipo = r.get("equipo", "")
        repuestos_por_equipo.setdefault(equipo, []).append(r)

    return render_template(
        'Aplic/inventario/FrontEnd/inventario.html',
        nemu=nemu,
        roles=current_user.roles,
        almacenes=almacenes,
        repuestos_por_equipo=repuestos_por_equipo,
    )