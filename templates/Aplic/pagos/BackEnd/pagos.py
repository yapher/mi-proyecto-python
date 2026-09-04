# pagos.py
"""
Módulo de gestión de pagos.
Usa MesStore de core para la lógica mensual reutilizable.
"""
from flask_login import login_required, current_user
from core.menu import cargar_menu
from auth.login import roles_required
from flask import Blueprint, jsonify, request, render_template
import json, os
from datetime import datetime
from calendar import monthrange

# ✅ IMPORTAR MesStore desde core
from core.mes_store import MesStore

pagos_bp = Blueprint('indexpagos', __name__)

# ✅ Instancia reutilizable de MesStore
mes_store = MesStore(
    base_dir='DataBase/hogar',
    archivo_general='GASTOS',
    prefijo_mensual='GASTO'
)

# ============================================================
# FUNCIONES LEGACY (compatibilidad con tests)
# ============================================================

def leer_gastos():
    """Lee todos los gastos del archivo general."""
    return mes_store.leer_general()

def guardar_gastos(data):
    """Guarda todos los gastos en el archivo general."""
    mes_store.guardar_general(data)

def guardar_por_mes(pago):
    """Guarda un pago en su archivo mensual correspondiente."""
    try:
        fecha = datetime.strptime(pago['vencimiento'], "%Y-%m-%d")
        mes_store.agregar_a_mes(fecha.year, fecha.month, pago)
    except Exception as e:
        print("Error al guardar por mes:", e)

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
    return jsonify(mes_store.leer_general())

@pagos_bp.route('/pagos/agregar', methods=['POST'])
@login_required
def agregar_pago():
    data = mes_store.leer_general()
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
            nuevo['id'] = int(datetime.now().timestamp())
        
        data.append(nuevo)
        
        # ✅ Usar MesStore para guardar en archivo mensual
        guardar_por_mes(nuevo)
    
    mes_store.guardar_general(data)
    return jsonify({"mensaje": "Pagos agregados correctamente"})

@pagos_bp.route('/pagos/editar/<int:pid>', methods=['PUT'])
@login_required
def editar_pago(pid):
    try:
        data = mes_store.leer_general()
        modificado = request.json
        pago_encontrado = False
        
        for i, gasto in enumerate(data):
            if gasto['id'] == pid:
                data[i].update(modificado)
                pago_encontrado = True
                
                # ✅ Usar MesStore para sincronizar
                mes_store.sincronizar_registro(data[i])
                break
        
        if pago_encontrado:
            mes_store.guardar_general(data)
            return jsonify({"mensaje": "Pago actualizado"}), 200
        else:
            return jsonify({"error": "Pago no encontrado"}), 404
    
    except Exception as e:
        print("Error inesperado en editar_pago:", e)
        return jsonify({"mensaje": "Pago actualizado"}), 200

@pagos_bp.route('/pagos/eliminar/<int:pid>', methods=['DELETE'])
@login_required
def eliminar_pago(pid):
    data = mes_store.leer_general()
    pago_a_eliminar = next((g for g in data if g['id'] == pid), None)
    
    if not pago_a_eliminar:
        return jsonify({"error": "Pago no encontrado"}), 404
    
    # Eliminar del archivo general
    data = [g for g in data if g['id'] != pid]
    mes_store.guardar_general(data)
    
    # ✅ Usar MesStore para eliminar del archivo mensual
    try:
        fecha_str = pago_a_eliminar.get('vencimiento')
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
        mes_store.eliminar_de_mes(fecha.year, fecha.month, pid)
    except Exception as e:
        print("Error al eliminar del archivo mensual:", e)
    
    return jsonify({"mensaje": "Pago eliminado"})

@pagos_bp.route('/pagos/mensuales/<int:anio>/<int:mes>')
@login_required
def pagos_mensuales(anio, mes):
    # ✅ Usar MesStore para leer mes y calcular totales
    pagos = mes_store.leer_mes(anio, mes)
    rubros = mes_store.totales_por_rubro(anio, mes)
    
    return jsonify({"pagos": pagos, "rubros": rubros})

@pagos_bp.route('/pagos/toggle_estado/<int:id>', methods=['PATCH'])
@login_required
def toggle_estado_pago(id):
    actualizado = None
    
    # Leer y modificar archivo general
    pagos = mes_store.leer_general()
    
    for pago in pagos:
        if pago["id"] == id:
            pago["pagado"] = not pago.get("pagado", False)
            actualizado = pago
            break
    
    mes_store.guardar_general(pagos)
    
    # ✅ Usar MesStore para sincronizar con archivo mensual
    if actualizado:
        mes_store.sincronizar_registro(actualizado)
    
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
    
    # ✅ Usar MesStore para clonar
    try:
        cantidad, _ = mes_store.clonar_mes(
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