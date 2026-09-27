"""
scripts/agregar_campo_comentario.py
====================================
Migración: agrega la columna 'comentario' a la tabla 'repuestos'.

Ejecutar UNA sola vez:
    python scripts/agregar_campo_comentario.py

Funciona con SQLite local y PostgreSQL de Render.
Si la columna ya existe, no hace nada.
"""
import sys
import os

# Asegurar que se ejecuta desde la raíz del proyecto
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.chdir(project_root)

from app import app
from core.db_sql import db
from sqlalchemy import text, inspect

def migrar():
    with app.app_context():
        inspector = inspect(db.engine)
        columnas = [col['name'] for col in inspector.get_columns('repuestos')]

        if 'comentario' in columnas:
            print("✅ La columna 'comentario' ya existe. No se requiere migración.")
            return

        print("🔧 Agregando columna 'comentario' a la tabla 'repuestos'...")

        # SQLite y PostgreSQL usan la misma sintaxis para ALTER TABLE ADD COLUMN
        db.session.execute(text(
            "ALTER TABLE repuestos ADD COLUMN comentario TEXT DEFAULT ''"
        ))
        db.session.commit()

        print("✅ Columna 'comentario' agregada correctamente.")

if __name__ == '__main__':
    migrar()