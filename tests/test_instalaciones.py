"""Tests del módulo Instalaciones."""
import pytest


class TestInstalacionesPagina:
    def test_pagina_responde_200(self, auth_client):
        r = auth_client.get("/instalaciones")
        assert r.status_code == 200
        assert b"instalacion" in r.data.lower() or b"tree" in r.data.lower()

    def test_pagina_sin_auth_redirige(self, client):
        r = client.get("/instalaciones")
        assert r.status_code in (302, 401)


class TestInstalacionesAPI:
    def test_api_ubicaciones_devuelve_json(self, auth_client):
        r = auth_client.get("/api/ubicaciones")
        assert r.status_code == 200
        data = r.get_json()
        assert isinstance(data, list)

    def test_api_ubicacion_tecnica_json(self, auth_client):
        r = auth_client.get("/api/ubicacion_tecnica_json")
        assert r.status_code == 200

    def test_editar_sin_datos_falla(self, auth_client):
        r = auth_client.put("/api/editar_ubicacion", json={})
        assert r.status_code in (400, 404)

    def test_borrar_sin_datos_falla(self, auth_client):
        r = auth_client.delete("/api/borrar_ubicacion", json={})
        assert r.status_code in (400, 404)

    def test_agregar_sububicacion_sin_datos_falla(self, auth_client):
        r = auth_client.post("/api/agregar_sububicacion", json={})
        assert r.status_code in (400, 404)