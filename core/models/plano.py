"""Modelo de Plano (documentos PDF por línea/ubicación)."""
from core.db_sql import db
from datetime import datetime


class Plano(db.Model):
    __tablename__ = 'planos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_linea = db.Column(db.String(100), nullable=False, index=True)
    descripcion = db.Column(db.Text, default='')
    nombre_archivo = db.Column(db.String(255), nullable=False)
    fecha_carga = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_carga = db.Column(db.String(80), nullable=False)
    
    # Constraint único combinado (nombre_linea + nombre_archivo)
    __table_args__ = (
        db.UniqueConstraint('nombre_linea', 'nombre_archivo', name='uq_plano_linea_archivo'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'nombre_linea': self.nombre_linea,
            'descripcion': self.descripcion,
            'nombre_archivo': self.nombre_archivo,
            'fecha_carga': self.fecha_carga.isoformat() if self.fecha_carga else '',
            'usuario_carga': self.usuario_carga,
            # ✅ Compatibilidad con template existente: 'carpeta' = 'nombre_linea'
            'carpeta': self.nombre_linea,
            'archivo': self.nombre_archivo,
        }