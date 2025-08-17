# Archivo backend generado automáticamente

from flask_login import login_required, current_user
from menu import cargar_menu
from login import roles_required
from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, current_app
from templates.Aplic.tareas.BackEnd.db_manager import cargar_eventos, agregar_evento, editar_evento, eliminar_evento

import json, re, os

tareas_bp = Blueprint('indextareas', __name__)


@tareas_bp.route('/tareas')
@login_required
@roles_required('viewer')
def indextareas():
    eventos = cargar_eventos()
    nemu = cargar_menu()
    return render_template('Aplic/tareas/FrontEnd/tareas.html',nemu=nemu, roles=current_user.roles, eventos=eventos)

@tareas_bp.route("/agregar", methods=["POST"])
@login_required
@roles_required('viewer')
def agregar():
    nuevo_evento = {
        "titulo": request.form["titulo"],
        "fecha": request.form["fecha"],
        "descripcion": request.form["descripcion"]
    }
    agregar_evento(nuevo_evento)
    return redirect("/tareas")

@tareas_bp.route("/editar/<int:evento_id>", methods=["POST"])
@login_required
@roles_required('viewer')
def editar(evento_id):
    nuevos_datos = {
        "titulo": request.form["titulo"],
        "fecha": request.form["fecha"],
        "descripcion": request.form["descripcion"]
    }
    editar_evento(evento_id, nuevos_datos)
    return redirect("/tareas")

@tareas_bp.route("/eliminar/<int:evento_id>")
@login_required
@roles_required('viewer')
def eliminar(evento_id):
    eliminar_evento(evento_id)
    return redirect("/tareas")