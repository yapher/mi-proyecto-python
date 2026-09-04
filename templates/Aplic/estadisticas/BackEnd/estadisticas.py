# Archivo backend generado automáticamente
from flask_login import login_required, current_user
from core.menu import cargar_menu
from auth.login import roles_required
from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, current_app
import json, re, os
from glob import glob
from datetime import datetime

# ✅ IMPORTAR MesStore desde core
from core.mes_store import MesStore

estadisticas_bp = Blueprint('indexestadisticas', __name__)

# ✅ Instancia reutilizable de MesStore
mes_store = MesStore(
    base_dir='DataBase/hogar',
    archivo_general='GASTOS',
    prefijo_mensual='GASTO'
)

@estadisticas_bp.route('/estadisticas')
@login_required
@roles_required('viewer')
def indexestadisticas():
    nemu = cargar_menu()
    return render_template('Aplic/estadisticas/FrontEnd/estadisticas.html', nemu=nemu, roles=current_user.roles)

@estadisticas_bp.route('/api/estadisticas')
@login_required
def api_estadisticas():
    # ✅ Usar MesStore para listar meses disponibles
    meses_disponibles = mes_store.listar_meses_disponibles()
    
    rubros = {}
    items = {}
    
    for anio, mes in meses_disponibles:
        fecha_fmt = f"{anio}-{mes:02d}"
        
        # ✅ Usar MesStore para leer mes
        pagos = mes_store.leer_mes(anio, mes)
        
        for p in pagos:
            rubro = p.get("rubro", "Sin Rubro")
            descripcion = p.get("descripcion", "Sin Descripción")
            importe = p.get("importe", 0)
            
            # Sumar por rubro y fecha
            if rubro not in rubros:
                rubros[rubro] = {}
            rubros[rubro][fecha_fmt] = rubros[rubro].get(fecha_fmt, 0) + importe
            
            # Sumar por ítem/descripción y fecha
            if descripcion not in items:
                items[descripcion] = {}
            items[descripcion][fecha_fmt] = items[descripcion].get(fecha_fmt, 0) + importe
    
    return jsonify({
        "rubros": rubros,
        "items": items
    })

@estadisticas_bp.route('/estadisticas/gasto_mensual')
@login_required
def gasto_mensual():
    # ✅ Usar MesStore para listar meses y calcular totales
    meses_disponibles = mes_store.listar_meses_disponibles()
    
    gastos_por_mes = {}
    
    for anio, mes in meses_disponibles:
        clave = f"{anio}-{mes:02d}"
        total = mes_store.total_mes(anio, mes)
        gastos_por_mes[clave] = total
    
    # Ordenar por fecha
    gastos_ordenados = dict(sorted(gastos_por_mes.items()))
    
    return jsonify(gastos_ordenados)