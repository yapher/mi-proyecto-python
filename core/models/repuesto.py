"""Modelo de Repuesto (identificado por código único)."""
from core.db_sql import db
from datetime import datetime
import json

# ✅ NUEVO: tabla intermedia repuesto <-> ubicación técnica (muchos a muchos)
repuesto_ubicacion = db.Table(
    'repuesto_ubicacion',
    db.Column('repuesto_id', db.Integer,
              db.ForeignKey('repuestos.id', ondelete='CASCADE'), primary_key=True),
    db.Column('ubicacion_id', db.Integer,
              db.ForeignKey('ubicaciones.id', ondelete='CASCADE'), primary_key=True),
)


class Repuesto(db.Model):
    __tablename__ = 'repuestos'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(100), unique=True, nullable=False, index=True)
    nombre = db.Column(db.Text, nullable=False)
    cantidad = db.Column(db.Integer, default=0)

    # Texto legacy del almacén (la relación real es almacen_id)
    equipo_legacy = db.Column('equipo', db.Text, default='')
    almacen_id = db.Column(
        db.Integer,
        db.ForeignKey('almacenes.id', ondelete='SET NULL'),
        nullable=True
    )
    almacen = db.relationship(
        'Almacen',
        lazy='joined',
        backref=db.backref('repuestos', lazy='select')
    )

    # ✅ NUEVO: ubicaciones técnicas como relación real
    ubicaciones = db.relationship(
        'Ubicacion',
        secondary=repuesto_ubicacion,
        lazy='selectin',   # una sola consulta extra para todos los repuestos
        backref=db.backref('repuestos', lazy='select')
    )

    imagen = db.Column(db.String(255), default='')
    fecha_creacion = db.Column(db.String(20), default='')
    fecha_fin = db.Column(db.String(20), default='')
    link = db.Column(db.Text, default='')
    estado = db.Column(db.String(50), default='')
    comentario = db.Column(db.Text, default='')

    # Ahora guarda SOLO rutas "sueltas" que no coinciden con ninguna ubicación
    ruta_jerarquia_json = db.Column('ruta_jerarquia', db.Text, default='[]')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def equipo(self):
        if self.almacen is not None:
            return self.almacen.ruta_jerarquia
        return self.equipo_legacy or ''

    @equipo.setter
    def equipo(self, valor):
        self.equipo_legacy = valor or ''

    def rutas_ubicacion(self):
        """Rutas actuales (se actualizan solas si se renombra una ubicación)."""
        rutas = sorted(u.ruta_jerarquia for u in self.ubicaciones)
        try:
            legacy = json.loads(self.ruta_jerarquia_json or '[]')
        except Exception:
            legacy = []
        if isinstance(legacy, list):
            for x in legacy:
                if x and x not in rutas:
                    rutas.append(x)
        return rutas

    def to_dict(self):
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
            'comentario': self.comentario or '',
            'ruta_jerarquia': self.rutas_ubicacion(),
        }