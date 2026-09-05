"""
Módulo de autenticación y autorización.
Contiene login, gestión de usuarios y decoradores de roles.
AHORA USA SQL para usuarios (no más JSON).
"""
from .login import (
    User,
    init_routes_login,
    roles_required,
    comparar_rostros,
)

__all__ = [
    'User',
    'init_routes_login',
    'roles_required',
    'comparar_rostros',
]