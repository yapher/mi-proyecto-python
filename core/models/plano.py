"""Modelo de Plano (documentos PDF por ubicación técnica)."""
from core.db_sql import db
from datetime import datetime


class Plano(db.Model):
    __tablename__ = 'planos'

    id = db.Column(db.Integer, primary_key=True)

    # Texto legacy (snapshot). La relación real es ubicacion_id.
    nombre_linea_legacy = db.Column('nombre_linea', db.String(100), nullable=False, index=True)

    # ✅ NUEVO: relación real con la ubicación técnica
    ubicacion_id = db.Column(
        db.Integer,
        db.ForeignKey('ubicaciones.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    ubicacion = db.relationship(
        'Ubicacion',
        lazy='joined',
        backref=db.backref('planos', lazy='select')
    )

    # ✅ NUEVO: carpeta real en disco (no cambia aunque se renombre la ubicación)
    carpeta = db.Column(db.String(100), nullable=True)

    descripcion = db.Column(db.Text, default='')
    nombre_archivo = db.Column(db.String(255), nullable=False)
    fecha_carga = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_carga = db.Column(db.String(80), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('nombre_linea', 'nombre_archivo', name='uq_plano_linea_archivo'),
    )

    @property
    def nombre_linea(self):
        """Ruta actual de la ubicación (cambia sola si se renombra)."""
        if self.ubicacion is not None:
            return self.ubicacion.ruta_jerarquia
        return self.nombre_linea_legacy or ''

    @nombre_linea.setter
    def nombre_linea(self, valor):
        self.nombre_linea_legacy = valor or ''

    @property
    def carpeta_disco(self):
        return self.carpeta or self.nombre_linea_legacy or ''

    def to_dict(self):
        return {
            'id': self.id,
            'nombre_linea': self.nombre_linea,
            'descripcion': self.descripcion,
            'nombre_archivo': self.nombre_archivo,
            'fecha_carga': self.fecha_carga.isoformat() if self.fecha_carga else '',
            'usuario_carga': self.usuario_carga,
            # Compatibilidad con los templates existentes
            'carpeta': self.carpeta_disco,
            'archivo': self.nombre_archivo,
        }