"""Modelo de Tab (pestañas de repuestos)."""
from core.db_sql import db


class Tab(db.Model):
    __tablename__ = 'tabs'

    id = db.Column(db.Integer, primary_key=True)
    tab_id = db.Column(db.String(255), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    ruta_jerarquia = db.Column(db.String(500), default='')
    sanitized_id = db.Column(db.String(255), default='')

    def to_dict(self):
        return {
            'id': self.tab_id,
            'title': self.title,
            'ruta_jerarquia': self.ruta_jerarquia,
            'sanitized_id': self.sanitized_id,
        }