from flask import Blueprint, render_template, request, redirect, url_for, current_app
from pathlib import Path
import json

crear_listado_bp = Blueprint('crear_listado', __name__, url_prefix='/crear-listado')

def get_paths():
    base_path = Path(current_app.root_path)  # Punto clave
    ubicacion_path = base_path / 'DataBase' / 'dataRep' / 'ubicacion_tecnica.json'
    tabs_path = base_path / 'DataBase' / 'tabs.json'
    return ubicacion_path, tabs_path

def obtener_rutas():
    ubicacion_path, _ = get_paths()
    rutas = []

    def extraer(data):
        for item in data:
            rutas.append({
                "ruta": item["ruta"],
                "ruta_jerarquia": item["ruta_jerarquia"]
            })
            if item.get("sububicaciones"):
                extraer(item["sububicaciones"])

    with open(ubicacion_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        extraer(data)

    return rutas

def guardar_tab(ruta, rutas_disponibles):
    _, tabs_path = get_paths()
    ruta_jerarquia = next((r['ruta_jerarquia'] for r in rutas_disponibles if r['ruta'] == ruta), '')

    nuevo_tab = {
        "id": ruta,
        "title": f"{ruta} 🏬",
        "ruta_jerarquia": ruta_jerarquia
    }

    with open(tabs_path, 'r', encoding='utf-8') as f:
        tabs = json.load(f)

    if not any(tab['id'] == ruta for tab in tabs):
        tabs.append(nuevo_tab)
        with open(tabs_path, 'w', encoding='utf-8') as f:
            json.dump(tabs, f, indent=4, ensure_ascii=False)

@crear_listado_bp.route('/', methods=['GET', 'POST'])
def crear_listado():
    rutas = obtener_rutas()

    if request.method == 'POST':
        ruta = request.form.get('ruta')
        guardar_tab(ruta, rutas)
        return redirect(url_for('crear_listado.crear_listado'))

    return render_template(
        'Aplic/crearlistadoderepuestoporlinea/FrontEnd/crear_listado_de_repuesto_por_linea.html',
        rutas=rutas
    )
