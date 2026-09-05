"""Modelo de Nodo de Bloqueo (árbol de interruptores)."""
from core.db_sql import db


class NodoBloqueo(db.Model):
    __tablename__ = 'nodos_bloqueo'

    id = db.Column(db.String(50), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(20), default='apagado')
    descripcion = db.Column(db.Text, default='')
    padre_id = db.Column(db.String(50), db.ForeignKey('nodos_bloqueo.id'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'estado': self.estado,
            'descripcion': self.descripcion,
            'padre': self.padre_id,
        }