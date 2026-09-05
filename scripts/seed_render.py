"""
scripts/seed_render.py
======================
Puebla la base de datos con datos iniciales para Render.
Se ejecuta automáticamente si la DB está vacía.
"""
from core.db_sql import db
from core.models import Usuario, Menu, Estado, Tab, NodoBloqueo


def seed_usuarios():
    """Crea usuarios por defecto si no existen."""
    if Usuario.query.count() > 0:
        print("✅ Usuarios ya existen, saltando seed")
        return 0

    usuarios_default = [
        {
            'id': '1',
            'username': 'admin',
            'password': 'admin123',
            'roles': ['admin', 'editor', 'viewer']
        },
        {
            'id': '2',
            'username': 'viewer',
            'password': 'viewer123',
            'roles': ['viewer']
        }
    ]

    for u in usuarios_default:
        usuario = Usuario(**u)
        db.session.add(usuario)

    db.session.commit()
    print(f"✅ Seed: {len(usuarios_default)} usuarios creados")
    return len(usuarios_default)


def seed_menu():
    """Crea menú inicial si no existe."""
    if Menu.query.count() > 0:
        print("✅ Menú ya existe, saltando seed")
        return 0

    # Menú básico inicial
    menu_inicial = [
        {
            'nombre': 'Inicio',
            'emoji': '🏠',
            'ruta': '/',
            'ruta_jerarquia': 'Inicio',
            'padre_id': None,
            'roles': []
        },
        {
            'nombre': 'Administración',
            'emoji': '⚙️',
            'ruta': '',
            'ruta_jerarquia': 'Administración',
            'padre_id': None,
            'roles': ['admin']
        }
    ]

    for m in menu_inicial:
        menu = Menu(**m)
        db.session.add(menu)

    db.session.commit()
    print(f"✅ Seed: {len(menu_inicial)} nodos de menú creados")
    return len(menu_inicial)


def seed_estados():
    """Crea estados de repuestos por defecto."""
    if Estado.query.count() > 0:
        print("✅ Estados ya existen, saltando seed")
        return 0

    estados_default = [
        {'nombre': 'Disponible', 'emoji': '✅'},
        {'nombre': 'En espera', 'emoji': '⏳'},
        {'nombre': 'No disponible', 'emoji': '❌'},
        {'nombre': 'Sin código', 'emoji': '🔍'},
        {'nombre': 'Descontinuado', 'emoji': '🚫'},
        {'nombre': 'Actualizar código', 'emoji': '🔄'},
        {'nombre': 'Otros', 'emoji': '📦'}
    ]

    for e in estados_default:
        estado = Estado(**e)
        db.session.add(estado)

    db.session.commit()
    print(f"✅ Seed: {len(estados_default)} estados creados")
    return len(estados_default)


def seed_nodo_bloqueo():
    """Crea nodo raíz de bloqueos si no existe."""
    if NodoBloqueo.query.count() > 0:
        print("✅ Nodos de bloqueo ya existen, saltando seed")
        return 0

    nodo = NodoBloqueo(
        id='1',
        nombre='Nodo Raíz',
        estado='apagado',
        descripcion='',
        padre_id=None
    )
    db.session.add(nodo)
    db.session.commit()
    print("✅ Seed: Nodo raíz de bloqueos creado")
    return 1


def seed_todo():
    """Ejecuta todos los seeds."""
    print("🌱 Ejecutando seed de datos iniciales...")
    total = 0
    total += seed_usuarios()
    total += seed_menu()
    total += seed_estados()
    total += seed_nodo_bloqueo()
    print(f"✅ Seed completado: {total} registros creados")
    return total


if __name__ == '__main__':
    from app import app
    with app.app_context():
        db.create_all()
        seed_todo()