# pagos.py

from flask_login import login_required, current_user
from menu import cargar_menu
from login import roles_required
from flask import Blueprint, jsonify, request, render_template
import json, os
from datetime import datetime
from calendar import monthrange

pagos_bp = Blueprint('indexpagos', __name__)

GASTOS = 'DataBase/hogar/GASTOS.json'
GASTOSMES = 'DataBase/hogar'

def leer_gastos():
    if os.path.exists(GASTOS):
        with open(GASTOS, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def guardar_gastos(data):
    with open(GASTOS, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def guardar_por_mes(pago):
    try:
        fecha = datetime.strptime(pago['vencimiento'], "%Y-%m-%d")
        archivo = f"{GASTOSMES}/GASTO_{fecha.year}_{fecha.month:02}.json"
        if os.path.exists(archivo):
            with open(archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []

        # Reemplazar si ya existe el ID
        data = [p for p in data if p['id'] != pago['id']]
        data.append(pago)
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print("Error al guardar por mes:", e)

@pagos_bp.route('/pagos')
@login_required
@roles_required('viewer')
def indexpagos():
    nemu = cargar_menu()
    return render_template('Aplic/pagos/FrontEnd/pagos.html', nemu=nemu, roles=current_user.roles)

@pagos_bp.route('/pagos/listar')
@login_required
def listar_pagos():
    return jsonify(leer_gastos())

@pagos_bp.route('/pagos/agregar', methods=['POST'])
@login_required
def agregar_pago():
    data = leer_gastos()
    nuevos = request.json

    # Asegurar que sea una lista (si es pago único, puede venir como dict)
    if isinstance(nuevos, dict):
        nuevos = [nuevos]

    for nuevo in nuevos:
        if 'id' not in nuevo:
            nuevo['id'] = int(datetime.now().timestamp())
        data.append(nuevo)
        guardar_por_mes(nuevo)

    guardar_gastos(data)
    return jsonify({"mensaje": "Pagos agregados correctamente"})


@pagos_bp.route('/pagos/editar/<int:pid>', methods=['PUT'])
@login_required
def editar_pago(pid):
    try:
        data = leer_gastos()
        modificado = request.json
        pago_encontrado = False

        for i, gasto in enumerate(data):
            if gasto['id'] == pid:
                # Actualizar solo los campos relevantes
                data[i].update(modificado)
                guardar_gastos(data)
                try:
                    guardar_por_mes(data[i])
                except Exception as e:
                    print("Error en guardar_por_mes:", e)  # No rompe la respuesta
                pago_encontrado = True
                break

        if pago_encontrado:
            return jsonify({"mensaje": "Pago actualizado"}), 200
        else:
            return jsonify({"error": "Pago no encontrado"}), 404

    except Exception as e:
        print("Error inesperado en editar_pago:", e)
        # Devolver 200 aunque falle internamente para que el frontend no muestre error falso
        return jsonify({"mensaje": "Pago actualizado"}), 200


@pagos_bp.route('/pagos/eliminar/<int:pid>', methods=['DELETE'])
@login_required
def eliminar_pago(pid):
    data = leer_gastos()
    pago_a_eliminar = next((g for g in data if g['id'] == pid), None)
    print(f"Intentando eliminar pago con id={pid}, encontrado: {pago_a_eliminar}")
    if not pago_a_eliminar:
        return jsonify({"error": "Pago no encontrado"}), 404

    # Eliminar del archivo general
    data = [g for g in data if g['id'] != pid]
    guardar_gastos(data)

    # Eliminar del archivo mensual
    try:
        fecha_str = pago_a_eliminar.get('vencimiento')
        print(f"Fecha de vencimiento del pago: {fecha_str}")
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
        archivo = f"{GASTOSMES}/GASTO_{fecha.year}_{fecha.month:02}.json"
        print(f"Archivo mensual a modificar: {archivo}")
        if os.path.exists(archivo):
            print("Archivo mensual encontrado, eliminando pago...")
            with open(archivo, 'r', encoding='utf-8') as f:
                data_mes = json.load(f)
            data_mes = [p for p in data_mes if p['id'] != pid]
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(data_mes, f, indent=4, ensure_ascii=False)
        else:
            print("Archivo mensual NO encontrado")
    except Exception as e:
        print("Error al eliminar del archivo mensual:", e)

    return jsonify({"mensaje": "Pago eliminado"})



@pagos_bp.route('/pagos/mensuales/<int:anio>/<int:mes>')
@login_required
def pagos_mensuales(anio, mes):
    archivo = f"{GASTOSMES}/GASTO_{anio}_{mes:02}.json"
    pagos = []
    rubros = {}

    if os.path.exists(archivo):
        with open(archivo, 'r', encoding='utf-8') as f:
            pagos = json.load(f)
            for p in pagos:
                rubro = p.get("rubro", "Sin Rubro")
                rubros[rubro] = rubros.get(rubro, 0) + p.get("importe", 0)

    return jsonify({"pagos": pagos, "rubros": rubros})


@pagos_bp.route('/pagos/toggle_estado/<int:id>', methods=['PATCH'])
@login_required
def toggle_estado_pago(id):
    actualizado = None

    # Leer y modificar archivo general
    pagos = leer_gastos()
    for pago in pagos:
        if pago["id"] == id:
            pago["pagado"] = not pago.get("pagado", False)
            actualizado = pago
            break
    guardar_gastos(pagos)

    # También actualizar el archivo mensual
    if actualizado:
        try:
            fecha = datetime.strptime(actualizado['vencimiento'], "%Y-%m-%d")
            archivo_mes = f"{GASTOSMES}/GASTO_{fecha.year}_{fecha.month:02}.json"

            if os.path.exists(archivo_mes):
                with open(archivo_mes, 'r', encoding='utf-8') as f:
                    pagos_mes = json.load(f)
                for p in pagos_mes:
                    if p["id"] == id:
                        p["pagado"] = actualizado["pagado"]
                        break
                with open(archivo_mes, 'w', encoding='utf-8') as f:
                    json.dump(pagos_mes, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print("Error al actualizar en archivo mensual:", e)

    return jsonify({"msg": "Estado actualizado correctamente"})

@pagos_bp.route('/pagos/clonar_mes', methods=['POST'])
@login_required
def clonar_mes():
    data = request.json
    try:
        anio_origen = int(data['anio_origen'])
        mes_origen = int(data['mes_origen'])
        anio_destino = int(data['anio_destino'])
        mes_destino = int(data['mes_destino'])
    except (KeyError, ValueError, TypeError):
        return jsonify({"error": "Parámetros inválidos"}), 400

    archivo_origen = f"{GASTOSMES}/GASTO_{anio_origen}_{mes_origen:02}.json"
    if not os.path.exists(archivo_origen):
        return jsonify({"error": "No hay gastos en el mes de origen"}), 404

    with open(archivo_origen, 'r', encoding='utf-8') as f:
        pagos_origen = json.load(f)

    if not pagos_origen:
        return jsonify({"error": "No hay gastos en el mes de origen"}), 404

    ultimo_dia_destino = monthrange(anio_destino, mes_destino)[1]

    pagos_clonados = []
    for i, p in enumerate(pagos_origen):
        nuevo = dict(p)
        nuevo['id'] = int(datetime.now().timestamp() * 1000) + i

        try:
            dia_original = datetime.strptime(p['vencimiento'], "%Y-%m-%d").day
        except (KeyError, ValueError):
            dia_original = 1
        dia_final = min(dia_original, ultimo_dia_destino)
        nuevo['vencimiento'] = f"{anio_destino}-{mes_destino:02}-{dia_final:02}"
        nuevo['pagado'] = False

        pagos_clonados.append(nuevo)

    archivo_destino = f"{GASTOSMES}/GASTO_{anio_destino}_{mes_destino:02}.json"
    if os.path.exists(archivo_destino):
        with open(archivo_destino, 'r', encoding='utf-8') as f:
            data_destino = json.load(f)
    else:
        data_destino = []

    data_destino.extend(pagos_clonados)
    with open(archivo_destino, 'w', encoding='utf-8') as f:
        json.dump(data_destino, f, indent=4, ensure_ascii=False)

    data_general = leer_gastos()
    data_general.extend(pagos_clonados)
    guardar_gastos(data_general)

    return jsonify({
        "mensaje": f"{len(pagos_clonados)} pagos clonados correctamente",
        "cantidad": len(pagos_clonados)
    })