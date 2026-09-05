"""
core/migrator.py
================
Script para migrar datos de JSON a PostgreSQL/SQLite.
Uso:
    python -m core.migrator
"""
import json
import os
from core.db_sql import db
from core.models import Tarea, Evento, Usuario


def migrar_tareas():
    """Migra tareas desde dataTask.json."""
    ruta = 'DataBase/time/dataTask.json'
    if not os.path.exists(ruta):
        print(f"⚠️  No existe {ruta}")
        return 0

    with open(ruta, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Limpiar tabla
    Tarea.query.delete()
    db.session.commit()

    # Insertar datos
    for item in data:
        tarea = Tarea(
            titulo=item.get('titulo', ''),
            fecha=item.get('fecha', ''),
            descripcion=item.get('descripcion', '')
        )
        db.session.add(tarea)

    db.session.commit()
    print(f"✅ Migradas {len(data)} tareas")
    return len(data)


def migrar_eventos():
    """Migra eventos desde agenda.json."""
    ruta = 'DataBase/time/agenda.json'
    if not os.path.exists(ruta):
        print(f"⚠️  No existe {ruta}")
        return 0

    with open(ruta, 'r', encoding='utf-8') as f:
        data = json.load(f)

    Evento.query.delete()
    db.session.commit()

    for item in data:
        evento = Evento(
            titulo=item.get('titulo', ''),
            fecha=item.get('fecha', ''),
            descripcion=item.get('descripcion', ''),
            email=item.get('email', ''),
            realizado=item.get('realizado', False),
            prioridad=item.get('prioridad', 'media')
        )
        db.session.add(evento)

    db.session.commit()
    print(f"✅ Migrados {len(data)} eventos")
    return len(data)


def migrar_usuarios():
    """Migra usuarios desde users.json."""
    ruta = 'users.json'
    if not os.path.exists(ruta):
        print(f"⚠️  No existe {ruta}")
        return 0

    with open(ruta, 'r', encoding='utf-8') as f:
        data = json.load(f)

    Usuario.query.delete()
    db.session.commit()

    for item in data:
        usuario = Usuario(
            id=str(item.get('id', '')),
            username=item.get('username', ''),
            password=item.get('password', ''),
            roles=item.get('roles', [])
        )
        db.session.add(usuario)

    db.session.commit()
    print(f"✅ Migrados {len(data)} usuarios")
    return len(data)


def migrar_todo():
    """Ejecuta todas las migraciones."""
    print("🚀 Iniciando migración de datos...")
    print("=" * 50)

    total = 0
    total += migrar_usuarios()
    total += migrar_eventos()
    total += migrar_tareas()

    print("=" * 50)
    print(f"✅ Migración completada: {total} registros totales")


if __name__ == '__main__':
    from app import app
    with app.app_context():
        migrar_todo()