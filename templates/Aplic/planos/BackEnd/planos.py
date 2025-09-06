# Archivo backend generado automáticamente

from flask_login import login_required, current_user
from menu import cargar_menu
from login import roles_required
from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, current_app
import json, re, os

planos_bp = Blueprint('indexplanos', __name__)

# Copiar y pegar estas dos linea en app.py
#
#

@planos_bp.route('/planos')
@login_required
@roles_required('viewer')
def indexplanos():
    nemu = cargar_menu()
    return render_template('Aplic/planos/FrontEnd/planos.html',nemu=nemu, roles=current_user.roles)
