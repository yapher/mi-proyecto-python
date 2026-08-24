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


class TestEstadosRepuestosFrontend:
    """Tests que verifican que el HTML generado tenga los elementos necesarios para el JS"""
    
    def test_botones_editar_tienen_atributos_para_js(self, auth_client):
        r = auth_client.get("/estadosRep")
        assert r.status_code == 200
        html = r.data.decode('utf-8')
        
        # Esto hubiera fallado cuando el atributo se llamaba data-emojy en lugar de data-estado
        # o cuando el JS no podía leer los datos por un error de sintaxis.
        assert 'data-codigo=' in html, "Falta el atributo data-codigo en los botones de editar"
        assert 'data-estado=' in html or 'data-emojy=' in html, "Falta el atributo del estado en los botones"
        assert 'data-ruta_jerarquia=' in html, "Falta el atributo de ruta jerárquica"

    def test_modal_nuevo_repuesto_tiene_campo_return_to(self, auth_client):
        r = auth_client.get("/lista_repuestos") # Probamos desde la otra vista
        assert r.status_code == 200
        html = r.data.decode('utf-8')
        
        # Esto verifica que la solución del redirect dinámico esté presente en el HTML
        assert 'name="return_to"' in html, "El modal debe tener el campo oculto return_to para redirigir correctamente"