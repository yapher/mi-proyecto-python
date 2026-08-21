"""Tests de diagnóstico - Verifica que las rutas principales respondan."""
import pytest


class TestRutasBasicas:
    """Verifica que las rutas principales de la app respondan."""

    # ============ RUTAS PÚBLICAS (sin auth) ============
    def test_login_get(self, client):
        """GET /login debe responder 200."""
        r = client.get('/login')
        assert r.status_code == 200

    def test_login_post_sin_credenciales(self, client):
        """POST /login sin credenciales debe redirigir o fallar."""
        r = client.post('/login', data={})
        # Puede ser 200 (vuelve al login con error) o 302 (redirige)
        assert r.status_code in (200, 302, 400)

    # ============ RUTAS PROTEGIDAS (requieren auth) ============
    def test_tareas_get(self, auth_client):
        """GET /tareas debe responder 200."""
        r = auth_client.get('/tareas')
        assert r.status_code == 200

    def test_agenda_get(self, auth_client):
        """GET /agenda/ debe responder 200."""
        r = auth_client.get('/agenda/')
        assert r.status_code == 200

    def test_pagos_get(self, auth_client):
        """GET /pagos debe responder 200."""
        r = auth_client.get('/pagos')
        assert r.status_code == 200

    def test_gestion_bloqueos_get(self, auth_client):
        """GET /gestion_de_bloqueos debe responder 200."""
        r = auth_client.get('/gestion_de_bloqueos')
        assert r.status_code == 200

    # ============ ENDPOINTS API (JSON) ============
    def test_agenda_eventos_listar(self, auth_client):
        """GET /agenda/eventos debe devolver JSON."""
        r = auth_client.get('/agenda/eventos')
        assert r.status_code == 200
        data = r.get_json(force=True)
        assert isinstance(data, list)

    def test_pagos_listar(self, auth_client):
        """GET /pagos/listar debe devolver JSON."""
        r = auth_client.get('/pagos/listar')
        assert r.status_code == 200
        data = r.get_json(force=True)
        assert isinstance(data, (list, dict))

    # ============ RUTAS PROTEGIDAS SIN AUTH ============
    def test_tareas_sin_auth_redirige(self, client):
        """GET /tareas sin auth debe redirigir a login."""
        r = client.get('/tareas')
        # Flask-Login redirige con 302 a /login
        assert r.status_code in (302, 401)

    def test_agenda_sin_auth_redirige(self, client):
        """GET /agenda/ sin auth debe redirigir a login."""
        r = client.get('/agenda/')
        assert r.status_code in (302, 401)

    def test_pagos_sin_auth_redirige(self, client):
        """GET /pagos sin auth debe redirigir a login."""
        r = client.get('/pagos')
        assert r.status_code in (302, 401)