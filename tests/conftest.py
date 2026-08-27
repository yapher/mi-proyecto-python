# tests/conftest.py
"""
Configuración global de pytest.
Define los fixtures 'app', 'client' y 'auth_client' que usan TODOS los tests.
"""
import sys
import os
import json
from pathlib import Path

# ============================================================
# 1. AGREGAR RAÍZ DEL PROYECTO AL PYTHONPATH
# ============================================================
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest
from flask import Flask
from flask_login import UserMixin, login_user


# ============================================================
# 2. FIXTURE: app (Flask de prueba)
# ============================================================
@pytest.fixture
def app(tmp_path, monkeypatch):
    """
    Crea una app Flask mínima configurada para testing.
    """
    # Forzamos rutas absolutas para que Flask encuentre static/templates sin depender del CWD
    app = Flask(
        "test_app",
        root_path=str(ROOT_DIR),
        template_folder=str(ROOT_DIR / "templates"),
        static_folder=str(ROOT_DIR / "static"),
        static_url_path="/static"
    )
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key-for-pytest"
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SERVER_NAME"] = "localhost"

    # ============================================================
    # Redirigir archivos JSON a tmp_path (no tocar datos reales)
    # ============================================================
    db_dir = tmp_path / "DataBase"
    db_dir.mkdir(exist_ok=True)
    (db_dir / "Config").mkdir(exist_ok=True)
    (db_dir / "time").mkdir(exist_ok=True)
    (db_dir / "dataOT").mkdir(exist_ok=True)
    (db_dir / "dataRep").mkdir(exist_ok=True)
    (db_dir / "hogar").mkdir(exist_ok=True)
    (db_dir / "planos").mkdir(exist_ok=True)
    
    # Crear también Database (por si algún módulo usa mayúscula/minúscula incorrecta)
    db_dir_alt = tmp_path / "Database"
    db_dir_alt.mkdir(exist_ok=True)
    (db_dir_alt / "planos").mkdir(exist_ok=True)

    # Lista de TODOS los archivos JSON que las apps pueden intentar leer
    json_files = [
        db_dir / "Config" / "menu.json",
        db_dir / "time" / "agenda.json",
        db_dir / "time" / "dataTask.json",
        db_dir / "dataRep" / "almacenes.json",
        db_dir / "dataRep" / "ubicacion_tecnica.json",
        db_dir / "dataRep" / "estados.json",
        db_dir / "dataRep" / "REPUESTOS.json",
        db_dir / "hogar" / "GASTOS.json",
        db_dir / "hogar" / "rubro.json",       # <-- Corregido: rubro.json va en hogar
        db_dir / "tabs.json",
        db_dir / "planos.json",
        db_dir_alt / "planos" / "nodo.json",   # <-- Para gestion_de_bloqueos
    ]
    
    for jf in json_files:
        jf.parent.mkdir(parents=True, exist_ok=True)
        if not jf.exists():
            if jf.name == "REPUESTOS.json":
                # Pre-poblamos con un repuesto que coincida con el tab de prueba
                jf.write_text(json.dumps([{
                    "codigo": "TEST001",
                    "nombre": "Repuesto de Prueba",
                    "cantidad": 10,
                    "equipo": "Planta Principal",
                    "ruta_jerarquia": ["Planta Principal"],
                    "fecha_creacion": "2026-08-28",
                    "estado": "Disponible",
                    "imagen": "test.png"
                }]), encoding="utf-8")
            elif jf.name == "tabs.json":
                # Pre-poblamos con un tab que coincida con el repuesto de prueba
                jf.write_text(json.dumps([{
                    "id": "Planta Principal",
                    "title": "Planta Principal",
                    "ruta_jerarquia": "Planta Principal",
                    "sanitized_id": "Planta_Principal"
                }]), encoding="utf-8")
            else:
                jf.write_text("[]", encoding="utf-8")

    # Crear users.json en tmp_path (para auth.login)
    users_file = tmp_path / "users.json"
    users_file.write_text(json.dumps([{
        "id": "1",
        "username": "testuser",
        "password": "testpass",
        "roles": ["admin", "viewer", "editor"]
    }]), encoding="utf-8")

    # Cambiar directorio de trabajo a tmp_path para que las rutas relativas apunten aquí
    monkeypatch.chdir(tmp_path)

    # ============================================================
    # Parchear la carga de usuarios para que SIEMPRE haya un usuario de prueba
    # ============================================================
    import auth.login
    mock_users = [{
        "id": "1",
        "username": "testuser",
        "password": "testpass",
        "roles": ["admin", "viewer", "editor"]
    }]
    monkeypatch.setattr(auth.login, 'usuarios', mock_users)
    monkeypatch.setattr(auth.login, 'usuarios_dict', {u['username']: u for u in mock_users})

    # ============================================================
    # Inicializar autenticación
    # ============================================================
    from auth.login import init_routes_login
    init_routes_login(app)

    # ============================================================
    # Registrar blueprints usando el auto_register_blueprints del proyecto
    # Necesitamos cambiar temporalmente a ROOT_DIR para que encuentre "templates/Aplic"
    # ============================================================
    from core.blueprint_registry import auto_register_blueprints
    
    original_cwd = os.getcwd()
    try:
        os.chdir(ROOT_DIR)
        auto_register_blueprints(app)
    finally:
        os.chdir(original_cwd)  # Restaurar a tmp_path antes de yield

    # Ruta de contexto para inyectar menu y roles (evita errores en templates)
    @app.context_processor
    def inject_menu():
        from core.menu import cargar_menu
        from flask_login import current_user
        if current_user.is_authenticated:
            return dict(menu=cargar_menu(), roles=current_user.roles)
        return dict(menu=[], roles=[])

    yield app


# ============================================================
# 3. FIXTURE: client (Flask test client sin autenticar)
# ============================================================
@pytest.fixture
def client(app):
    """Cliente de prueba de Flask sin autenticar."""
    return app.test_client()


# ============================================================
# 4. FIXTURE: auth_client (Flask test client AUTENTICADO)
# ============================================================
@pytest.fixture
def auth_client(app):
    """
    Cliente de prueba de Flask con un usuario ya logueado.
    Inyecta directamente la sesión de Flask-Login.
    """
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['_user_id'] = '1'
            sess['_fresh'] = True
        yield client


# ============================================================
# 5. FIXTURE: _isolated_env (cambio de directorio temporal)
# ============================================================
@pytest.fixture(autouse=True)
def _isolated_env(tmp_path, monkeypatch):
    """
    Fixture automático que asegura que cada test trabaje
    en un directorio temporal aislado.
    """
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    yield
    os.chdir(original_cwd)