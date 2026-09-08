"""
Aplicación principal.
- Auto-registro de blueprints (no hay que tocar este archivo al agregar apps)
- Configuración de mail, scheduler, login y context processors
- Configuración de seguridad y proxies para producción (Render)
"""
import os
import threading
import webbrowser
from pathlib import Path
from flask import Flask, render_template
from flask_login import login_required, current_user
from flask_mail import Mail
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

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

# ============================================================
# Configuración de PROXY (CRÍTICO para Render)
# Render usa proxies, necesitamos confiar en ellos para detectar HTTPS
# ============================================================
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# ============================================================
# Configuración de Base de Datos (SQLAlchemy)
# ============================================================
env_db_url = os.environ.get('DATABASE_URL')

if env_db_url:
    # Render a veces usa 'postgres://' en lugar de 'postgresql://'
    # SQLAlchemy requiere 'postgresql://' obligatoriamente
    if env_db_url.startswith('postgres://'):
        env_db_url = env_db_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = env_db_url
    print("📦 Usando base de datos PostgreSQL (Render o local con .env)")
else:
    # Fallback: SQLite local
    db_dir = Path(__file__).parent / 'DataBase'
    db_dir.mkdir(exist_ok=True)
    db_path = db_dir / 'empresa.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    print(f"📦 Usando base de datos SQLite local: {db_path}")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar base de datos
init_db(app)

# ============================================================
# Configuración de SEGURIDAD para producción (HTTPS)
# ============================================================
# Detectar si estamos en producción (Render)
is_production = bool(os.environ.get('DATABASE_URL'))

if is_production:
    # Configuración para producción (HTTPS)
    app.config['SESSION_COOKIE_SECURE'] = True      # Cookies solo por HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True    # No accesible por JavaScript
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'   # Protección CSRF
    app.config['REMEMBER_COOKIE_SECURE'] = True     # Cookie "recordarme" solo por HTTPS
    app.config['REMEMBER_COOKIE_HTTPONLY'] = True
    app.config['REMEMBER_COOKIE_SAMESITE'] = 'Lax'
    app.config['PREFERRED_URL_SCHEME'] = 'https'    # URLs generadas serán HTTPS
    print("🔒 Modo PRODUCCIÓN: Cookies seguras habilitadas")
else:
    # Configuración para desarrollo (HTTP local)
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['REMEMBER_COOKIE_SECURE'] = False
    app.config['REMEMBER_COOKIE_HTTPONLY'] = True
    app.config['REMEMBER_COOKIE_SAMESITE'] = 'Lax'
    print("🔧 Modo DESARROLLO: Cookies normales")

# ============================================================
# Crear tablas y AUTO-SEED
# ============================================================
with app.app_context():
    db.create_all()  # Asegura que las tablas existan antes de consultar
    
    # Si no hay usuarios, ejecutar seed automáticamente
    from core.models import Usuario
    if Usuario.query.count() == 0:
        print("🌱 DB vacía detectada. Ejecutando seed inicial...")
        try:
            from scripts.seed_render import seed_todo
            seed_todo()
        except ImportError:
            print("⚠️ No se encontró el script de seed, continuando sin datos iniciales.")

# ============================================================
# Configuración General y Secret Key
# ============================================================
app.secret_key = os.environ.get("SECRET_KEY", "221d18b67f2d4705a132d532b1d12ab2")

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
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME", "oherasimovich730@alumnos.iua.edu.ar")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "cvoe jyvn psqp tgjl")
app.config["MAIL_DEFAULT_SENDER"] = app.config["MAIL_USERNAME"]
mail = Mail(app)

# ============================================================
# Scheduler (solo se inicia en el proceso principal)
# ============================================================
scheduler = setup_scheduler(app, mail)

# ============================================================
# FILTRO JINJA2: Intersect (A prueba de balas)
# ============================================================
@app.template_filter('intersect')
def intersect_filter(user_roles, item_roles):
    """
    Devuelve True si hay al menos un rol en común.
    Maneja casos donde los roles vienen como string desde la DB.
    """
    # Si el ítem no tiene roles definidos, es público (True)
    if not item_roles:
        return True
    
    try:
        # Si item_roles es un string (ej: "['admin']"), lo convertimos a lista
        if isinstance(item_roles, str):
            import json
            item_roles = json.loads(item_roles)
            
        # Aseguramos que ambos sean conjuntos (sets)
        user_set = set(user_roles) if isinstance(user_roles, (list, set, tuple)) else set()
        item_set = set(item_roles) if isinstance(item_roles, (list, set, tuple)) else set()
        
        return bool(user_set & item_set)
    except Exception:
        # Si hay cualquier error, por seguridad mostramos el ítem
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
# RUTA DE DEPURACIÓN DEL MENÚ (¡Eliminar cuando funcione!)
# ============================================================
@app.route("/debug_menu")
@login_required
def debug_menu():
    from core.menu import cargar_menu
    import json
    
    menu_data = cargar_menu()
    user_roles = current_user.roles if current_user.is_authenticated else []
    
    html = f"<h2>🔍 Depuración del Menú para: {current_user.username}</h2>"
    html += f"<p><strong>Roles del usuario:</strong> {user_roles} <em>(Tipo: {type(user_roles).__name__})</em></p>"
    
    html += "<h3>Menú crudo desde la base de datos:</h3>"
    html += "<pre style='background:#f4f4f4; padding:15px; border-radius:5px; overflow:auto;'>"
    html += json.dumps(menu_data, indent=2, ensure_ascii=False)
    html += "</pre>"
    
    html += "<h3>Prueba del filtro intersect:</h3>"
    html += "<ul>"
    for item in menu_data:
        # Simulamos lo que hace el template
        item_roles = item.get('roles', [])
        resultado = intersect_filter(user_roles, item_roles)
        color = "green" if resultado else "red"
        html += f"<li style='color:{color}'>{item.get('emoji')} {item.get('nombre')} (Roles del ítem: {item_roles}) → <strong>{resultado}</strong></li>"
    html += "</ul>"
    
    return html


# ============================================================
# RUTA DE DEPURACIÓN TEMPORAL (¡Eliminar después de arreglar!)
# ============================================================
@app.route("/debug_db")
def debug_db():
    from core.models import Usuario
    usuarios = Usuario.query.all()
    info = []
    for u in usuarios:
        info.append(f"👤 {u.username} | Pass: '{u.password}' | Roles: {u.roles}")
    return "<h3>Usuarios en la DB de Render en vivo:</h3>" + "<br>".join(info)

@app.route("/fix_usuario")
def fix_usuario():
    from core.models import Usuario
    from core.db_sql import db
    
    # Buscar el usuario 'viewer' y cambiarlo a 'usuario'
    u = Usuario.query.filter_by(username='viewer').first()
    if u:
        u.username = 'usuario'
        u.password = 'usuario123'
        db.session.commit()
        return "✅ Usuario actualizado a 'usuario' / 'usuario123' en Render"
    
    # Si no existe 'viewer', creamos 'usuario'
    nuevo = Usuario(id='2', username='usuario', password='usuario123', roles=['viewer'])
    db.session.add(nuevo)
    db.session.commit()
    return "✅ Usuario 'usuario' creado en Render"


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
    
    # Iniciar scheduler solo si no estamos en modo reload de Flask (evita duplicados en local)
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        scheduler.start()
        threading.Timer(1.0, _abrir_navegador).start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)