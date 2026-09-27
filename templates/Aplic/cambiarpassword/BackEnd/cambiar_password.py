"""
Blueprint de Cambio de Contraseña
Permite a los usuarios cambiar su contraseña
✅ SEGURIDAD: Verifica hash de contraseñas
✅ CSRF: Endpoint protegido
"""
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from auth.login import roles_required, hash_password, verify_password
from core.menu import cargar_menu
from core.db_sql import db
from core.models import Usuario
from core.csrf import csrf_protect
import os

# ✅ NUEVO: Logger
from core.logging_config import get_logger
logger = get_logger(__name__)

_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_STATIC_DIR = os.path.abspath(os.path.join(_APP_DIR, '..', 'static'))

cambiar_password_bp = Blueprint(
    'indexcambiar_password',
    __name__,
    static_folder=_STATIC_DIR,
    static_url_path='/cambiarpassword/static'
)

@cambiar_password_bp.route('/cambiar_password')
@login_required
def indexcambiar_password():
    """Vista principal (puede ser accedida directamente o via modal)"""
    nemu = cargar_menu()
    return render_template(
        'Aplic/cambiarpassword/FrontEnd/cambiar_password.html',
        nemu=nemu,
        roles=current_user.roles
    )

@cambiar_password_bp.route('/api/cambiar_password', methods=['POST'])
@login_required
@csrf_protect  # ✅ NUEVO: Protección CSRF
def api_cambiar_password():
    """API para cambiar la contraseña"""
    try:
        data = request.get_json()

        password_actual = data.get('password_actual', '')
        password_nueva = data.get('password_nueva', '')
        password_confirmar = data.get('password_confirmar', '')

        if not password_actual or not password_nueva or not password_confirmar:
            return jsonify({
                'status': 'error',
                'msg': 'Todos los campos son obligatorios'
            }), 400

        if password_nueva != password_confirmar:
            return jsonify({
                'status': 'error',
                'msg': 'Las contraseñas nuevas no coinciden'
            }), 400

        if len(password_nueva) < 4:
            return jsonify({
                'status': 'error',
                'msg': 'La nueva contraseña debe tener al menos 4 caracteres'
            }), 400

        usuario = Usuario.query.get(current_user.id)
        if not usuario:
            return jsonify({
                'status': 'error',
                'msg': 'Usuario no encontrado'
            }), 404

        # ✅ Verificar contraseña actual (soporta hash y texto plano legacy)
        password_guardada = usuario.password
        password_valida = False

        if password_guardada and password_guardada.startswith(('pbkdf2:', 'scrypt:', 'argon2')):
            password_valida = verify_password(password_actual, password_guardada)
        else:
            password_valida = (password_guardada == password_actual)

        if not password_valida:
            logger.warning(f"Intento de cambio de contraseña fallido para {usuario.username}")
            return jsonify({
                'status': 'error',
                'msg': 'La contraseña actual es incorrecta'
            }), 401

        # ✅ Hashear nueva contraseña
        usuario.password = hash_password(password_nueva)
        db.session.commit()

        logger.info(f"Contraseña cambiada exitosamente para usuario: {usuario.username}")

        return jsonify({
            'status': 'ok',
            'msg': 'Contraseña cambiada exitosamente'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al cambiar contraseña: {e}")
        return jsonify({
            'status': 'error',
            'msg': 'Error interno del servidor'
        }), 500