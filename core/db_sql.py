"""
core/db_sql.py
==============
Capa de abstracción SQL que mantiene la misma API que JsonStore.
Permite migrar gradualmente de JSON a PostgreSQL sin romper el código existente.

Uso:
    from core.db_sql import SQLStore
    store = SQLStore('tarea')  # usa el modelo Tarea
    items = store.cargar()
    store.agregar({'titulo': 'Nueva tarea', 'fecha': '2026-09-05'})
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect

# Instancia global de SQLAlchemy (se inicializa en app.py)
db = SQLAlchemy()


class SQLStore:
    """
    Store SQL que imita la API de JsonStore.
    Permite migrar módulo por módulo sin romper el código existente.
    """

    def __init__(self, model_class):
        """
        Args:
            model_class: Clase del modelo SQLAlchemy (ej: Tarea, Evento)
        """
        self.model = model_class

    def cargar(self):
        """Retorna todos los items como lista de dicts."""
        items = self.model.query.all()
        return [item.to_dict() for item in items]

    def guardar(self, items):
        """
        Reemplaza TODOS los items (equivalente a JsonStore.guardar).
        Útil para migración, pero en producción es mejor usar agregar/editar.
        """
        # Eliminar todos los existentes
        self.model.query.delete()
        db.session.commit()

        # Insertar los nuevos
        for item_data in items:
            item = self.model(**item_data)
            db.session.add(item)
        db.session.commit()

    def agregar(self, item_data, defaults=None):
        """Agrega un item con ID autoincremental."""
        if defaults:
            for clave, valor in defaults.items():
                item_data.setdefault(clave, valor)

        item = self.model(**item_data)
        db.session.add(item)
        db.session.commit()
        return item.to_dict()

    def editar(self, item_id, nuevos_datos, ensure_fields=None):
        """Actualiza los campos de un item por ID."""
        item = self.model.query.get(item_id)
        if not item:
            return False

        for clave, valor in nuevos_datos.items():
            if hasattr(item, clave):
                setattr(item, clave, valor)

        if ensure_fields:
            for clave, valor in ensure_fields.items():
                if not getattr(item, clave, None):
                    setattr(item, clave, valor)

        db.session.commit()
        return True

    def eliminar(self, item_id):
        """Elimina un item por ID."""
        item = self.model.query.get(item_id)
        if item:
            db.session.delete(item)
            db.session.commit()
            return True
        return False

    def buscar(self, **criterios):
        """Busca items que cumplan todos los criterios."""
        query = self.model.query
        for clave, valor in criterios.items():
            if hasattr(self.model, clave):
                query = query.filter(getattr(self.model, clave) == valor)
        return [item.to_dict() for item in query.all()]

    def buscar_uno(self, **criterios):
        """Busca el primer item que cumpla los criterios."""
        resultados = self.buscar(**criterios)
        return resultados[0] if resultados else None

    def filtrar(self, predicate):
        """Filtra items usando una función predicate."""
        items = self.cargar()
        return [item for item in items if predicate(item)]

    def contar(self):
        """Retorna la cantidad de items."""
        return self.model.query.count()

    def existe(self, item_id):
        """Verifica si existe un item con el ID dado."""
        return self.model.query.get(item_id) is not None

    def limpiar(self):
        """Elimina todos los items."""
        self.model.query.delete()
        db.session.commit()


def init_db(app):
    """
    Inicializa la base de datos con la app Flask.
    Crea las tablas si no existen.
    """
    db.init_app(app)
    with app.app_context():
        # Importar todos los modelos para que se registren
        from core.models import tarea, evento, usuario  # noqa
        db.create_all()