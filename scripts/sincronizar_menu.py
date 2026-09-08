"""
scripts/sincronizar_menu.py
===========================
Sincroniza el árbol de menús desde SQLite local a PostgreSQL de Render.
No necesita el archivo menu.json, lee directamente de la DB local.
"""
import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Asegurar que se ejecuta desde la raíz
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.chdir(project_root)


def leer_menus_sqlite():
    """Lee todos los menús de SQLite local preservando jerarquía."""
    from flask import Flask
    from core.db_sql import db as _db
    from core.models import Menu
    
    db_path = Path(project_root) / 'DataBase' / 'empresa.db'
    if not db_path.exists():
        print(f"❌ No existe la base de datos local: {db_path}")
        return []
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    _db.init_app(app)
    
    def construir_arbol(nodos_padre):
        resultado = []
        for nodo in nodos_padre:
            item = {
                'nombre': nodo.nombre,
                'emoji': nodo.emoji or '',
                'ruta': nodo.ruta or '',
                'ruta_jerarquia': nodo.ruta_jerarquia,
                'roles': nodo.roles or [],
                'submenues': construir_arbol(nodo.hijos)
            }
            resultado.append(item)
        return resultado
    
    with app.app_context():
        raices = Menu.query.filter_by(padre_id=None).order_by(Menu.id).all()
        arbol = construir_arbol(raices)
        total = Menu.query.count()
        print(f"📚 Leídos {total} menús de SQLite local ({len(arbol)} raíces)")
        return arbol


def escribir_menus_postgres(arbol):
    """Escribe el árbol de menús en PostgreSQL de Render."""
    load_dotenv()
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ No se encontró DATABASE_URL en .env")
        return
    
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    from flask import Flask
    from core.db_sql import db as _db
    from core.models import Menu
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    _db.init_app(app)
    
    def importar_arbol(items, padre_id=None, ruta_padre=''):
        count = 0
        for item in items:
            nombre = item.get('nombre', '')
            if not nombre:
                continue
            
            ruta_j = item.get('ruta_jerarquia', f"{ruta_padre}.{nombre}" if ruta_padre else nombre)
            
            nodo = Menu(
                nombre=nombre,
                emoji=item.get('emoji', ''),
                ruta=item.get('ruta', ''),
                ruta_jerarquia=ruta_j,
                padre_id=padre_id,
                roles=item.get('roles', [])
            )
            _db.session.add(nodo)
            _db.session.flush()  # Para obtener el ID
            count += 1
            
            submenues = item.get('submenues', [])
            if submenues:
                count += importar_arbol(submenues, nodo.id, ruta_j)
        
        return count
    
    with app.app_context():
        _db.create_all()
        
        # Limpiar menús actuales
        total_anterior = Menu.query.count()
        Menu.query.delete()
        _db.session.commit()
        print(f"🗑️  Eliminados {total_anterior} menús anteriores de Render")
        
        # Importar el árbol completo
        total_nuevo = importar_arbol(arbol)
        _db.session.commit()
        print(f"✅ Importados {total_nuevo} menús a Render")
        
        # Verificar
        raices = Menu.query.filter_by(padre_id=None).all()
        print(f"📂 Nodos raíz finales: {[m.nombre for m in raices]}")


def main():
    print("=" * 60)
    print("🔄 SINCRONIZANDO MENÚS: SQLite local → PostgreSQL Render")
    print("=" * 60)
    
    # 1. Leer de SQLite local
    arbol = leer_menus_sqlite()
    if not arbol:
        print("❌ No hay menús para sincronizar")
        return
    
    print(f"\n📋 Menús raíz locales:")
    for item in arbol:
        print(f"   {item['emoji']} {item['nombre']} ({len(item['submenues'])} submenús)")
    
    # 2. Escribir en PostgreSQL
    print()
    escribir_menus_postgres(arbol)
    
    print("\n" + "=" * 60)
    print("✅ SINCRONIZACIÓN COMPLETADA")
    print("=" * 60)
    print("💡 Ahora refresca tu app en Render y el menú debería aparecer.")


if __name__ == '__main__':
    main()