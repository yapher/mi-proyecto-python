# app.py
"""
Aplicación principal.
- Auto-registro de blueprints (no hay que tocar este archivo al agregar apps)
- Configuración de mail, scheduler, login y context processors
"""
from flask import Flask, render_template, redirect, url_for
import os
import threading
import webbrowser

from flask_login import login_required, current_user
from flask_mail import Mail

from menu import cargar_menu
from login import init_routes_login, roles_required

# Módulos centrales
from core.blueprint_registry import auto_register_blueprints
from core.scheduler import setup_scheduler

# ============================================================
# Crear app
# ============================================================
app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY", "221d18b67f2d4705a132d532b1d12ab2"
)

# ============================================================
# Autenticación
# ============================================================
init_routes_login(app)

# ============================================================
# Auto-registro de TODOS los blueprints
# Escanea templates/Aplic/*/BackEnd/*.py automáticamente
# ============================================================
auto_register_blueprints(app)

# ============================================================
# Mail (recordatorios de agenda)
# ============================================================
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get(
    "MAIL_USERNAME", "oherasimovich730@alumnos.iua.edu.ar"
)
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "cvoe jyvn psqp tgjl")
app.config["MAIL_DEFAULT_SENDER"] = app.config["MAIL_USERNAME"]
mail = Mail(app)

# ============================================================
# Scheduler (solo se inicia en el proceso principal)
# ============================================================
scheduler = setup_scheduler(app, mail)

# ============================================================
# Context processor: inyecta menú y roles en TODAS las plantillas
# ============================================================
@app.context_processor
def inject_menu():
    if current_user.is_authenticated:
        return dict(menu=cargar_menu(), roles=current_user.roles)
    return dict(menu=[], roles=[])


# ============================================================
# Rutas principales
# ============================================================
@app.route("/")
@login_required
def index():
    return render_template(
        "index.html",
        menu=cargar_menu(),
        roles=current_user.roles,
    )


@app.route("/gestion_menu")
@login_required
@roles_required("admin", "editor")
def gestion_menu():
    return render_template(
        "Aplic/GestionAplic/FrontEnd/gestion_menu.html",
        menu=cargar_menu(),
        roles=current_user.roles,
    )


@app.route("/gestion_aplicaciones")
@login_required
@roles_required("admin", "editor")
def gestion_aplicaciones():
    return render_template(
        "Aplic/GestionAplic/FrontEnd/gestion_aplicaciones.html",
        menu=cargar_menu(),
        roles=current_user.roles,
    )


# ============================================================
# Manejo de errores
# ============================================================
@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403


@app.errorhandler(404)
def not_found(e):
    return render_template("403.html"), 404  # o crea un 404.html


# ============================================================
# Arranque
# ============================================================
def _abrir_navegador():
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    os.makedirs("DataBase/Config", exist_ok=True)

    # Iniciar scheduler solo si no estamos en modo reload de Flask
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        scheduler.start()
        threading.Timer(1.0, _abrir_navegador).start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)