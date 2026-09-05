"""Modelo de Rubro (árbol jerárquico)."""
from core.db_sql import db
from datetime import datetime


class Rubro(db.Model):
    __tablename__ = 'rubros'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    emoji = db.Column(db.String(20), default='')
    ruta = db.Column(db.String(255), default='')
    ruta_jerarquia = db.Column(db.String(500), unique=True, nullable=False)
    padre_id = db.Column(db.Integer, db.ForeignKey('rubros.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    hijos = db.relationship(
        'Rubro',
        backref=db.backref('padre', remote_side=[id]),
        lazy='select',
        cascade='all, delete-orphan'
    )

    def to_dict(self, include_hijos=False):
        data = {
            'id': self.id,
            'nombre': self.nombre,
            'emoji': self.emoji,
            'ruta': self.ruta,
            'ruta_jerarquia': self.ruta_jerarquia,
        }
        if include_hijos:
            data['submenues'] = [h.to_dict(include_hijos=True) for h in self.hijos]
        return data