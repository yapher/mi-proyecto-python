from flask_login import login_required, current_user
from menu import cargar_menu
from login import roles_required
from flask import Blueprint, render_template
import json
from collections import defaultdict

inventario_bp = Blueprint('indexinventario', __name__)

DATA_FILE = 'DataBase/dataRep/almacenes.json'
DATA_REP = 'DataBase/dataRep/REPUESTOS.json'

def aplanar_jerarquia(data, ruta_padre=""):
    resultado = []
    for nodo in data:
        nombre = nodo["nombre"]
        ruta = f"{ruta_padre}/{nombre}" if ruta_padre else nombre
        hijos = nodo.get("subcrear_almacenes", [])
        resultado.append({
            "nombre": nombre,
            "ruta": ruta,
            "subcrear_almacenes": hijos
        })
        resultado.extend(aplanar_jerarquia(hijos, ruta))
    return resultado

def crear_diccionario_hijos(nodos):
    hijos_por_ruta = defaultdict(list)
    for nodo in nodos:
        ruta = nodo['ruta']
        if '/' in ruta:
            padre = ruta.rsplit('/', 1)[0]
        else:
            padre = ''
        hijos_por_ruta[padre].append(nodo)
    return hijos_por_ruta

@inventario_bp.route('/inventario')
@login_required
@roles_required('viewer')
def indexinventario():
    nemu = cargar_menu()

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        almacenes = json.load(f)

    with open(DATA_REP, 'r', encoding='utf-8') as f:
        repuestos = json.load(f)

    # Aquí no aplanamos, trabajamos con el árbol directamente
    # Creamos un diccionario para acceso rápido por nombre de equipo
    repuestos_por_equipo = {}
    for r in repuestos:
        equipo = r.get("equipo", "")
        repuestos_por_equipo.setdefault(equipo, []).append(r)

    return render_template(
        'Aplic/inventario/FrontEnd/inventario.html',
        nemu=nemu,
        roles=current_user.roles,
        almacenes=almacenes,
        repuestos_por_equipo=repuestos_por_equipo,
    )

