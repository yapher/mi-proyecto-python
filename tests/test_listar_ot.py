"""Tests del módulo Listar OT."""
import pytest
import json
import os


class TestListarOTPágina:
    def test_pagina_sin_archivos(self, auth_client, tmp_path, monkeypatch):
        # Forzar carpeta vacía
        monkeypatch.setattr(
            "templates.Aplic.listarot.BackEnd.listar_ot.CARPETA_JSON",
            str(tmp_path)
        )
        r = auth_client.get("/listar_ot")
        # Puede responder 200 con mensaje o texto plano
        assert r.status_code in (200, 404)

    def test_pagina_sin_auth_redirige(self, client):
        r = client.get("/listar_ot")
        assert r.status_code in (302, 401)


class TestListarOTConDatos:
    @pytest.fixture
    def ot_json(self, tmp_path, monkeypatch):
        """Crea un archivo JSON de OT de prueba."""
        carpeta = tmp_path / "dataOT"
        carpeta.mkdir()
        data = [
            {
                "numero_orden": "1234567",
                "descripcion": "OT de prueba",
                "inicio_extremo": "01/01/2026",
                "fin_extremo": "31/12/2026",
                "equipo_ut": "EQ1",
                "descripcion_equipo": "Equipo 1",
                "estado": "ABIERTA",
                "revision": "REV1"
            }
        ]
        archivo = carpeta / "ordenes_2026_08_24.JSON"
        archivo.write_text(json.dumps(data), encoding="utf-8")
        monkeypatch.setattr(
            "templates.Aplic.listarot.BackEnd.listar_ot.CARPETA_JSON",
            str(carpeta)
        )
        return archivo

    def test_pagina_con_datos(self, auth_client, ot_json):
        r = auth_client.get("/listar_ot")
        assert r.status_code == 200
        assert b"1234567" in r.data or b"OT de prueba" in r.data

    def test_filtro_torta(self, auth_client, ot_json):
        r = auth_client.get("/filtro_torta/estado/ABIERTA")
        assert r.status_code == 200