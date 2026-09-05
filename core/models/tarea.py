"""
Modelo de Tarea.
Equivalente a DataBase/time/dataTask.json
"""
from core.db_sql import db
from datetime import datetime


class Tarea(db.Model):
    """Tabla de tareas."""
    __tablename__ = 'tareas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(200), nullable=False)
    fecha = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD
    descripcion = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convierte el modelo a dict (compatible con JsonStore)."""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'fecha': self.fecha,
            'descripcion': self.descripcion,
        }

    def __repr__(self):
        return f'<Tarea {self.id}: {self.titulo}>'