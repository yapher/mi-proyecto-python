# Archivo backend generado automáticamente

from flask_login import login_required, current_user
from menu import cargar_menu
from login import roles_required
from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, current_app
import json, re, os

imagenes_bp = Blueprint('indeximagenes', __name__)

# Copiar y pegar estas dos linea en app.py
#from templates.Aplic.imagenes.BackEnd.imagenes import imagenes_bp
#app.register_blueprint(imagenes_bp)

@imagenes_bp.route('/imagenes')
@login_required
@roles_required('viewer')
def indeximagenes():
    nemu = cargar_menu()
    return render_template('Aplic/imagenes/FrontEnd/imagenes.html',nemu=nemu, roles=current_user.roles)
