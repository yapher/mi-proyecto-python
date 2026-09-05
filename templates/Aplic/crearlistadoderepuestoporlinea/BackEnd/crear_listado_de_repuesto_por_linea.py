"""
Blueprint de Crear Listado de Repuesto por Línea — VERSIÓN SQL
Lee ubicaciones y tabs desde SQL, y crea nuevos tabs en SQL.
"""
from flask import Blueprint, render_template, request, redirect, url_for
from core.db_sql_store import ubicacion_store, tab_store

crear_listado_bp = Blueprint('crear_listado', __name__, url_prefix='/crear-listado')


def obtener_rutas():
    """Obtiene todas las rutas de ubicaciones técnicas desde SQL."""
    arbol = ubicacion_store.cargar_arbol()
    rutas = []

    def extraer(items):
        for item in items:
            rutas.append({
                "ruta": item.get("ruta", ""),
                "ruta_jerarquia": item.get("ruta_jerarquia", "")
            })
            if item.get("sububicaciones"):
                extraer(item["sububicaciones"])

    extraer(arbol)
    return rutas


def guardar_tab(ruta, rutas_disponibles):
    """Guarda un nuevo tab en SQL si no existe."""
    # Buscar la ruta_jerarquia correspondiente
    ruta_jerarquia = next((r['ruta_jerarquia'] for r in rutas_disponibles if r['ruta'] == ruta), '')

    # Verificar si ya existe
    tabs_existentes = tab_store.cargar()
    if any(tab['id'] == ruta for tab in tabs_existentes):
        return  # Ya existe, no duplicar

    # Crear nuevo tab usando el store SQL
    tab_store.agregar({
        'tab_id': ruta,
        'title': f"{ruta} 🏬",
        'ruta_jerarquia': ruta_jerarquia,
        'sanitized_id': ruta.replace(' ', '-').replace('/', '-')
    })


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