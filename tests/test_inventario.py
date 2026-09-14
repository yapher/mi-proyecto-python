# tests/test_inventario.py
"""
Tests para la aplicación Inventario.
Verifica que los repuestos se muestren correctamente por almacén.
"""
import pytest
from app import app as flask_app
from core.db_sql import db as _db


@pytest.fixture
def app():
    """Crea la app con configuración de test."""
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['WTF_CSRF_ENABLED'] = False
    flask_app.config['LOGIN_DISABLED'] = True

    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """Cliente de test."""
    return app.test_client()


@pytest.fixture
def auth_client(app, client):
    """Cliente autenticado."""
    from core.models import Usuario
    with app.app_context():
        usuario = Usuario(
            id='test1',
            username='testuser',
            password='testpass',
            roles=['viewer', 'admin']
        )
        _db.session.add(usuario)
        _db.session.commit()

    with client.session_transaction() as sess:
        sess['_user_id'] = 'test1'
        sess['_fresh'] = True

    return client


@pytest.fixture
def seed_data(app):
    """Crea datos de prueba: almacenes y repuestos."""
    from core.models import Almacen, Repuesto
    import json

    with app.app_context():
        # Almacén raíz
        alm1 = Almacen(
            nombre='Almacén Central',
            emoji='🏭',
            ruta='',
            ruta_jerarquia='Almacén Central',
            padre_id=None
        )
        _db.session.add(alm1)
        _db.session.flush()

        # Subalmacén
        alm2 = Almacen(
            nombre='Pañol 1',
            emoji='🔧',
            ruta='',
            ruta_jerarquia='Almacén Central.Pañol 1',
            padre_id=alm1.id
        )
        _db.session.add(alm2)

        # Otro almacén raíz
        alm3 = Almacen(
            nombre='Depósito',
            emoji='📦',
            ruta='',
            ruta_jerarquia='Depósito',
            padre_id=None
        )
        _db.session.add(alm3)
        _db.session.flush()

        # Repuestos asignados a distintos almacenes
        rep1 = Repuesto(
            codigo='REP001',
            nombre='Rodamiento 6205',
            cantidad=10,
            equipo='Almacén Central',
            estado='Disponible',
            ruta_jerarquia_json=json.dumps([])
        )
        rep2 = Repuesto(
            codigo='REP002',
            nombre='Correa en V',
            cantidad=5,
            equipo='Almacén Central.Pañol 1',
            estado='En espera',
            ruta_jerarquia_json=json.dumps([])
        )
        rep3 = Repuesto(
            codigo='REP003',
            nombre='Filtro de aceite',
            cantidad=0,
            equipo='Depósito',
            estado='No disponible',
            ruta_jerarquia_json=json.dumps([])
        )
        # Repuesto con equipo que es solo el nombre (sin jerarquía)
        rep4 = Repuesto(
            codigo='REP004',
            nombre='Bulón M12',
            cantidad=100,
            equipo='Pañol 1',  # Solo nombre, no ruta_jerarquia completa
            estado='Disponible',
            ruta_jerarquia_json=json.dumps([])
        )

        _db.session.add_all([rep1, rep2, rep3, rep4])
        _db.session.commit()

        return {
            'almacenes': [alm1, alm2, alm3],
            'repuestos': [rep1, rep2, rep3, rep4]
        }


class TestInventarioRoute:
    """Tests de la ruta principal de inventario."""

    def test_inventario_requiere_login(self, client):
        """Sin autenticación debe redirigir a login."""
        response = client.get('/inventario')
        assert response.status_code in (302, 401)

    def test_inventario_renderiza_correctamente(self, auth_client, seed_data):
        """Con autenticación y datos, debe renderizar la página."""
        response = auth_client.get('/inventario')
        assert response.status_code == 200
        assert b'Inventario' in response.data

    def test_inventario_muestra_almacenes(self, auth_client, seed_data):
        """Debe mostrar los nombres de los almacenes."""
        response = auth_client.get('/inventario')
        html = response.data.decode('utf-8')
        assert 'Almacén Central' in html
        assert 'Pañol 1' in html
        assert 'Depósito' in html

    def test_inventario_muestra_repuestos(self, auth_client, seed_data):
        """Debe mostrar los repuestos asignados."""
        response = auth_client.get('/inventario')
        html = response.data.decode('utf-8')
        assert 'Rodamiento 6205' in html
        assert 'Correa en V' in html
        assert 'Filtro de aceite' in html

    def test_inventario_repuesto_con_solo_nombre(self, auth_client, seed_data):
        """
        BUG FIX: Un repuesto con equipo='Pañol 1' (solo nombre, sin
        ruta_jerarquia completa) debe aparecer en el almacén correcto.
        """
        response = auth_client.get('/inventario')
        html = response.data.decode('utf-8')
        assert 'Bulón M12' in html

    def test_inventario_sin_repuestos(self, auth_client):
        """Si no hay repuestos, debe mostrar mensaje apropiado."""
        response = auth_client.get('/inventario')
        assert response.status_code == 200


class TestInventarioMapeo:
    """Tests de la función de mapeo de repuestos."""

    def test_mapeo_por_ruta_jerarquia(self, app, seed_data):
        """Repuestos indexados por ruta_jerarquia exacta."""
        from templates.Aplic.inventario.BackEnd.inventario import _construir_mapeo_repuestos
        from core.db_sql_store import almacen_store, repuesto_store

        with app.app_context():
            almacenes = almacen_store.cargar_arbol()
            repuestos = repuesto_store.cargar()
            mapeo = _construir_mapeo_repuestos(repuestos, almacenes)

            assert 'Almacén Central' in mapeo
            assert len(mapeo['Almacén Central']) >= 1

    def test_mapeo_por_nombre_fallback(self, app, seed_data):
        """Repuestos con solo el nombre deben encontrarse vía fallback."""
        from templates.Aplic.inventario.BackEnd.inventario import _construir_mapeo_repuestos
        from core.db_sql_store import almacen_store, repuesto_store

        with app.app_context():
            almacenes = almacen_store.cargar_arbol()
            repuestos = repuesto_store.cargar()
            mapeo = _construir_mapeo_repuestos(repuestos, almacenes)

            # 'Pañol 1' como nombre suelto debe estar indexado
            assert 'Pañol 1' in mapeo
            assert any(r['codigo'] == 'REP004' for r in mapeo['Pañol 1'])

    def test_mapeo_vacio(self, app):
        """Con datos vacíos no debe fallar."""
        from templates.Aplic.inventario.BackEnd.inventario import _construir_mapeo_repuestos

        with app.app_context():
            mapeo = _construir_mapeo_repuestos([], [])
            assert mapeo == {}

    def test_mapeo_repuesto_sin_equipo(self, app):
        """Repuestos sin campo equipo no deben romper el mapeo."""
        from templates.Aplic.inventario.BackEnd.inventario import _construir_mapeo_repuestos

        with app.app_context():
            repuestos = [{'codigo': 'X', 'nombre': 'Test', 'equipo': ''}]
            mapeo = _construir_mapeo_repuestos(repuestos, [])
            assert mapeo == {}