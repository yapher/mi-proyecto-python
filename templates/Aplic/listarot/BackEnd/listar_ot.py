# Archivo backend generado automáticamente

from flask_login import login_required, current_user
from menu import cargar_menu
from login import roles_required
from flask import Blueprint, request, render_template, send_file
import json, re, os
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io

listar_ot_bp = Blueprint('indexlistar_ot', __name__)

# Ruta donde se guardan los archivos JSON
CARPETA_JSON = os.path.join("DataBase", "dataOT")

def obtener_archivos_json():
    archivos = []
    patron = re.compile(r"ordenes_(\d{4})_(\d{2})_(\d{2})\.JSON")
    if not os.path.exists(CARPETA_JSON):
        return archivos  # Si no existe la carpeta, lista vacía
    for archivo in os.listdir(CARPETA_JSON):
        match = patron.match(archivo)
        if match:
            fecha = datetime.strptime(f"{match.group(1)}-{match.group(2)}-{match.group(3)}", "%Y-%m-%d")
            archivos.append((fecha, archivo))
    archivos.sort(reverse=True)  # Más reciente primero
    return archivos

@listar_ot_bp.route('/listar_ot', methods=["GET"])
@login_required
@roles_required('viewer')
def indexlistar_ot():
    nemu = cargar_menu()
    archivos = obtener_archivos_json()
    if not archivos:
        return "No se encontraron archivos JSON válidos."

    archivo_seleccionado = request.args.get("archivo")
    if not archivo_seleccionado:
        archivo_seleccionado = archivos[0][1]  # El más reciente

    # Ruta completa del archivo
    ruta_archivo = os.path.join(CARPETA_JSON, archivo_seleccionado)

    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return f"No se encontró el archivo {ruta_archivo}"

    df = pd.DataFrame(data)
    df_unique = df.drop_duplicates(subset='numero_orden')

    # 🔹 Reemplazar campos vacíos por "sin valor"
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

# 🔹 Ruta para mostrar modal con órdenes
@listar_ot_bp.route('/filtro_torta/<columna>/<grupo>')
@login_required
@roles_required('viewer')
def filtro_torta(columna, grupo):
    archivo_seleccionado = request.args.get("archivo")
    if not archivo_seleccionado:
        archivos = obtener_archivos_json()
        if not archivos:
            return "No se encontraron archivos JSON válidos."
        archivo_seleccionado = archivos[0][1]

    ruta_archivo = os.path.join(CARPETA_JSON, archivo_seleccionado)
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return f"No se encontró el archivo {ruta_archivo}"

    df = pd.DataFrame(data)
    df_unique = df.drop_duplicates(subset="numero_orden")

    # 🔹 Reemplazar campos vacíos por "sin valor"
    df_unique = df_unique.fillna("sin revisión")
    df_unique = df_unique.replace("", "sin revisión")

    # 🔹 Filtrar según columna, si no hay coincidencias, devolvemos lista vacía
    if columna.lower() == "numero_orden":
        df_unique["numero_orden_prefix"] = df_unique["numero_orden"].astype(str).str[:4]
        ordenes = df_unique[df_unique["numero_orden_prefix"] == grupo].to_dict(orient="records")
    else:
        ordenes = df_unique[df_unique[columna].astype(str) == grupo].to_dict(orient="records")

    # 🔹 Asegurar que siempre sea lista, incluso vacía
    if not ordenes:
        ordenes = []

    return render_template(
        "Aplic/listarot/FrontEnd/filtroTorta.html",
        grupo=grupo,
        columna=columna,
        ordenes=ordenes,
        archivo=archivo_seleccionado
    )

# 🔹 Nueva ruta para exportar a PDF
@listar_ot_bp.route('/exportar_pdf/<columna>/<grupo>')
@login_required
@roles_required('viewer')
def exportar_pdf(columna, grupo):
    archivo_seleccionado = request.args.get("archivo")
    if not archivo_seleccionado:
        archivos = obtener_archivos_json()
        if not archivos:
            return "No se encontraron archivos JSON válidos."
        archivo_seleccionado = archivos[0][1]

    ruta_archivo = os.path.join(CARPETA_JSON, archivo_seleccionado)
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df_unique = df.drop_duplicates(subset="numero_orden")

    # 🔹 Reemplazar campos vacíos por "sin valor"
    df_unique = df_unique.fillna("sin revisión")
    df_unique = df_unique.replace("", "sin revisión")

    if columna.lower() == "numero_orden":
        df_unique["numero_orden_prefix"] = df_unique["numero_orden"].astype(str).str[:4]
        ordenes = df_unique[df_unique["numero_orden_prefix"] == grupo]
    else:
        ordenes = df_unique[df_unique[columna].astype(str) == grupo]

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), leftMargin=15, rightMargin=15, topMargin=20, bottomMargin=20)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Órdenes del grupo '{grupo}' (columna: {columna})", styles["Title"]))
    elements.append(Spacer(1, 12))

    if not ordenes.empty:
        # 🔹 Estilo para celdas con ajuste de texto
        cell_style = ParagraphStyle(
            name="CellStyle",
            fontSize=7,
            leading=9,
            alignment=1,  # 0=izq,1=center,2=der
            wordWrap='CJK'
        )

        # 🔹 Convertir todos los valores de la tabla en Paragraphs
        data_table = [[Paragraph(str(col), cell_style) for col in ordenes.columns]] + [
            [Paragraph(str(value), cell_style) for value in row]
            for row in ordenes.astype(str).values.tolist()
        ]

        # 🔹 Ajustar ancho proporcional al ancho de página
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

        # 🔹 Pie con cantidad de filas + fecha y hora
        elements.append(Spacer(1, 15))
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elementos_footer = f"Cantidad de filas: {len(ordenes)} | Generado el: {fecha_hora}"
        elements.append(Paragraph(elementos_footer, styles["Normal"]))

    else:
        elements.append(Paragraph("No hay órdenes en este grupo.", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name=f"ordenes_{grupo}.pdf", mimetype="application/pdf")
