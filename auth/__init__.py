"""
Módulo de autenticación y autorización.
Contiene login, gestión de usuarios y decoradores de roles.
"""
from .login import (
    User,
    cargar_usuarios,
    init_routes_login,
    roles_required,
    comparar_rostros,
    USERS_PATH
)

__all__ = [
    'User',
    'cargar_usuarios',
    'init_routes_login',
    'roles_required',
    'comparar_rostros',
    'USERS_PATH'
]