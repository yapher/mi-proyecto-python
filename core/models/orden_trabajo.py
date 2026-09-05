"""Modelo de Orden de Trabajo."""
from core.db_sql import db
from datetime import datetime


class OrdenTrabajo(db.Model):
    __tablename__ = 'ordenes_trabajo'

    id = db.Column(db.Integer, primary_key=True)
    numero_orden = db.Column(db.String(50), index=True)
    descripcion = db.Column(db.Text, default='')
    inicio_extremo = db.Column(db.String(20), default='')
    fin_extremo = db.Column(db.String(20), default='')
    equipo_ut = db.Column(db.String(100), default='')
    descripcion_equipo = db.Column(db.Text, default='')
    estado = db.Column(db.String(50), default='')
    revision = db.Column(db.String(50), default='')
    fecha_carga = db.Column(db.Date, default=datetime.utcnow)
    archivo_origen = db.Column(db.String(100), default='', index=True)

    def to_dict(self):
        return {
            'numero_orden': self.numero_orden,
            'descripcion': self.descripcion,
            'inicio_extremo': self.inicio_extremo,
            'fin_extremo': self.fin_extremo,
            'equipo_ut': self.equipo_ut,
            'descripcion_equipo': self.descripcion_equipo,
            'estado': self.estado,
            'revision': self.revision,
        }