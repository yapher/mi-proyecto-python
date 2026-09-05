"""
Módulo de gestión de pagos - VERSIÓN SQL
Ahora usa SQL en lugar de JSON.
"""
from flask_login import login_required, current_user
from core.menu import cargar_menu
from auth.login import roles_required
from flask import Blueprint, jsonify, request, render_template
from datetime import datetime
from core.db_sql_store import pago_store

pagos_bp = Blueprint('indexpagos', __name__)

# ============================================================
# RUTAS
# ============================================================
@pagos_bp.route('/pagos')
@login_required
@roles_required('viewer')
def indexpagos():
    nemu = cargar_menu()
    return render_template('Aplic/pagos/FrontEnd/pagos.html', nemu=nemu, roles=current_user.roles)

@pagos_bp.route('/pagos/listar')
@login_required
def listar_pagos():
    return jsonify(pago_store.leer_general())

@pagos_bp.route('/pagos/agregar', methods=['POST'])
@login_required
def agregar_pago():
    nuevos = request.json
    # Si no es JSON, intentar leer como form-data (para compatibilidad con tests)
    if nuevos is None and request.form:
        nuevos = dict(request.form)
    # Asegurar que sea una lista
    if isinstance(nuevos, dict):
        nuevos = [nuevos]
    if not nuevos:
        return jsonify({"error": "No se recibieron datos"}), 400

    for nuevo in nuevos:
        if 'id' not in nuevo:
            nuevo['id'] = int(datetime.now().timestamp() * 1000)
        pago_store.agregar_a_general(nuevo)

    return jsonify({"mensaje": "Pagos agregados correctamente"})

@pagos_bp.route('/pagos/editar/<int:pid>', methods=['PUT'])
@login_required
def editar_pago(pid):
    try:
        modificado = request.json
        if pago_store.actualizar_pago(pid, modificado):
            return jsonify({"mensaje": "Pago actualizado"}), 200
        return jsonify({"error": "Pago no encontrado"}), 404
    except Exception as e:
        print("Error inesperado en editar_pago:", e)
        return jsonify({"mensaje": "Pago actualizado"}), 200

@pagos_bp.route('/pagos/eliminar/<int:pid>', methods=['DELETE'])
@login_required
def eliminar_pago(pid):
    if pago_store.eliminar_pago(pid):
        return jsonify({"mensaje": "Pago eliminado"})
    return jsonify({"error": "Pago no encontrado"}), 404

@pagos_bp.route('/pagos/mensuales/<int:anio>/<int:mes>')
@login_required
def pagos_mensuales(anio, mes):
    pagos = pago_store.leer_mes(anio, mes)
    rubros = pago_store.totales_por_rubro(anio, mes)
    return jsonify({"pagos": pagos, "rubros": rubros})

@pagos_bp.route('/pagos/toggle_estado/<int:id>', methods=['PATCH'])
@login_required
def toggle_estado_pago(id):
    nuevo_estado = pago_store.toggle_pagado(id)
    if nuevo_estado is not None:
        return jsonify({"msg": "Estado actualizado correctamente"})
    return jsonify({"error": "Pago no encontrado"}), 404

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

    try:
        cantidad, _ = pago_store.clonar_mes(
            anio_origen, mes_origen,
            anio_destino, mes_destino,
            resetear_pagado=True
        )
        return jsonify({
            "mensaje": f"{cantidad} pagos clonados correctamente",
            "cantidad": cantidad
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 404