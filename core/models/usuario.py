"""
Modelo de Usuario.
Equivalente a users.json
"""
from core.db_sql import db
from datetime import datetime


class Usuario(db.Model):
    """Tabla de usuarios."""
    __tablename__ = 'usuarios'

    id = db.Column(db.String(50), primary_key=True)  # ID como string (compatibilidad)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    roles = db.Column(db.JSON, default=list)  # Lista de roles como JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convierte el modelo a dict."""
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'roles': self.roles,
        }

    def __repr__(self):
        return f'<Usuario {self.username}>'