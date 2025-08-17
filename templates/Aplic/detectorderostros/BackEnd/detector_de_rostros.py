# Archivo backend generado automáticamente

from flask_login import login_required, current_user
from menu import cargar_menu
from login import roles_required
from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, current_app
import json, re, os

detector_de_rostros_bp = Blueprint('indexdetector_de_rostros', __name__)


@detector_de_rostros_bp.route('/detector_de_rostros')
@login_required
@roles_required('viewer')
def indexdetector_de_rostros():
    nemu = cargar_menu()
    return render_template('Aplic/detectorderostros/FrontEnd/detector_de_rostros.html',nemu=nemu, roles=current_user.roles)
