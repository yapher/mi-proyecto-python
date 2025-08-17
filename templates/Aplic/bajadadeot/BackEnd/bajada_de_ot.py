from flask_login import login_required, current_user
from menu import cargar_menu
from login import roles_required
from flask import Blueprint, render_template, flash, redirect, url_for
import json, os
from bs4 import BeautifulSoup
from datetime import datetime

bajada_de_ot_bp = Blueprint('bajada_de_ot', __name__)

AGENDA_PATH = "DataBase/time/agenda.json"

@bajada_de_ot_bp.route('/bajada_de_ot', methods=['GET'])
@login_required
@roles_required('viewer')
def mostrar_bajada_ot():
    nemu = cargar_menu()
    return render_template('Aplic/bajadadeot/FrontEnd/bajada_de_ot.html', nemu=nemu, roles=current_user.roles)

@bajada_de_ot_bp.route('/generar_json_ot', methods=['POST'])
@login_required
@roles_required('viewer')
def generar_json_ot():
    nemu = cargar_menu()
    try:
        ruta_bajada = "static/modelos/bajada.txt"
        if not os.path.exists(ruta_bajada):
            flash("El archivo bajada.txt no existe en static/modelos/", "danger")
            return render_template('Aplic/bajadadeot/FrontEnd/bajada_de_ot.html', nemu=nemu, roles=current_user.roles)

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

        # Guardar archivo JSON de órdenes
        fecha_actual = datetime.today().strftime("%Y_%m_%d")
        output_path = f"DataBase/dataOT/ordenes_{fecha_actual}.JSON"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(ordenes, f, indent=4, ensure_ascii=False)

        # ===== Agregar a agenda.json =====
        if os.path.exists(AGENDA_PATH):
            with open(AGENDA_PATH, "r", encoding="utf-8") as f:
                agenda = json.load(f)
        else:
            agenda = []

        # Obtener último ID
        last_id = max((e.get("id", 0) for e in agenda), default=0)

        # Guardar títulos ya existentes para evitar duplicados exactos
        ordenes_existentes = {e.get("titulo") for e in agenda}

        nuevos_eventos = 0
        for orden in ordenes:
            if orden["numero_orden"] in ordenes_existentes:
                continue  # Ya existe exactamente este número de orden
            ordenes_existentes.add(orden["numero_orden"])

            try:
                fecha_obj = datetime.strptime(orden["fin_extremo"], "%d/%m/%Y")
                fecha_str = fecha_obj.strftime("%Y-%m-%d")
            except Exception:
                fecha_str = datetime.today().strftime("%Y-%m-%d")

            last_id += 1
            evento = {
                "id": last_id,
                "titulo": orden["numero_orden"],
                "fecha": fecha_str,
                "descripcion": orden["descripcion"],
                "email": "c.oherasimov@ternium.com.ar",
                "realizado": False
            }
            agenda.append(evento)
            nuevos_eventos += 1

        # Guardar agenda.json actualizado
        os.makedirs(os.path.dirname(AGENDA_PATH), exist_ok=True)
        with open(AGENDA_PATH, "w", encoding="utf-8") as f:
            json.dump(agenda, f, indent=4, ensure_ascii=False)

        flash(f"Archivo generado correctamente y {nuevos_eventos} nuevos eventos agregados a agenda.json", "success")

    except Exception as e:
        flash(f"Error al generar el archivo: {str(e)}", "danger")

    #return render_template('Aplic/bajadadeot/FrontEnd/bajada_de_ot.html', nemu=nemu, roles=current_user.roles)
# Redirección final a la lista de OT (GET), evitando re-envío del formulario
    return redirect("/listar_ot", code=303)