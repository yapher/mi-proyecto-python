"""Tests del módulo Modelos 3D."""
import pytest


class TestModelos3DPagina:
    def test_pagina_responde_200(self, auth_client):
        r = auth_client.get("/modelos_3d")
        assert r.status_code == 200
        assert b"modelo" in r.data.lower() or b"3d" in r.data.lower()

    def test_pagina_sin_auth_redirige(self, client):
        r = client.get("/modelos_3d")
        assert r.status_code in (302, 401)


class TestModelos3DAPI:
    def test_cargar_sensores_inexistente(self, auth_client):
        r = auth_client.get("/modelos_3d/cargar_sensores/no_existe.glb")
        assert r.status_code == 200
        data = r.get_json()
        assert isinstance(data, list) and len(data) == 0

    def test_guardar_sensores(self, auth_client):
        sensores = [
            {"nombre": "Sensor1", "color": 0xff0000, "forma": "sphere",
             "size": 1.0, "pos": {"x": 0, "y": 0, "z": 0}}
        ]
        r = auth_client.post(
            "/modelos_3d/guardar_sensores/test_model.glb",
            json=sensores
        )
        assert r.status_code == 200

        # Verificar que se guardó
        r = auth_client.get("/modelos_3d/cargar_sensores/test_model.glb")
        data = r.get_json()
        assert len(data) == 1
        assert data[0]["nombre"] == "Sensor1"