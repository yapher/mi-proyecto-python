# core/db_json.py
"""
Módulo genérico reutilizable para CRUD sobre archivos JSON.
Soporta:
  - Listas de objetos con campo 'id' autoincremental
  - Bloqueo de archivos para evitar corrupción
  - Backups automáticos antes de escribir
"""
import json
import os
import shutil
from datetime import datetime
from contextlib import contextmanager


class JsonStore:
    """
    Almacén JSON genérico con operaciones CRUD.

    Uso:
        store = JsonStore("data/agenda/eventos.json")
        items = store.cargar()
        store.agregar({"titulo": "Reunión", "fecha": "2026-08-25"})
    """

    def __init__(self, db_path, backup=False):
        self.db_path = db_path
        self.backup = backup

    # ------------------------------------------------------------------
    # Operaciones básicas
    # ------------------------------------------------------------------
    def cargar(self):
        """Retorna la lista de items. Si no existe o está corrupto, retorna []."""
        if not os.path.exists(self.db_path):
            return []
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def guardar(self, items):
        """Persiste la lista completa. Crea directorio si no existe."""
        directorio = os.path.dirname(self.db_path)
        if directorio:
            os.makedirs(directorio, exist_ok=True)

        # Backup opcional
        if self.backup and os.path.exists(self.db_path):
            self._crear_backup()

        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=4, ensure_ascii=False)

    def agregar(self, item, defaults=None):
        """
        Agrega un item con ID autoincremental.
        'defaults' setea campos si faltan.
        """
        items = self.cargar()
        item["id"] = max([e.get("id", 0) for e in items], default=0) + 1
        if defaults:
            for clave, valor in defaults.items():
                item.setdefault(clave, valor)
        items.append(item)
        self.guardar(items)
        return item

    def editar(self, item_id, nuevos_datos, ensure_fields=None):
        """Actualiza los campos de un item por ID."""
        items = self.cargar()
        for item in items:
            if item.get("id") == item_id:
                item.update(nuevos_datos)
                if ensure_fields:
                    for clave, valor in ensure_fields.items():
                        item.setdefault(clave, valor)
                break
        self.guardar(items)

    def eliminar(self, item_id):
        """Elimina un item por ID."""
        items = self.cargar()
        items = [e for e in items if e.get("id") != item_id]
        self.guardar(items)

    def buscar(self, **criterios):
        """Busca items que cumplan todos los criterios."""
        items = self.cargar()
        resultados = []
        for item in items:
            if all(item.get(k) == v for k, v in criterios.items()):
                resultados.append(item)
        return resultados

    def buscar_uno(self, **criterios):
        """Busca el primer item que cumpla los criterios."""
        resultados = self.buscar(**criterios)
        return resultados[0] if resultados else None

    def filtrar(self, predicate):
        """Filtra items usando una función predicate."""
        return [item for item in self.cargar() if predicate(item)]

    def contar(self):
        """Retorna la cantidad de items."""
        return len(self.cargar())

    def existe(self, item_id):
        """Verifica si existe un item con el ID dado."""
        return any(e.get("id") == item_id for e in self.cargar())

    def limpiar(self):
        """Elimina todos los items."""
        self.guardar([])

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def _crear_backup(self):
        """Crea un backup con timestamp."""
        if not os.path.exists(self.db_path):
            return
        backup_dir = os.path.join(os.path.dirname(self.db_path), "backups")
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre = f"{os.path.basename(self.db_path)}.{timestamp}.bak"
        shutil.copy2(self.db_path, os.path.join(backup_dir, nombre))

    @contextmanager
    def transaccion(self):
        """
        Context manager para operaciones atómicas.
        Si hay excepción, no se guardan los cambios.
        """
        items = self.cargar()
        try:
            yield items
            self.guardar(items)
        except Exception:
            raise