"""Configuración global de pytest - NO modifica archivos del proyecto."""
import pytest
import sys
import os
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch

# Agregar raíz del proyecto al path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ['TESTING'] = '1'


class MockUser:
    """Usuario simulado con todos los roles."""
    id = '1'
    username = 'admin'
    email = 'test@test.com'
    roles = ['admin', 'viewer', 'editor']
    is_authenticated = True
    is_active = True
    is_anonymous = False

    def get_id(self):
        return str(self.id)

    def has_role(self, role_name):
        return role_name in self.roles


@pytest.fixture(scope='session')
def app():
    """Crea la app Flask de prueba con DBs temporales."""
    from app import app as flask_app

    flask_app.config['TESTING'] = True
    flask_app.config['SECRET_KEY'] = 'test-secret-key'
    flask_app.config['WTF_CSRF_ENABLED'] = False

    # Crear directorio temporal para DBs
    tmp_dir = Path(tempfile.mkdtemp(prefix='pytest_empresa_'))
    
    # Crear subdirectorios y archivos vacíos
    (tmp_dir / 'time').mkdir(exist_ok=True)
    (tmp_dir / 'hogar').mkdir(exist_ok=True)
    (tmp_dir / 'dataOT').mkdir(exist_ok=True)
    (tmp_dir / 'dataRep').mkdir(exist_ok=True)
    (tmp_dir / 'Config').mkdir(exist_ok=True)

    # Archivos JSON vacíos para cada módulo
    (tmp_dir / 'time' / 'dataTask.json').write_text('[]', encoding='utf-8')
    (tmp_dir / 'time' / 'agenda.json').write_text('[]', encoding='utf-8')
    (tmp_dir / 'hogar' / 'GASTOS.json').write_text('[]', encoding='utf-8')
    (tmp_dir / 'hogar' / 'rubro.json').write_text('[]', encoding='utf-8')
    (tmp_dir / 'dataOT' / 'bloqueos.json').write_text('[]', encoding='utf-8')
    (tmp_dir / 'dataRep' / 'REPUESTOS.json').write_text('[]', encoding='utf-8')
    (tmp_dir / 'Config' / 'menu.json').write_text('[]', encoding='utf-8')

    # Parchear rutas de DB para que apunten al directorio temporal
    _patch_db_paths(tmp_dir)

    yield flask_app

    shutil.rmtree(tmp_dir, ignore_errors=True)


def _patch_db_paths(tmp_dir):
    """Reemplaza rutas de DB por temporales."""
    # Tareas
    try:
        from templates.Aplic.tareas.BackEnd import db_manager as tareas_db
        tareas_db.DB_PATH = str(tmp_dir / 'time' / 'dataTask.json')
    except Exception:
        pass

    # Agenda
    try:
        from templates.Aplic.agenda.BackEnd import db_manager as agenda_db
        agenda_db.DB_PATH = str(tmp_dir / 'time' / 'agenda.json')
    except Exception:
        pass

    # Pagos
    try:
        import templates.Aplic.pagos.BackEnd.pagos as pagos_mod
        pagos_mod.GASTOS = str(tmp_dir / 'hogar' / 'GASTOS.json')
        pagos_mod.GASTOSMES = str(tmp_dir / 'hogar')
        if hasattr(pagos_mod, 'DB_PATH'):
            pagos_mod.DB_PATH = Path(tmp_dir / 'hogar' / 'GASTOS.json')
    except Exception:
        pass

    # Bloqueos
    try:
        import templates.Aplic.gestiondebloqueos.BackEnd.gestion_de_bloqueos as bloqueos_mod
        bloqueos_mod.DB_PATH = Path(tmp_dir / 'dataOT' / 'bloqueos.json')
    except Exception:
        pass


@pytest.fixture
def client(app):
    """Cliente de test de Flask."""
    return app.test_client()


@pytest.fixture
def auth_client(app, client):
    """Cliente autenticado con MockUser."""
    with client.session_transaction() as sess:
        sess['_user_id'] = '1'
        sess['_fresh'] = True

    mock_user = MockUser()

    with patch('flask_login.utils._get_user', return_value=mock_user):
        yield client