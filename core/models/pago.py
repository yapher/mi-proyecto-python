"""Modelo de Pago/Gasto."""
from core.db_sql import db
from datetime import datetime


class Pago(db.Model):
    __tablename__ = 'pagos'

    id = db.Column(db.Integer, primary_key=True)
    rubro = db.Column(db.String(100), default='', index=True)
    descripcion = db.Column(db.String(255), default='')
    importe = db.Column(db.Float, default=0)
    tipo = db.Column(db.String(50), default='único')
    cuotas = db.Column(db.Integer, default=1)
    cuota_numero = db.Column(db.Integer, nullable=True)
    cuota_total = db.Column(db.Integer, nullable=True)
    vencimiento = db.Column(db.String(20), default='', index=True)
    pagado = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'rubro': self.rubro,
            'descripcion': self.descripcion,
            'importe': self.importe,
            'tipo': self.tipo,
            'cuotas': self.cuotas,
            'cuota_numero': self.cuota_numero,
            'cuota_total': self.cuota_total,
            'vencimiento': self.vencimiento,
            'pagado': self.pagado,
        }