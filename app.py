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

# Importar desde las nuevas ubicaciones
from core.menu import cargar_menu
from auth.login import init_routes_login, roles_required
from core.blueprint_registry import auto_register_blueprints
from core.scheduler import setup_scheduler

# ============================================================
# Crear app
# ============================================================
app = Flask(__name__)

# ============================================================
# Base de datos (SQLAlchemy)
# ============================================================
from core.db_sql import init_db
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# 1. Asegurar que el directorio DataBase exista (usando ruta absoluta)
db_dir = Path(__file__).parent / 'DataBase'
db_dir.mkdir(exist_ok=True)  # ✅ CORREGIDO: exist_ok en lugar de exexist_ok
db_path = db_dir / 'empresa.db'

# 2. Configurar URI: Si hay PostgreSQL en .env, lo usa. Si no, usa SQLite local con ruta absoluta.
env_db_url = os.environ.get('DATABASE_URL')
if env_db_url and env_db_url.startswith('postgresql'):
    app.config['SQLALCHEMY_DATABASE_URI'] = env_db_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 3. Inicializar base de datos
init_db(app)

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
    return render_template("403.html"), 404

# ============================================================
# Arranque
# ============================================================
def _abrir_navegador():
    webbrowser.open("http://127.0.0.1:5000")

# ============================================================
# AUTO-SEED: Si no hay usuarios, ejecutar seed automáticamente
# ============================================================
with app.app_context():
    from core.models import Usuario
    if Usuario.query.count() == 0:
        print("🌱 DB vacía detectada. Ejecutando seed...")
        from scripts.seed_render import seed_todo
        seed_todo()

if __name__ == "__main__":
    os.makedirs("DataBase/Config", exist_ok=True)
    
    # Iniciar scheduler solo si no estamos en modo reload de Flask
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        scheduler.start()
        threading.Timer(1.0, _abrir_navegador).start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)