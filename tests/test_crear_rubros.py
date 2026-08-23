"""Tests del módulo Crear Rubros - API CRUD completa."""
import pytest


class TestRubrosPagina:
    def test_pagina_responde_200(self, auth_client):
        r = auth_client.get("/crear_rubros")
        assert r.status_code == 200
        assert b"rubro" in r.data.lower()

    def test_pagina_sin_auth_redirige(self, client):
        r = client.get("/crear_rubros")
        assert r.status_code in (302, 401)


class TestRubrosAPI:
    def test_listar_arbol_devuelve_json(self, auth_client):
        r = auth_client.get("/api/rubro_arbol")
        assert r.status_code == 200
        data = r.get_json()
        assert isinstance(data, list)

    def test_crear_rubro_sin_datos_falla(self, auth_client):
        r = auth_client.post("/api/rubro", json={})
        assert r.status_code in (400, 422)

    def test_crear_rubro_raiz(self, auth_client):
        r = auth_client.post("/api/rubro", json={
            "nombre": "RubroTest",
            "emoji": "🧪",
            "ruta": "",
            "ruta_padre": ""
        })
        assert r.status_code in (200, 201)

    def test_editar_rubro_inexistente(self, auth_client):
        r = auth_client.put("/api/rubro", json={
            "ruta": "NoExiste",
            "nombre": "X",
            "emoji": "🧪"
        })
        assert r.status_code in (400, 404)

    def test_eliminar_rubro_inexistente(self, auth_client):
        r = auth_client.delete("/api/rubro", json={"ruta": "NoExiste"})
        assert r.status_code in (400, 404)

    def test_flujo_completo(self, auth_client):
        nombre = "FlujoTest"
        # Crear
        r = auth_client.post("/api/rubro", json={
            "nombre": nombre, "emoji": "🧪", "ruta": "", "ruta_padre": ""
        })
        assert r.status_code in (200, 201)

        # Listar
        r = auth_client.get("/api/rubro_arbol")
        data = r.get_json()
        assert any(n["nombre"] == nombre for n in data)

        # Eliminar
        r = auth_client.delete("/api/rubro", json={"ruta": nombre})
        assert r.status_code in (200, 404)