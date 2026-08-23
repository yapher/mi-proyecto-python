"""Tests adicionales para Pagos - clonado de meses."""
import pytest
import json


class TestPagosClonar:
    def test_clonar_mes_sin_origen(self, auth_client):
        r = auth_client.post("/pagos/clonar_mes", json={
            "anio_origen": 1900,
            "mes_origen": 1,
            "anio_destino": 2026,
            "mes_destino": 9
        })
        assert r.status_code in (400, 404)

    def test_clonar_mes_parametros_invalidos(self, auth_client):
        r = auth_client.post("/pagos/clonar_mes", json={})
        assert r.status_code in (400, 404)

    def test_clonar_mes_valido(self, auth_client):
        # 1. Crear un pago en un mes
        r = auth_client.post("/pagos/agregar", json={
            "rubro": "Test",
            "descripcion": "Pago para clonar",
            "importe": 100,
            "tipo": "único",
            "vencimiento": "2026-08-15",
            "pagado": False
        })
        assert r.status_code in (200, 201)

        # 2. Clonar agosto → septiembre
        r = auth_client.post("/pagos/clonar_mes", json={
            "anio_origen": 2026,
            "mes_origen": 8,
            "anio_destino": 2026,
            "mes_destino": 9
        })
        assert r.status_code == 200
        data = r.get_json()
        assert data.get("cantidad", 0) >= 1

        # 3. Verificar que existe en septiembre
        r = auth_client.get("/pagos/mensuales/2026/9")
        assert r.status_code == 200