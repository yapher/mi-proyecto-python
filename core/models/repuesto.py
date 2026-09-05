"""Modelo de Repuesto (identificado por código único)."""
from core.db_sql import db
from datetime import datetime
import json


class Repuesto(db.Model):
    __tablename__ = 'repuestos'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(100), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(255), nullable=False)
    cantidad = db.Column(db.Integer, default=0)
    equipo = db.Column(db.String(255), default='')
    imagen = db.Column(db.String(255), default='')
    fecha_creacion = db.Column(db.String(20), default='')
    fecha_fin = db.Column(db.String(20), default='')
    link = db.Column(db.String(500), default='')
    estado = db.Column(db.String(50), default='')
    ruta_jerarquia_json = db.Column('ruta_jerarquia', db.Text, default='[]')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        try:
            rutas = json.loads(self.ruta_jerarquia_json or '[]')
        except Exception:
            rutas = []
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'cantidad': self.cantidad,
            'equipo': self.equipo,
            'imagen': self.imagen,
            'fecha_creacion': self.fecha_creacion,
            'fecha_fin': self.fecha_fin,
            'link': self.link,
            'estado': self.estado,
            'ruta_jerarquia': rutas,
        }