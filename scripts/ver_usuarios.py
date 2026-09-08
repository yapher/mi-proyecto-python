"""
scripts/ver_usuarios.py
=======================
Muestra todos los usuarios de la base de datos.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from core.db_sql import db
from core.models import Usuario

with app.app_context():
    print('=' * 60)
    print('👤 USUARIOS EN LA BASE DE DATOS:')
    print('=' * 60)
    for u in Usuario.query.all():
        print(f'  ID:       {u.id}')
        print(f'  Username: "{u.username}"')
        print(f'  Password: "{u.password}"')
        print(f'  Roles:    {u.roles} (tipo: {type(u.roles).__name__})')
        print('-' * 60)