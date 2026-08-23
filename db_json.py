"""
Módulo genérico reutilizable para CRUD sobre archivos JSON
que contienen una lista de objetos con campo 'id'.

Uso:
    from db_json import JsonStore
    store = JsonStore("DataBase/time/dataTask.json")
    store.cargar() / store.guardar() / store.agregar() / store.editar() / store.eliminar()
"""
import json
import os


class JsonStore:
    def __init__(self, db_path):
        self.db_path = db_path

    def cargar(self):
        """Retorna la lista de items. Si no existe el archivo o está corrupto, retorna []."""
        if not os.path.exists(self.db_path):
            return []
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def guardar(self, items):
        """Persiste la lista completa. Crea el directorio si no existe."""
        directorio = os.path.dirname(self.db_path)
        if directorio:
            os.makedirs(directorio, exist_ok=True)
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=4, ensure_ascii=False)

    def agregar(self, item, defaults=None):
        """Agrega un item con ID autoincremental. 'defaults' setea campos si faltan."""
        items = self.cargar()
        item["id"] = max([e.get("id", 0) for e in items], default=0) + 1
        if defaults:
            for clave, valor in defaults.items():
                item.setdefault(clave, valor)
        items.append(item)
        self.guardar(items)
        return item

    def editar(self, item_id, nuevos_datos, ensure_fields=None):
        """Actualiza los campos de un item. 'ensure_fields' setea campos si faltan tras el update."""
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