"""
Cambia entre modo local (SQLite) y modo Render (PostgreSQL)
"""
import os
from pathlib import Path

def cambiar_modo(modo):
    env_file = Path('.env')
    env_off_file = Path('.env.off')
    
    if modo == 'local':
        if env_file.exists():
            env_file.rename(env_off_file)
            print("✅ Modo LOCAL activado (SQLite)")
            print("   Usando: DataBase/empresa.db")
        else:
            print("ℹ️  Ya estás en modo local")
            
    elif modo == 'render':
        if env_off_file.exists():
            env_off_file.rename(env_file)
            print("✅ Modo RENDER activado (PostgreSQL)")
            print("   Usando: Base de datos de Render")
        elif env_file.exists():
            print("ℹ️  Ya estás en modo Render")
        else:
            print("❌ No se encontró .env.off")
    else:
        # Mostrar modo actual
        if env_file.exists():
            print("📦 Modo actual: RENDER (PostgreSQL)")
        else:
            print("💻 Modo actual: LOCAL (SQLite)")
        print("\nUso:")
        print("  python scripts/cambiar_modo.py local   → Sin internet")
        print("  python scripts/cambiar_modo.py render  → Con internet")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        cambiar_modo(None)
    else:
        cambiar_modo(sys.argv[1])