"""
Blueprint de Bajada de OT — VERSIÓN SQL
Genera órdenes de trabajo desde HTML y las guarda en SQL.
También actualiza la agenda (eventos) en SQL.
"""
from flask_login import login_required, current_user
from core.menu import cargar_menu
from auth.login import roles_required
from flask import Blueprint, render_template, flash, redirect, url_for
import os
from bs4 import BeautifulSoup
from datetime import datetime
from core.db_sql import db
from core.models import Evento, OrdenTrabajo

bajada_de_ot_bp = Blueprint('bajada_de_ot', __name__)


@bajada_de_ot_bp.route('/bajada_de_ot', methods=['GET'])
@login_required
@roles_required('viewer')
def mostrar_bajada_ot():
    nemu = cargar_menu()
    return render_template('Aplic/bajadadeot/FrontEnd/bajada_de_ot.html',
                          nemu=nemu, roles=current_user.roles)


@bajada_de_ot_bp.route('/generar_json_ot', methods=['POST'])
@login_required
@roles_required('viewer')
def generar_json_ot():
    nemu = cargar_menu()
    try:
        ruta_bajada = os.path.join('static', 'modelos', 'bajada.txt')
        if not os.path.exists(ruta_bajada):
            flash("El archivo bajada.txt no existe en static/modelos/", "danger")
            return render_template('Aplic/bajadadeot/FrontEnd/bajada_de_ot.html',
                                  nemu=nemu, roles=current_user.roles)

        with open(ruta_bajada, "r", encoding="utf-8") as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, "html.parser")
        rows = soup.find_all("tr")
        ordenes = []

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 9:
                continue
            orden = {
                "numero_orden": cols[1].get_text(strip=True),
                "descripcion": cols[2].get_text(strip=True),
                "inicio_extremo": cols[3].get_text(strip=True),
                "fin_extremo": cols[4].get_text(strip=True),
                "equipo_ut": cols[5].get_text(strip=True),
                "descripcion_equipo": cols[6].get_text(strip=True),
                "estado": cols[7].get_text(strip=True),
                "revision": cols[8].get_text(strip=True)
            }
            ordenes.append(orden)

        # ✅ GUARDAR EN SQL (tabla OrdenTrabajo)
        fecha_actual = datetime.today().strftime("%Y_%m_%d")
        archivo_origen = f"ordenes_{fecha_actual}.JSON"

        # Eliminar órdenes anteriores del mismo archivo (si existe)
        OrdenTrabajo.query.filter_by(archivo_origen=archivo_origen).delete()

        for orden in ordenes:
            ot = OrdenTrabajo(
                numero_orden=orden["numero_orden"],
                descripcion=orden["descripcion"],
                inicio_extremo=orden["inicio_extremo"],
                fin_extremo=orden["fin_extremo"],
                equipo_ut=orden["equipo_ut"],
                descripcion_equipo=orden["descripcion_equipo"],
                estado=orden["estado"],
                revision=orden["revision"],
                archivo_origen=archivo_origen
            )
            db.session.add(ot)

        # ✅ ACTUALIZAR AGENDA EN SQL (tabla Evento)
        nuevos_eventos = 0
        actualizaciones = 0

        for orden in ordenes:
            try:
                fecha_obj = datetime.strptime(orden["fin_extremo"], "%d/%m/%Y")
                fecha_str = fecha_obj.strftime("%Y-%m-%d")
            except Exception:
                fecha_str = datetime.today().strftime("%Y-%m-%d")

            # Buscar si ya existe este número de orden en la agenda
            existente = Evento.query.filter_by(titulo=orden["numero_orden"]).first()

            if existente:
                if existente.fecha != fecha_str:
                    existente.fecha = fecha_str
                    actualizaciones += 1
            else:
                evento = Evento(
                    titulo=orden["numero_orden"],
                    fecha=fecha_str,
                    descripcion=orden["descripcion"],
                    email="c.oherasimov@ternium.com.ar",
                    realizado=False
                )
                db.session.add(evento)
                nuevos_eventos += 1

        db.session.commit()
        flash(f"Archivo generado correctamente: {len(ordenes)} órdenes guardadas en SQL, "
              f"{nuevos_eventos} nuevos eventos y {actualizaciones} fechas actualizadas en agenda",
              "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error al generar el archivo: {str(e)}", "danger")

    return redirect("/listar_ot", code=303)