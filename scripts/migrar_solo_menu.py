"""
scripts/migrar_solo_menu.py
===========================
Migra SOLO el menú desde JSON a la base de datos actual.
IMPRIME la URL de la DB para verificar que sea Render.
"""
import sys
import os
import json
from dotenv import load_dotenv

# 1. Forzar carga de .env
load_dotenv()

# 2. Configurar rutas
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from core.db_sql import db
from core.models import Menu

def migrar_menu():
    # Mostrar a qué DB nos estamos conectando
    db_url = os.environ.get('DATABASE_URL', 'NO ENCONTRADA (Usando SQLite local)')
    print(f"🔌 CONECTANDO A: {db_url[:50]}...")
    
    ruta = 'DataBase/Config/menu.json'
    if not os.path.exists(ruta):
        print(f"❌ ERROR: No existe {ruta}")
        print("   Asegúrate de haber restaurado los archivos JSON desde Git.")
        return
    
    with open(ruta, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📂 Leyendo {ruta}: {len(data)} nodos raíz encontrados")
    
    with app.app_context():
        # Limpiar menús existentes
        Menu.query.delete()
        db.session.commit()
        print("🗑️  Menús anteriores eliminados de la DB")
        
        def _migrar_nodos(items, padre_id=None, ruta_padre=''):
            count = 0
            for item in items:
                nombre = item.get('nombre', '')
                if not nombre:
                    continue
                
                ruta_j = f"{ruta_padre}.{nombre}" if ruta_padre else nombre
                
                nodo = Menu(
                    nombre=nombre,
                    emoji=item.get('emoji', ''),
                    ruta=item.get('ruta', ''),
                    ruta_jerarquia=ruta_j,
                    padre_id=padre_id,
                    roles=item.get('roles', [])
                )
                db.session.add(nodo)
                db.session.flush()  # Para obtener el ID
                count += 1
                
                hijos = item.get('submenues', [])
                if hijos:
                    count += _migrar_nodos(hijos, padre_id=nodo.id, ruta_padre=ruta_j)
            
            return count
        
        total = _migrar_nodos(data)
        db.session.commit()
        
        print(f"✅ Migrados {total} nodos de menú a la base de datos")
        print(f"📊 Total de menús en la DB AHORA: {Menu.query.count()}")

if __name__ == '__main__':
    migrar_menu()