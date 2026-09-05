"""
Modelo de Evento (Agenda).
Equivalente a DataBase/time/agenda.json
"""
from core.db_sql import db
from datetime import datetime


class Evento(db.Model):
    """Tabla de eventos de la agenda."""
    __tablename__ = 'eventos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(200), nullable=False)
    fecha = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD
    descripcion = db.Column(db.Text, default='')
    email = db.Column(db.String(120), default='')
    realizado = db.Column(db.Boolean, default=False)
    prioridad = db.Column(db.String(10), default='media')  # alta, media, baja
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convierte el modelo a dict."""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'fecha': self.fecha,
            'descripcion': self.descripcion,
            'email': self.email,
            'realizado': self.realizado,
            'prioridad': self.prioridad,
        }

    def __repr__(self):
        return f'<Evento {self.id}: {self.titulo} ({self.fecha})>'