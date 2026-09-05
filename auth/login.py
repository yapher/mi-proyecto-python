"""
Módulo de autenticación: login por credenciales y reconocimiento facial.
AHORA USA SQL para usuarios.
"""
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import request, redirect, url_for, render_template, abort, flash
from datetime import datetime
import os
from functools import wraps
import cv2
import numpy as np
from core.db_sql import db
from core.models import Usuario


# Ruta de rostros (se mantiene en filesystem)
ROSTROS_DIR = 'static/rostros'


class User(UserMixin):
    """Modelo de usuario para Flask-Login."""
    def __init__(self, id, username, roles):
        self.id = id
        self.username = username
        self.roles = roles if isinstance(roles, list) else []

    def has_role(self, role):
        return role in self.roles


def roles_required(*roles):
    """Decorador para requerir roles específicos."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if not any(current_user.has_role(role) for role in roles):
                return abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator


def comparar_rostros(rostro1, rostro2):
    """Compara dos imágenes de rostros y retorna similitud."""
    rostro1_gray = cv2.cvtColor(rostro1, cv2.COLOR_BGR2GRAY)
    rostro2_gray = cv2.cvtColor(rostro2, cv2.COLOR_BGR2GRAY)
    rostro1_gray = cv2.resize(rostro1_gray, (150, 150))
    rostro2_gray = cv2.resize(rostro2_gray, (150, 150))
    rostro1_gray = cv2.equalizeHist(rostro1_gray)
    rostro2_gray = cv2.equalizeHist(rostro2_gray)
    resultado = cv2.matchTemplate(rostro1_gray, rostro2_gray, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(resultado)
    return max_val


def init_routes_login(app):
    """Inicializa las rutas de login y Flask-Login."""
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @login_manager.user_loader
    def load_user(user_id):
        # ✅ USAR SQL en lugar de JSON
        usuario = Usuario.query.get(str(user_id))
        if usuario:
            return User(usuario.id, usuario.username, usuario.roles)
        return None

    @app.template_filter('intersect')
    def intersect_filter(user_roles, item_roles):
        if not item_roles:
            return True
        return bool(set(user_roles) & set(item_roles))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            # ✅ USAR SQL en lugar de JSON
            usuario = Usuario.query.filter_by(username=username, password=password).first()
            
            if usuario:
                user = User(usuario.id, usuario.username, usuario.roles)
                login_user(user)
                return redirect(request.args.get('next') or url_for('index'))
            else:
                flash("Usuario o contraseña incorrectos. Puede intentar con reconocimiento facial.")
        return render_template('login.html', error=error, current_year=datetime.now().year)

    @app.route('/login_rostro', methods=['POST'])
    def login_rostro():
        debug_info = []
        if 'rostro' not in request.files:
            flash("No se envió imagen del rostro.")
            return redirect(url_for('login'))

        file = request.files['rostro']
        in_memory_file = file.read()
        npimg = np.frombuffer(in_memory_file, np.uint8)
        rostro_capturado = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        if rostro_capturado is None:
            flash("Error al procesar la imagen del rostro.")
            return redirect(url_for('login'))

        debug_info.append("Imagen recibida y decodificada correctamente.")

        # ✅ USAR SQL en lugar de JSON
        usuarios = Usuario.query.all()
        
        for usuario in usuarios:
            ruta_rostro = f"{ROSTROS_DIR}/{usuario.username}.png"
            if not os.path.exists(ruta_rostro):
                debug_info.append(f"Imagen de referencia no encontrada para usuario '{usuario.username}'.")
                continue

            rostro_guardado = cv2.imread(ruta_rostro)
            if rostro_guardado is None:
                debug_info.append(f"No se pudo leer la imagen de referencia para usuario '{usuario.username}'.")
                continue

            similitud = comparar_rostros(rostro_capturado, rostro_guardado)
            debug_info.append(f"Similitud con usuario '{usuario.username}': {similitud:.3f}")

            if similitud > 0.4:
                user = User(usuario.id, usuario.username, usuario.roles)
                login_user(user)
                debug_info.append(f"¡Login exitoso con usuario '{usuario.username}'!")
                return redirect(request.args.get('next') or url_for('index'))

        flash("Rostro no coincide con ningún usuario.")
        return redirect(url_for('login'))