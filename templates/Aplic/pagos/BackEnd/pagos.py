"""
Blueprint de Pagos - VERSIÓN SQL
Rutas coinciden con el JS original (pagos.js, newPagos.js, etc.)
"""
from flask_login import login_required, current_user
from core.menu import cargar_menu
from auth.login import roles_required
from flask import Blueprint, render_template, jsonify, request
from core.db_sql import db
from core.db_sql_store import pago_store, rubro_store
from core.logging_config import get_logger
from datetime import datetime
import os

logger = get_logger(__name__)

_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_STATIC_DIR = os.path.abspath(os.path.join(_APP_DIR, '..', 'static'))

pagos_bp = Blueprint(
    'indexpagos',
    __name__,
    static_folder=_STATIC_DIR,
    static_url_path='/pagos/static'
)


# ============================================================
# RUTAS HTML
# ============================================================

@pagos_bp.route('/pagos')
@login_required
@roles_required('viewer')
def indexpagos():
    nemu = cargar_menu()
    return render_template(
        'Aplic/pagos/FrontEnd/pagos.html',
        nemu=nemu,
        roles=current_user.roles
    )


# ============================================================
# RUTAS API
# ============================================================

@pagos_bp.route('/pagos/listar')
@login_required
def listar_pagos():
    """Devuelve todos los pagos."""
    return jsonify(pago_store.leer_general())


def _validar_pago(p):
    """Valida y normaliza un pago. Lanza ValueError con un mensaje claro."""
    if not isinstance(p, dict):
        raise ValueError("Formato de pago inválido")

    rubro = str(p.get('rubro') or '').strip()
    if not rubro:
        raise ValueError("Falta el rubro")

    try:
        importe = float(p.get('importe'))
    except (TypeError, ValueError):
        raise ValueError("El importe no es válido")
    if importe <= 0:
        raise ValueError("El importe debe ser mayor a 0")

    venc = str(p.get('vencimiento') or '').strip()
    try:
        datetime.strptime(venc, '%Y-%m-%d')
    except ValueError:
        raise ValueError("El vencimiento debe tener formato AAAA-MM-DD")

    p['rubro'] = rubro
    p['importe'] = importe
    p['vencimiento'] = venc
    return p


@pagos_bp.route('/pagos/agregar', methods=['POST'])
@login_required
def agregar_pago():
    """
    Crea uno o varios pagos (cuotas o único) en UNA sola transacción:
    si falla uno, no se guarda ninguno.
    """
    nuevos = request.get_json(silent=True)
    if nuevos is None and request.form:
        nuevos = request.form.to_dict()
    if isinstance(nuevos, dict):
        nuevos = [nuevos]
    if not nuevos or not isinstance(nuevos, list):
        return jsonify({"error": "No se recibieron datos"}), 400

    try:
        for nuevo in nuevos:
            _validar_pago(nuevo)
            pago_store._crear_desde_dict(nuevo)
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error agregando pagos: {e}")
        return jsonify({"error": f"Error al guardar en la base de datos: {e}"}), 500

    return jsonify({"mensaje": f"{len(nuevos)} pago(s) agregado(s) correctamente"})


@pagos_bp.route('/pagos/editar/<int:pid>', methods=['PUT'])
@login_required
def editar_pago(pid):
    """Actualiza un pago por ID."""
    try:
        modificado = request.get_json(silent=True) or {}
        if pago_store.actualizar_pago(pid, modificado):
            return jsonify({"mensaje": "Pago actualizado"}), 200
        return jsonify({"error": "Pago no encontrado"}), 404
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error editando pago {pid}: {e}")
        return jsonify({"error": f"No se pudo actualizar el pago: {e}"}), 500


@pagos_bp.route('/pagos/eliminar/<int:pid>', methods=['DELETE'])
@login_required
def eliminar_pago(pid):
    """Elimina un pago por ID."""
    if pago_store.eliminar_pago(pid):
        return jsonify({"mensaje": "Pago eliminado"})
    return jsonify({"error": "Pago no encontrado"}), 404


@pagos_bp.route('/pagos/mensuales/<int:anio>/<int:mes>')
@login_required
def pagos_mensuales(anio, mes):
    """Devuelve pagos y totales por rubro de un mes específico."""
    pagos = pago_store.leer_mes(anio, mes)
    rubros = pago_store.totales_por_rubro(anio, mes)
    return jsonify({"pagos": pagos, "rubros": rubros})


@pagos_bp.route('/pagos/toggle_estado/<int:id>', methods=['PATCH'])
@login_required
def toggle_estado_pago(id):
    """Alterna el estado de pagado de un pago."""
    nuevo_estado = pago_store.toggle_pagado(id)
    if nuevo_estado is not None:
        return jsonify({"msg": "Estado actualizado correctamente"})
    return jsonify({"error": "Pago no encontrado"}), 404


@pagos_bp.route('/pagos/clonar_mes', methods=['POST'])
@login_required
def clonar_mes():
    """Clona los pagos de un mes a otro."""
    data = request.get_json(silent=True) or {}
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


@pagos_bp.route('/api/rubros', methods=['GET'])
@login_required
def obtener_rubros():
    """Devuelve el árbol de rubros para el selector de newPagos."""
    rubros = rubro_store.cargar_arbol()
    return jsonify(rubros)