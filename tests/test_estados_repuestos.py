"""Tests del módulo Estados de Repuestos."""
import pytest


class TestEstadosRepuestosPagina:
    def test_pagina_responde_200(self, auth_client):
        r = auth_client.get("/estadosRep")
        assert r.status_code == 200

    def test_pagina_sin_auth_redirige(self, client):
        r = client.get("/estadosRep")
        assert r.status_code in (302, 401)


class TestEstadosRepuestosAPI:
    def test_api_repuestos_devuelve_json(self, auth_client):
        r = auth_client.get("/api/repuestos")
        assert r.status_code == 200
        data = r.get_json()
        assert "repuestos" in data

    def test_api_con_filtro_ruta(self, auth_client):
        r = auth_client.get("/api/repuestos?ruta_jerarquia=Almacen1")
        assert r.status_code == 200
        data = r.get_json()
        assert isinstance(data.get("repuestos"), list)

    def test_exportar_pdf(self, auth_client):
        r = auth_client.post("/exportar_pdf", data={
            "ruta_jerarquia": "",
            "buscar": ""
        })
        # Debe devolver PDF o redirigir
        assert r.status_code in (200, 302)
        if r.status_code == 200:
            assert r.mimetype == "application/pdf"