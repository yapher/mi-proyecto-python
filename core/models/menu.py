"""Modelo de Menú (árbol jerárquico)."""
from core.db_sql import db
from datetime import datetime


class Menu(db.Model):
    __tablename__ = 'menus'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    emoji = db.Column(db.String(20), default='')
    ruta = db.Column(db.String(255), default='')
    ruta_jerarquia = db.Column(db.String(500), unique=True, nullable=False)
    padre_id = db.Column(db.Integer, db.ForeignKey('menus.id'), nullable=True)
    roles = db.Column(db.JSON, default=list)  # ✅ NUEVO: Lista de roles
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación recursiva (padre → hijos)
    hijos = db.relationship(
        'Menu',
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
            'padre_id': self.padre_id,
            'roles': self.roles or [],  # ✅ NUEVO
        }
        if include_hijos:
            data['submenues'] = [h.to_dict(include_hijos=True) for h in self.hijos]
        return data

    def __repr__(self):
        return f'<Menu {self.ruta_jerarquia}>'