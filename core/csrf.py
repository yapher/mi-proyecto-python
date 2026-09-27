"""
core/csrf.py
============
Protección CSRF reutilizable para Flask.
Genera y valida tokens CSRF de forma segura.

Uso:
    from core.csrf import csrf_protect, generate_csrf_token, init_csrf

    # En app.py:
    init_csrf(app)

    # En blueprints:
    @bp.route('/api/endpoint', methods=['POST'])
    @csrf_protect
    def endpoint():
        return jsonify({'status': 'ok'})
"""
import secrets
from functools import wraps
from flask import request, session, abort, current_app


def generate_csrf_token():
    """
    Genera un token CSRF único para la sesión actual.
    El token se almacena en la sesión y se puede incluir en formularios.
    """
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(32)
    return session['_csrf_token']


def validate_csrf_token(token):
    """
    Valida que el token CSRF coincida con el de la sesión.
    Usa comparación segura contra ataques de timing.
    """
    session_token = session.get('_csrf_token')
    if not session_token or not token:
        return False
    return secrets.compare_digest(session_token, token)


def csrf_protect(f):
    """
    Decorador para proteger endpoints contra ataques CSRF.
    Solo aplica a métodos POST, PUT, PATCH, DELETE.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Solo proteger métodos que modifican datos
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            # Obtener token del header, form data o JSON
            token = (
                request.headers.get('X-CSRFToken') or
                request.headers.get('X-CSRF-Token') or
                request.form.get('_csrf_token') or
                (request.json.get('_csrf_token') if request.is_json else None)
            )

            if not validate_csrf_token(token):
                current_app.logger.warning(
                    f"CSRF token validation failed for {request.path} "
                    f"from {request.remote_addr}"
                )
                abort(403, description="CSRF token validation failed")

        return f(*args, **kwargs)

    return decorated_function


def csrf_exempt(f):
    """
    Decorador para eximir endpoints de protección CSRF.
    Útil para webhooks o APIs públicas.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)

    decorated_function._csrf_exempt = True
    return decorated_function


def init_csrf(app):
    """
    Inicializa el sistema CSRF para la aplicación.
    Agrega el token CSRF al contexto de todos los templates.
    """
    @app.context_processor
    def csrf_processor():
        return {'csrf_token': generate_csrf_token()}

    app.config.setdefault('SESSION_COOKIE_SAMESITE', 'Lax')
    app.config.setdefault('SESSION_COOKIE_HTTPONLY', True)

    if not app.debug:
        app.config.setdefault('SESSION_COOKIE_SECURE', True)

    app.logger.info("✅ CSRF protection initialized")