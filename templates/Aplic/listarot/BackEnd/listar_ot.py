# templates/Aplic/listarot/BackEnd/listar_ot.py
"""
Blueprint de Listar OT — VERSIÓN SQL
Lee las órdenes de trabajo desde la base de datos SQL (tabla OrdenTrabajo).
"""
from flask_login import login_required, current_user
from core.menu import cargar_menu
from auth.login import roles_required
from flask import Blueprint, request, render_template, send_file
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io
import os
from core.db_sql import db
from core.models import OrdenTrabajo

_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_STATIC_DIR = os.path.abspath(os.path.join(_APP_DIR, '..', 'static'))

listar_ot_bp = Blueprint(
    'indexlistar_ot',
    __name__,
    static_folder=_STATIC_DIR,
    static_url_path='/listarot/static'
)


def obtener_archivos_disponibles():
    """Retorna lista de (fecha, archivo_origen) únicos, ordenados."""
    archivos = db.session.query(OrdenTrabajo.archivo_origen).distinct().all()
    archivos = [a[0] for a in archivos if a[0]]
    archivos.sort(reverse=True)

    resultado = []
    for archivo in archivos:
        try:
            partes = archivo.replace('.JSON', '').replace('ordenes_', '').split('_')
            if len(partes) == 3:
                fecha = datetime.strptime(f"{partes[0]}-{partes[1]}-{partes[2]}", "%Y-%m-%d")
                resultado.append((fecha, archivo))
        except (ValueError, IndexError):
            pass

    resultado.sort(key=lambda x: x[0], reverse=True)
    return resultado


def obtener_dataframe(archivo_seleccionado=None):
    """Obtiene el DataFrame de órdenes de trabajo."""
    query = db.session.query(OrdenTrabajo)
    if archivo_seleccionado:
        query = query.filter(OrdenTrabajo.archivo_origen == archivo_seleccionado)
    ordenes = query.all()

    if not ordenes:
        return pd.DataFrame()

    datos = [ot.to_dict() for ot in ordenes]
    df = pd.DataFrame(datos)

    # Eliminar columnas internas
    cols_eliminar = ['id', 'archivo_origen', 'fecha_creacion']
    df = df.drop(columns=[c for c in cols_eliminar if c in df.columns], errors='ignore')

    return df


@listar_ot_bp.route('/listar_ot')
@login_required
@roles_required('viewer')
def indexlistar_ot():
    nemu = cargar_menu()
    archivos = obtener_archivos_disponibles()

    if not archivos:
        return render_template(
            'Aplic/listarot/FrontEnd/listar_ot.html',
            nemu=nemu,
            roles=current_user.roles,
            tables='',
            num_filas=0,
            selector=[],
            archivo_actual=None
        )

    archivo_seleccionado = request.args.get('archivo', archivos[0][1])
    df = obtener_dataframe(archivo_seleccionado)

    if df.empty:
        return render_template(
            'Aplic/listarot/FrontEnd/listar_ot.html',
            nemu=nemu,
            roles=current_user.roles,
            tables='',
            num_filas=0,
            selector=[(a[1], a[0].strftime("%Y-%m-%d")) for a in archivos],
            archivo_actual=archivo_seleccionado
        )

    df_unique = df.drop_duplicates()
    df_unique = df_unique.fillna("sin revisión")
    df_unique = df_unique.replace("", "sin revisión")
    num_filas = len(df_unique)

    html_table = df_unique.to_html(
        classes="table table-bordered table-hover table-striped table-dark align-middle w-100 mb-0",
        index=False,
        escape=False
    ).replace('', '')

    selector = [(archivo[1], archivo[0].strftime("%Y-%m-%d")) for archivo in archivos]

    return render_template(
        'Aplic/listarot/FrontEnd/listar_ot.html',
        nemu=nemu,
        roles=current_user.roles,
        tables=html_table,
        num_filas=num_filas,
        selector=selector,
        archivo_actual=archivo_seleccionado
    )


@listar_ot_bp.route('/filtro_torta/<columna>/<grupo>')
@login_required
@roles_required('viewer')
def filtro_torta(columna, grupo):
    archivo_seleccionado = request.args.get("archivo")
    if not archivo_seleccionado:
        archivos = obtener_archivos_disponibles()
        archivo_seleccionado = archivos[0][1] if archivos else None

    df = obtener_dataframe(archivo_seleccionado)
    if df.empty:
        return render_template(
            "Aplic/listarot/FrontEnd/filtroTorta.html",
            grupo=grupo, columna=columna, ordenes=[], archivo=archivo_seleccionado
        )

    df_unique = df.drop_duplicates()
    df_unique = df_unique.fillna("sin revisión")
    df_unique = df_unique.replace("", "sin revisión")

    if columna.lower() == "numero_orden":
        df_unique["numero_orden_prefix"] = df_unique["numero_orden"].astype(str).str[:4]
        ordenes = df_unique[df_unique["numero_orden_prefix"] == grupo].to_dict(orient="records")
    else:
        ordenes = df_unique[df_unique[columna].astype(str) == grupo].to_dict(orient="records")

    if not ordenes:
        ordenes = []

    return render_template(
        "Aplic/listarot/FrontEnd/filtroTorta.html",
        grupo=grupo, columna=columna, ordenes=ordenes, archivo=archivo_seleccionado
    )


@listar_ot_bp.route('/exportar_pdf/<columna>/<grupo>')
@login_required
@roles_required('viewer')
def exportar_pdf(columna, grupo):
    archivo_seleccionado = request.args.get("archivo")
    if not archivo_seleccionado:
        archivos = obtener_archivos_disponibles()
        archivo_seleccionado = archivos[0][1] if archivos else None

    df = obtener_dataframe(archivo_seleccionado)
    if df.empty:
        ordenes = []
    else:
        df_unique = df.drop_duplicates()
        df_unique = df_unique.fillna("sin revisión")
        df_unique = df_unique.replace("", "sin revisión")

        if columna.lower() == "numero_orden":
            df_unique["numero_orden_prefix"] = df_unique["numero_orden"].astype(str).str[:4]
            ordenes = df_unique[df_unique["numero_orden_prefix"] == grupo].to_dict(orient="records")
        else:
            ordenes = df_unique[df_unique[columna].astype(str) == grupo].to_dict(orient="records")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
                            leftMargin=20, rightMargin=20, topMargin=20, bottomMargin=20)
    styles = getSampleStyleSheet()
    elements = []

    titulo_style = ParagraphStyle('Titulo', parent=styles['Title'], fontSize=16, spaceAfter=12)
    elements.append(Paragraph(f"Órdenes de Trabajo — {grupo}", titulo_style))
    elements.append(Paragraph(f"Columna: {columna}", styles['Normal']))
    elements.append(Spacer(1, 10))

    if ordenes:
        headers = list(ordenes[0].keys())
        data = [headers] + [[str(o.get(h, '')) for h in headers] for o in ordenes]

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#370d60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
        ]))
        elements.append(table)
        elements.append(Spacer(1, 15))

        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elementos_footer = f"Cantidad de filas: {len(ordenes)} | Generado el: {fecha_hora}"
        elements.append(Paragraph(elementos_footer, styles["Normal"]))
    else:
        elements.append(Paragraph("No hay órdenes en este grupo.", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True,
                     download_name=f"ordenes_{grupo}.pdf", mimetype="application/pdf")