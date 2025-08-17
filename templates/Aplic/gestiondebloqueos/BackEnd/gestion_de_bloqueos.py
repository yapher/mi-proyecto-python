from flask_login import login_required, current_user
from flask import Blueprint, render_template, redirect, request, session, url_for
from login import roles_required
from menu import cargar_menu
import requests
import base64

gestion_de_bloqueos_bp = Blueprint('indexgestion_de_bloqueos', __name__)



@gestion_de_bloqueos_bp.route('/gestion_de_bloqueos')
@login_required
@roles_required('viewer')
def indexgestion_de_bloqueos():
    nemu = cargar_menu()
   

    return render_template('Aplic/gestiondebloqueos/FrontEnd/gestion_de_bloqueos.html',
                           nemu=nemu, roles=current_user.roles)

