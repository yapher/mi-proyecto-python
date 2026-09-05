"""Modelo de Estado de repuestos."""
from core.db_sql import db


class Estado(db.Model):
    __tablename__ = 'estados'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    emoji = db.Column(db.String(20), default='')

    def to_dict(self):
        return {'nombre': self.nombre, 'emoji': self.emoji}