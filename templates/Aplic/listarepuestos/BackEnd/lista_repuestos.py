from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from login import roles_required
from menu import cargar_menu
import json, os
from datetime import datetime
from templates.Aplic.estadosderepuestos.BackEnd.export_pdf import exportar_pdf_reportlab
from templates.Aplic.estadosderepuestos.BackEnd.estados_de_repuestos import cargar_tabs, cargar_almacenes, obtener_nombres_almacenes, cargar_estados, cargar_ubicaciones


lista_repuestos_bp = Blueprint('indexlista_repuestos', __name__)
PATHREPUESTOS = 'DataBase/dataRep/REPUESTOS.json'


def filtrar_repuestos(repuestos, filtros):
    resultado = []
    hoy = datetime.today().date()
    mostrar_vencidos = filtros.get('vencidos') == '1'

    for rep in repuestos:
        cumple = True

        # Check vencido según fecha_fin
        fecha_fin_str = rep.get('fecha_fin')
        esta_vencido = False
        if fecha_fin_str:
            try:
                fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
                if fecha_fin < hoy:
                    esta_vencido = True
            except ValueError:
                pass

        if mostrar_vencidos and not esta_vencido:
            continue  # Saltamos los no vencidos

        # Filtros
        if filtros.get('nombre') and filtros['nombre'].lower() not in rep.get('nombre', '').lower():
            cumple = False
        if filtros.get('codigo') and filtros['codigo'].lower() not in rep.get('codigo', '').lower():
            cumple = False
        if filtros.get('estado') and filtros['estado'] != rep.get('estado', ''):
            cumple = False
        if filtros.get('fecha_alta'):
            try:
                fecha_alta = datetime.strptime(filtros['fecha_alta'], '%Y-%m-%d')
                rep_fecha = datetime.strptime(rep.get('fecha_creacion', ''), '%Y-%m-%d')
                if rep_fecha.date() != fecha_alta.date():
                    cumple = False
            except:
                pass
        if filtros.get('fecha_baja'):
            try:
                fecha_baja = datetime.strptime(filtros['fecha_baja'], '%Y-%m-%d')
                rep_fecha = datetime.strptime(rep.get('fecha_fin', ''), '%Y-%m-%d')
                if rep_fecha.date() != fecha_baja.date():
                    cumple = False
            except:
                if rep.get('fecha_fin'):
                    cumple = False

        if cumple:
            resultado.append(rep)
    return resultado

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

    if not os.path.exists(PATHREPUESTOS):
        repuestos = []
    else:
        with open(PATHREPUESTOS, 'r', encoding='utf-8') as f:
            repuestos = json.load(f)

    hoy = datetime.today().date()
    cantidad_vencidos = 0
    for rep in repuestos:
        try:
            if rep.get('fecha_fin'):
                fecha_fin = datetime.strptime(rep['fecha_fin'], '%Y-%m-%d').date()
                if fecha_fin < hoy:
                    cantidad_vencidos += 1
        except:
            pass

    repuestos_filtrados = filtrar_repuestos(repuestos, filtros)

    # ✅ Si se solicita exportar a PDF
    if request.args.get('exportar_pdf') == '1':
        return exportar_pdf_reportlab(repuestos_filtrados)

    return render_template(
        'Aplic/listarepuestos/FrontEnd/lista_repuestos.html',
        nemu=nemu,
        roles=current_user.roles,
        repuestos=repuestos_filtrados,
        filtros=filtros,
        cantidad_vencidos=cantidad_vencidos,
        tabs = tabs,
        nombres_almacenes =nombres_almacenes,
        estados=estados,
        ubicaciones = ubicaciones
    )
