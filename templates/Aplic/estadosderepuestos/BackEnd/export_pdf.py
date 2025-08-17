import os
from io import BytesIO
from datetime import datetime
from flask import make_response, current_app
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from PIL import Image as PILImage, UnidentifiedImageError

UPLOAD_FOLDER = 'static/uploads/Imagenes'

def imagen_valida(ruta):
    try:
        with PILImage.open(ruta) as im:
            im.verify()
        return True
    except (UnidentifiedImageError, OSError):
        return False

def exportar_pdf_reportlab(repuestos):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter),
                            leftMargin=40, rightMargin=40, topMargin=60, bottomMargin=40)

    styles = getSampleStyleSheet()

    if 'CustomTitle' not in styles:
        styles.add(ParagraphStyle(
            name='CustomTitle',
            fontName='Helvetica-Bold',
            fontSize=24,
            leading=28,
            alignment=1,
            spaceAfter=12,
            textColor=colors.HexColor('#003366')
        ))
    if 'CustomDate' not in styles:
        styles.add(ParagraphStyle(
            name='CustomDate',
            fontName='Helvetica-Oblique',
            fontSize=12,
            leading=14,
            alignment=1,
            spaceAfter=20,
            textColor=colors.HexColor('#666666')
        ))
    if 'CustomTotal' not in styles:
        styles.add(ParagraphStyle(
            name='CustomTotal',
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=14,
            alignment=2,
            textColor=colors.HexColor('#000000'),
            spaceBefore=20
        ))

    titulo = Paragraph("Informe de Estado de Repuestos", styles['CustomTitle'])
    fecha_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    fecha = Paragraph(f"Fecha de generación: {fecha_str}", styles['CustomDate'])

    data = [[
        Paragraph("<u>Imagen</u>", styles['Heading4']),
        Paragraph("<u>Nombre</u>", styles['Heading4']),
        Paragraph("<u>Código</u>", styles['Heading4']),
        Paragraph("<u>Cantidad</u>", styles['Heading4']),
        Paragraph("<u>Almacén</u>", styles['Heading4']),
        Paragraph("<u>Ubicación Técnica</u>", styles['Heading4'])
    ]]

    for r in repuestos:
        ubicacion = r.get("ruta_jerarquia", [])
        if isinstance(ubicacion, list):
            ubicacion = ", ".join(ubicacion)

        img_rel_path = r.get("imagen", None)
        if img_rel_path:
            img_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, os.path.basename(img_rel_path))
            if os.path.exists(img_path) and imagen_valida(img_path):
                try:
                    img = RLImage(img_path)
                    fixed_width = 1 * inch
                    fixed_height = 1 * inch
                    aspect = img.imageWidth / float(img.imageHeight)
                    if aspect > 1:
                        img.drawWidth = fixed_width
                        img.drawHeight = fixed_width / aspect
                    else:
                        img.drawHeight = fixed_height
                        img.drawWidth = fixed_height * aspect
                except Exception:
                    img = Paragraph("Sin imagen", styles['Normal'])
            else:
                img = Paragraph("Sin imagen", styles['Normal'])
        else:
            img = Paragraph("Sin imagen", styles['Normal'])

        data.append([
            img,
            Paragraph(str(r.get("nombre", "")), styles['Normal']),
            Paragraph(str(r.get("codigo", "")), styles['Normal']),
            Paragraph(str(r.get("cantidad", "")), styles['Normal']),
            Paragraph(str(r.get("equipo", "")), styles['Normal']),
            Paragraph(ubicacion, styles['Normal']),
        ])

    table = Table(data, repeatRows=1, hAlign='CENTER')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#333333')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (1, 0), (-1, -1), [colors.whitesmoke, colors.lightgrey])
    ]))

    cantidad_items = len(repuestos)
    total_text = Paragraph(f"Cantidad de ítems listados: <b>{cantidad_items}</b>", styles['CustomTotal'])

    elements = [titulo, fecha, table, total_text]
    doc.build(elements)
    buffer.seek(0)

    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=repuestos.pdf'
    return response
