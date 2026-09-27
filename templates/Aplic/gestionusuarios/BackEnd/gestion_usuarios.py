"""
Blueprint de Gestión de Usuarios.
Solo accesible para administradores.
Permite crear, editar, eliminar usuarios y asignar roles.
✅ SEGURIDAD: Contraseñas hasheadas con werkzeug.security
"""
from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from auth.login import roles_required, hash_password
from core.menu import cargar_menu
from core.db_sql import db
from core.models import Usuario
import os

# ✅ NUEVO: Logger centralizado
from core.logging_config import get_logger
logger = get_logger(__name__)

_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_STATIC_DIR = os.path.abspath(os.path.join(_APP_DIR, '..', 'static'))

gestion_usuarios_bp = Blueprint(
    'indexgestion_usuarios',
    __name__,
    static_folder=_STATIC_DIR,
    static_url_path='/gestionusuarios/static'
)


# ============================================================
# RUTAS HTML
# ============================================================
@gestion_usuarios_bp.route('/gestion_usuarios')
@login_required
@roles_required('admin')
def indexgestion_usuarios():
    """Vista principal de gestión de usuarios."""
    nemu = cargar_menu()
    return render_template(
        'Aplic/gestionusuarios/FrontEnd/gestion_usuarios.html',
        nemu=nemu,
        roles=current_user.roles
    )


# ============================================================
# API REST: Listar todos los usuarios
# ============================================================
@gestion_usuarios_bp.route('/api/usuarios', methods=['GET'])
@login_required
@roles_required('admin')
def listar_usuarios():
    """Retorna todos los usuarios (sin passwords)."""
    usuarios = Usuario.query.all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'roles': u.roles or [],
        'created_at': u.created_at.isoformat() if u.created_at else None
    } for u in usuarios])


# ============================================================
# API REST: Crear usuario
# ============================================================
@gestion_usuarios_bp.route('/api/usuarios', methods=['POST'])
@login_required
@roles_required('admin')
def crear_usuario():
    """Crea un nuevo usuario con contraseña hasheada."""
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()
    roles = data.get('roles', [])

    # Validaciones
    if not username or not password:
        return jsonify({'msg': 'Usuario y contraseña son obligatorios', 'type': 'error'}), 400

    if len(password) < 4:
        return jsonify({'msg': 'La contraseña debe tener al menos 4 caracteres', 'type': 'error'}), 400

    # Verificar unicidad de username
    if Usuario.query.filter_by(username=username).first():
        return jsonify({'msg': f'El usuario "{username}" ya existe', 'type': 'error'}), 400

    # Validar roles
    roles_validos = ['admin', 'editor', 'viewer']
    roles_filtrados = [r for r in roles if r in roles_validos]

    if not roles_filtrados:
        return jsonify({'msg': 'Debe asignar al menos un rol válido', 'type': 'error'}), 400

    # ✅ NUEVO: Hashear contraseña antes de guardar
    password_hash = hash_password(password)

    # Crear usuario
    nuevo_usuario = Usuario(
        id=username,
        username=username,
        password=password_hash,  # ✅ Hash en lugar de texto plano
        roles=roles_filtrados
    )
    db.session.add(nuevo_usuario)
    db.session.commit()

    logger.info(f"Usuario creado: {username} por admin {current_user.username}")

    return jsonify({
        'msg': f'Usuario "{username}" creado correctamente',
        'type': 'success',
        'usuario': {
            'id': nuevo_usuario.id,
            'username': nuevo_usuario.username,
            'roles': nuevo_usuario.roles
        }
    }), 201


# ============================================================
# API REST: Actualizar usuario
# ============================================================
@gestion_usuarios_bp.route('/api/usuarios/<string:usuario_id>', methods=['PUT'])
@login_required
@roles_required('admin')
def actualizar_usuario(usuario_id):
    """Actualiza un usuario existente."""
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({'msg': 'Usuario no encontrado', 'type': 'error'}), 404

    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()
    roles = data.get('roles', [])

    # Validar username si cambió
    if username and username != usuario.username:
        if Usuario.query.filter_by(username=username).first():
            return jsonify({'msg': f'El usuario "{username}" ya existe', 'type': 'error'}), 400
        usuario.username = username
        usuario.id = username

    # ✅ NUEVO: Si se proporciona nueva contraseña, hashearla
    if password:
        if len(password) < 4:
            return jsonify({'msg': 'La contraseña debe tener al menos 4 caracteres', 'type': 'error'}), 400
        usuario.password = hash_password(password)  # ✅ Hash
        logger.info(f"Contraseña actualizada para usuario: {username}")

    # Validar roles
    roles_validos = ['admin', 'editor', 'viewer']
    roles_filtrados = [r for r in roles if r in roles_validos]

    if not roles_filtrados:
        return jsonify({'msg': 'Debe asignar al menos un rol válido', 'type': 'error'}), 400

    # Verificar que no se quede sin admins
    if 'admin' not in roles_filtrados and usuario.username == current_user.username:
        return jsonify({'msg': 'No puedes quitarte el rol de administrador', 'type': 'error'}), 400

    usuario.roles = roles_filtrados
    db.session.commit()

    logger.info(f"Usuario actualizado: {username} por admin {current_user.username}")

    return jsonify({
        'msg': 'Usuario actualizado correctamente',
        'type': 'success',
        'usuario': {
            'id': usuario.id,
            'username': usuario.username,
            'roles': usuario.roles
        }
    })


# ============================================================
# API REST: Eliminar usuario
# ============================================================
@gestion_usuarios_bp.route('/api/usuarios/<string:usuario_id>', methods=['DELETE'])
@login_required
@roles_required('admin')
def eliminar_usuario(usuario_id):
    """Elimina un usuario."""
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({'msg': 'Usuario no encontrado', 'type': 'error'}), 404

    # No permitir eliminar el propio usuario
    if usuario.username == current_user.username:
        return jsonify({'msg': 'No puedes eliminar tu propio usuario', 'type': 'error'}), 400

    # Verificar que no sea el último admin
    if 'admin' in usuario.roles:
        total_admins = Usuario.query.filter(Usuario.roles.contains(['admin'])).count()
        if total_admins <= 1:
            return jsonify({'msg': 'No se puede eliminar el último administrador', 'type': 'error'}), 400

    username_eliminado = usuario.username
    db.session.delete(usuario)
    db.session.commit()

    logger.info(f"Usuario eliminado: {username_eliminado} por admin {current_user.username}")

    return jsonify({
        'msg': f'Usuario "{username_eliminado}" eliminado correctamente',
        'type': 'success'
    })


# ============================================================
# API REST: Obtener roles disponibles
# ============================================================
@gestion_usuarios_bp.route('/api/roles', methods=['GET'])
@login_required
@roles_required('admin')
def obtener_roles():
    """Retorna la lista de roles disponibles."""
    return jsonify(['admin', 'editor', 'viewer'])