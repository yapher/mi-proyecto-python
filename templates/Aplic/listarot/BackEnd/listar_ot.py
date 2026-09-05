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
from core.db_sql import db
from core.models import OrdenTrabajo

listar_ot_bp = Blueprint('indexlistar_ot', __name__)


def obtener_archivos_disponibles():
    """Retorna lista de (fecha, archivo_origen) únicos, ordenados."""
    archivos = db.session.query(OrdenTrabajo.archivo_origen).distinct().all()
    archivos = [a[0] for a in archivos if a[0]]
    # Ordenar por fecha (los archivos tienen formato ordenes_YYYY_MM_DD.JSON)
    archivos.sort(reverse=True)
    # Extraer fecha del nombre del archivo
    resultado = []
    for archivo in archivos:
        try:
            # Extraer YYYY_MM_DD del nombre
            partes = archivo.replace('.JSON', '').replace('ordenes_', '').split('_')
            if len(partes) == 3:
                fecha = datetime.strptime(f"{partes[0]}-{partes[1]}-{partes[2]}", "%Y-%m-%d")
                resultado.append((fecha, archivo))
        except Exception:
            resultado.append((datetime.now(), archivo))
    resultado.sort(key=lambda x: x[0], reverse=True)
    return resultado


@listar_ot_bp.route('/listar_ot', methods=["GET"])
@login_required
@roles_required('viewer')
def indexlistar_ot():
    nemu = cargar_menu()
    archivos = obtener_archivos_disponibles()

    if not archivos:
        return "No se encontraron archivos de órdenes."

    archivo_seleccionado = request.args.get("archivo")
    if not archivo_seleccionado:
        archivo_seleccionado = archivos[0][1]

    # Leer desde SQL
    ordenes_db = OrdenTrabajo.query.filter_by(archivo_origen=archivo_seleccionado).all()
    data = [o.to_dict() for o in ordenes_db]

    if not data:
        return "No hay órdenes en este archivo."

    df = pd.DataFrame(data)
    df_unique = df.drop_duplicates(subset='numero_orden')
    df_unique = df_unique.fillna("sin revisión")
    df_unique = df_unique.replace("", "sin revisión")

    num_filas = len(df_unique)
    html_table = df_unique.to_html(
        classes="table table-bordered table-hover table-striped table-dark align-middle w-100 mb-0",
        index=False,
        escape=False
    ).replace('\n', '')

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
        if not archivos:
            return "No se encontraron archivos."
        archivo_seleccionado = archivos[0][1]

    # Leer desde SQL
    ordenes_db = OrdenTrabajo.query.filter_by(archivo_origen=archivo_seleccionado).all()
    data = [o.to_dict() for o in ordenes_db]

    df = pd.DataFrame(data)
    df_unique = df.drop_duplicates(subset="numero_orden")
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
        grupo=grupo, columna=columna, ordenes=ordenes,
        archivo=archivo_seleccionado
    )


@listar_ot_bp.route('/exportar_pdf/<columna>/<grupo>')
@login_required
@roles_required('viewer')
def exportar_pdf(columna, grupo):
    archivo_seleccionado = request.args.get("archivo")
    if not archivo_seleccionado:
        archivos = obtener_archivos_disponibles()
        if not archivos:
            return "No se encontraron archivos."
        archivo_seleccionado = archivos[0][1]

    # Leer desde SQL
    ordenes_db = OrdenTrabajo.query.filter_by(archivo_origen=archivo_seleccionado).all()
    data = [o.to_dict() for o in ordenes_db]

    df = pd.DataFrame(data)
    df_unique = df.drop_duplicates(subset="numero_orden")
    df_unique = df_unique.fillna("sin revisión")
    df_unique = df_unique.replace("", "sin revisión")

    if columna.lower() == "numero_orden":
        df_unique["numero_orden_prefix"] = df_unique["numero_orden"].astype(str).str[:4]
        ordenes = df_unique[df_unique["numero_orden_prefix"] == grupo]
    else:
        ordenes = df_unique[df_unique[columna].astype(str) == grupo]

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
                            leftMargin=15, rightMargin=15, topMargin=20, bottomMargin=20)
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Órdenes del grupo '{grupo}' (columna: {columna})", styles["Title"]))
    elements.append(Spacer(1, 12))

    if not ordenes.empty:
        cell_style = ParagraphStyle(
            name="CellStyle", fontSize=7, leading=9,
            alignment=1, wordWrap='CJK'
        )
        data_table = [[Paragraph(str(col), cell_style) for col in ordenes.columns]] + [
            [Paragraph(str(value), cell_style) for value in row]
            for row in ordenes.astype(str).values.tolist()
        ]
        col_widths = [doc.width / len(ordenes.columns)] * len(ordenes.columns)
        table = Table(data_table, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
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