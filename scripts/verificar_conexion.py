"""
Verifica si hay conexión a la base de datos de Render
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

def verificar_conexion():
    load_dotenv()
    db_url = os.getenv('DATABASE_URL')
    
    if not db_url:
        print("❌ No hay DATABASE_URL configurada")
        print("   Estás en modo LOCAL (SQLite)")
        return False
    
    try:
        from app import app
        from core.models import Usuario
        
        with app.app_context():
            count = Usuario.query.count()
            print(f"✅ Conexión exitosa a PostgreSQL de Render")
            print(f"   Usuarios en DB: {count}")
            return True
    except Exception as e:
        print(f"❌ Error al conectar con Render: {e}")
        print("   Probablemente no hay internet")
        return False

if __name__ == '__main__':
    verificar_conexion()