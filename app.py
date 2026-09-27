"""
Aplicación principal.
- Auto-registro de blueprints (no hay que tocar este archivo al agregar apps)
- Configuración de mail, scheduler, login y context processors
- Configuración de seguridad y proxies para producción (Render)
- Logging centralizado
- Protección CSRF
"""
import os
import threading
import webbrowser
from pathlib import Path
from flask import Flask, render_template, jsonify
from flask_login import login_required, current_user
from flask_mail import Mail
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

# ✅ NUEVO: Importar logging centralizado
from core.logging_config import setup_logging, get_logger

# ✅ NUEVO: Importar CSRF
from core.csrf import init_csrf, generate_csrf_token

# 1. Cargar variables de entorno (.env) AL INICIO
load_dotenv()

# Importar módulos internos
from core.menu import cargar_menu
from auth.login import init_routes_login, roles_required
from core.blueprint_registry import auto_register_blueprints
from core.scheduler import setup_scheduler
from core.db_sql import db, init_db

# ============================================================
# Crear app
# ============================================================
app = Flask(__name__)

# ✅ NUEVO: Configurar logging centralizado
setup_logging("Empresa")
logger = get_logger("app")
logger.info("🚀 Iniciando aplicación Flask")

# ============================================================
# Configuración de PROXY (CRÍTICO para Render)
# ============================================================
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# ============================================================
# Configuración de Base de Datos (SQLAlchemy)
# ============================================================
env_db_url = os.environ.get('DATABASE_URL')
if env_db_url:
    if env_db_url.startswith('postgres://'):
        env_db_url = env_db_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = env_db_url
    logger.info("📦 Usando base de datos PostgreSQL (Render o local con .env)")
else:
    db_dir = Path(__file__).parent / 'DataBase'
    db_dir.mkdir(exist_ok=True)
    db_path = db_dir / 'empresa.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    logger.info(f"📦 Usando base de datos SQLite local: {db_path}")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar base de datos
init_db(app)

# ============================================================
# Configuración de SEGURIDAD para producción (HTTPS)
# ============================================================
is_production = bool(os.environ.get('DATABASE_URL'))
if is_production:
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['REMEMBER_COOKIE_SECURE'] = True
    app.config['REMEMBER_COOKIE_HTTPONLY'] = True
    app.config['REMEMBER_COOKIE_SAMESITE'] = 'Lax'
    app.config['PREFERRED_URL_SCHEME'] = 'https'
    logger.info("🔒 Modo PRODUCCIÓN: Cookies seguras habilitadas")
else:
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['REMEMBER_COOKIE_SECURE'] = False
    app.config['REMEMBER_COOKIE_HTTPONLY'] = True
    app.config['REMEMBER_COOKIE_SAMESITE'] = 'Lax'
    logger.info("🔧 Modo DESARROLLO: Cookies normales")

# ============================================================
# Crear tablas y AUTO-SEED
# ============================================================
with app.app_context():
    db.create_all()

    from core.models import Usuario
    if Usuario.query.count() == 0:
        logger.warning("🌱 DB vacía detectada. Ejecutando seed inicial...")
        try:
            from scripts.seed_render import seed_todo
            seed_todo()
        except ImportError:
            logger.warning("⚠️ No se encontró el script de seed, continuando sin datos iniciales.")

# ============================================================
# Configuración General y Secret Key
# ============================================================
app.secret_key = os.environ.get("SECRET_KEY", "221d18b67f2d4705a132d532b1d12ab2")

# ============================================================
# ✅ NUEVO: Inicializar CSRF
# ============================================================
init_csrf(app)

# ============================================================
# Autenticación
# ============================================================
init_routes_login(app)

# ============================================================
# Auto-registro de TODOS los blueprints
# ============================================================
auto_register_blueprints(app)

# ============================================================
# Mail (recordatorios de agenda)
# ============================================================
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME", "oherasimovich730@alumnos.iua.edu.ar")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "cvoe jyvn psqp tgjl")
app.config["MAIL_DEFAULT_SENDER"] = app.config["MAIL_USERNAME"]
mail = Mail(app)

# ============================================================
# Scheduler
# ============================================================
scheduler = setup_scheduler(app, mail)

# ============================================================
# FILTRO JINJA2: Intersect
# ============================================================
@app.template_filter('intersect')
def intersect_filter(user_roles, item_roles):
    if not item_roles:
        return True
    try:
        if isinstance(item_roles, str):
            import json
            item_roles = json.loads(item_roles)
        user_set = set(user_roles) if isinstance(user_roles, (list, set, tuple)) else set()
        item_set = set(item_roles) if isinstance(item_roles, (list, set, tuple)) else set()
        return bool(user_set & item_set)
    except Exception:
        return True

# ============================================================
# Context processor: inyecta menú y roles en TODAS las plantillas
# ============================================================
@app.context_processor
def inject_menu():
    if current_user.is_authenticated:
        return dict(
            menu=cargar_menu(),
            roles=current_user.roles if current_user.roles else []
        )
    return dict(menu=[], roles=[])

# ============================================================
# MIDDLEWARE: Verificación dinámica de acceso por roles del menú
# ============================================================
@app.before_request
def verificar_acceso_menu():
    from flask import request
    from flask_login import current_user

    rutas_publicas = [
        '/login', '/logout', '/health', '/static',
        '/login_rostro', '/favicon.ico', '/api/csrf-token'
    ]
    if any(request.path.startswith(ruta) for ruta in rutas_publicas):
        return None

    if not current_user.is_authenticated:
        return None

    from core.menu import obtener_roles_por_ruta
    roles_requeridos = obtener_roles_por_ruta(request.path)

    if not roles_requeridos:
        return None

    user_roles = set(current_user.roles or [])
    required_roles = set(roles_requeridos)

    if not user_roles & required_roles:
        logger.warning(f"🚫 Acceso denegado: {current_user.username} intentó acceder a {request.path}")
        from flask import abort
        abort(403)

    return None

# ============================================================
# ✅ NUEVO: Endpoint para obtener token CSRF (útil para AJAX)
# ============================================================
@app.route('/api/csrf-token', methods=['GET'])
@login_required
def get_csrf_token():
    """Retorna el token CSRF actual para usar en requests AJAX."""
    return jsonify({'csrf_token': generate_csrf_token()})

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

@app.route("/health")
def health():
    return {"status": "ok", "message": "App funcionando correctamente"}

# ============================================================
# Manejo de errores
# ============================================================
@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

# ============================================================
# Arranque
# ============================================================
def _abrir_navegador():
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    os.makedirs("DataBase/Config", exist_ok=True)

    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        scheduler.start()

    threading.Timer(1.0, _abrir_navegador).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)