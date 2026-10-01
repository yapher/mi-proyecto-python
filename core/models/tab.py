"""Modelo de Tab (pestañas de repuestos)."""
from core.db_sql import db


class Tab(db.Model):
    __tablename__ = 'tabs'

    id = db.Column(db.Integer, primary_key=True)
    tab_id = db.Column(db.String(255), unique=True, nullable=False)

    # Texto legacy del título: solo se usa si la pestaña no tiene ubicación vinculada
    title_legacy = db.Column('title', db.String(255), nullable=False)

    ubicacion_id = db.Column(
        db.Integer,
        db.ForeignKey('ubicaciones.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    ubicacion = db.relationship(
        'Ubicacion',
        lazy='joined',
        backref=db.backref('tabs', lazy='select')
    )

    ruta_jerarquia_legacy = db.Column('ruta_jerarquia', db.String(500), default='')
    sanitized_id = db.Column(db.String(255), default='')

    @property
    def ruta_jerarquia(self):
        """Ruta actual de la ubicación (cambia sola si se renombra)."""
        if self.ubicacion is not None:
            return self.ubicacion.ruta_jerarquia
        return self.ruta_jerarquia_legacy or ''

    @ruta_jerarquia.setter
    def ruta_jerarquia(self, valor):
        self.ruta_jerarquia_legacy = valor or ''

    @property
    def title(self):
        """Título calculado: sigue al nombre/ruta de la ubicación."""
        if self.ubicacion is not None:
            etiqueta = self.ubicacion.ruta or self.ubicacion.nombre
            return f"{etiqueta} 🏬"
        return self.title_legacy or ''

    @title.setter
    def title(self, valor):
        self.title_legacy = valor or ''

    def to_dict(self):
        return {
            'id': self.tab_id,
            'title': self.title,
            'ruta_jerarquia': self.ruta_jerarquia,
            'sanitized_id': self.sanitized_id,
        }