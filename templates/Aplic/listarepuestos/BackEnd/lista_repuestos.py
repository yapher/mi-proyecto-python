# templates/Aplic/listarepuestos/BackEnd/lista_repuestos.py
"""
Blueprint de Lista de Repuestos.
USA core/repuestos.py para funciones reutilizables.
"""
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from core.menu import cargar_menu
from auth.login import roles_required
from datetime import datetime
from templates.Aplic.estadosderepuestos.BackEnd.export_pdf import exportar_pdf_reportlab
from core.data_loaders import (
    cargar_tabs,
    cargar_almacenes,
    obtener_nombres_almacenes,
    cargar_estados,
    cargar_ubicaciones,
)
from core.repuestos import (
    cargar_todos_repuestos,
    filtrar_repuestos,
)

lista_repuestos_bp = Blueprint(
    'indexlista_repuestos',
    __name__,
    static_folder='../static',
    static_url_path='/lista_repuestos/static'
)


@lista_repuestos_bp.route('/lista_repuestos')
@login_required
@roles_required('viewer')
def indexlista_repuestos():
    nemu = cargar_menu()
    tabs = cargar_tabs()
    estados = cargar_estados()
    almacenes = cargar_almacenes()
    ubicaciones = cargar_ubicaciones()
    nombres_almacenes = obtener_nombres_almacenes(almacenes)

    filtros = {
        'nombre': request.args.get('nombre', '').strip(),
        'codigo': request.args.get('codigo', '').strip(),
        'estado': request.args.get('estado', '').strip(),
        'fecha_alta': request.args.get('fecha_alta', '').strip(),
        'fecha_baja': request.args.get('fecha_baja', '').strip(),
        'vencidos': request.args.get('vencidos', '').strip()
    }

    # ✅ Usar función reutilizable
    repuestos = cargar_todos_repuestos()

    hoy = datetime.today().date()
    cantidad_vencidos = 0
    for rep in repuestos:
        try:
            if rep.get('fecha_fin'):
                fecha_fin = datetime.strptime(rep['fecha_fin'], '%Y-%m-%d').date()
                if fecha_fin < hoy:
                    cantidad_vencidos += 1
        except Exception:
            pass

    # ✅ Usar función reutilizable de filtrado
    repuestos_filtrados = filtrar_repuestos(repuestos, filtros)

    if request.args.get('exportar_pdf') == '1':
        return exportar_pdf_reportlab(repuestos_filtrados)

    return render_template(
        'Aplic/listarepuestos/FrontEnd/lista_repuestos.html',
        nemu=nemu,
        roles=current_user.roles,
        repuestos=repuestos_filtrados,
        filtros=filtros,
        cantidad_vencidos=cantidad_vencidos,
        tabs=tabs,
        nombres_almacenes=nombres_almacenes,
        estados=estados,
        ubicaciones=ubicaciones,
        hoy_str=hoy.strftime('%Y-%m-%d')
    )