# templates/Aplic/detectorderostros/BackEnd/detector_de_rostros.py
"""
Blueprint de Detector de Rostros.
"""
from flask_login import login_required, current_user
from core.menu import cargar_menu
from auth.login import roles_required
from flask import Blueprint, render_template
import os

_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_STATIC_DIR = os.path.abspath(os.path.join(_APP_DIR, '..', 'static'))

detector_de_rostros_bp = Blueprint(
    'indexdetector_de_rostros',
    __name__,
    static_folder=_STATIC_DIR,
    static_url_path='/detectorderostros/static'
)

@detector_de_rostros_bp.route('/detector_de_rostros')
@login_required
@roles_required('viewer')
def indexdetector_de_rostros():
    nemu = cargar_menu()
    return render_template(
        'Aplic/detectorderostros/FrontEnd/detector_de_rostros.html',
        nemu=nemu,
        roles=current_user.roles
    )