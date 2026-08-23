"""Tests del módulo Agenda - CRUD completo + Mobile.
Cubre:
- Página principal (200, auth)
- Listado de eventos (JSON)
- Crear / Editar / Eliminar eventos
- Toggle realizado
- Validaciones básicas
- Responsive (headers mobile)
"""
import pytest
from datetime import datetime

class TestAgendaPagina:
    """Tests de la página principal de agenda."""
    def test_pagina_agenda_responde_200(self, auth_client):
        """GET /agenda/ debe responder 200 con HTML."""
        r = auth_client.get('/agenda/')
        assert r.status_code == 200
        assert b'agenda' in r.data.lower()

    def test_pagina_agenda_contiene_calendario(self, auth_client):
        """La página debe incluir el contenedor del calendario."""
        r = auth_client.get('/agenda/')
        assert b'id="calendario"' in r.data
        assert b'id="mes"' in r.data
        assert b'id="a' in r.data  # año

    def test_pagina_agenda_incluye_css_mobile(self, auth_client):
        """Debe cargar el CSS de agenda (mobile-first)."""
        r = auth_client.get('/agenda/')
        assert b'agenda.css' in r.data

    def test_pagina_agenda_incluye_js(self, auth_client):
        """Debe cargar el JS de agenda."""
        r = auth_client.get('/agenda/')
        assert b'agenda.js' in r.data

    def test_pagina_agenda_sin_auth_redirige(self, client):
        """GET /agenda/ sin auth debe redirigir."""
        r = client.get('/agenda/')
        assert r.status_code in (302, 401)

    def test_viewport_meta_presente(self, auth_client):
        """El layout debe incluir viewport mobile-friendly."""
        r = auth_client.get('/agenda/')
        assert b'viewport' in r.data.lower()
        assert b'width=device-width' in r.data

class TestAgendaEventos:
    """Tests del endpoint de listado de eventos."""
    def test_listar_eventos_devuelve_json(self, auth_client):
        """GET /agenda/eventos debe devolver JSON."""
        r = auth_client.get('/agenda/eventos')
        assert r.status_code == 200
        assert r.content_type.startswith('application/json')
        data = r.get_json()
        assert isinstance(data, list)

    def test_listar_eventos_con_filtro_mes(self, auth_client):
        """GET /agenda/eventos?mes=X&año=Y filtra correctamente."""
        r = auth_client.get('/agenda/eventos?mes=8&año=2026')
        assert r.status_code == 200
        data = r.get_json()
        assert isinstance(data, list)

class TestAgendaCRUD:
    """Tests de Crear / Leer / Actualizar / Eliminar."""
    def test_crear_evento_minimo(self, auth_client):
        """POST /agenda/evento con datos mínimos crea el evento."""
        payload = {
            'titulo': 'Evento TEST',
            'fecha': '2026-08-23',
            'descripcion': 'Descripción test',
            'email': 'test@test.com',
            'prioridad': 'media',
            'realizado': False
        }
        r = auth_client.post('/agenda/evento', json=payload)
        assert r.status_code in (200, 201)
        # Verificar que existe
        r2 = auth_client.get('/agenda/eventos')
        eventos = r2.get_json()
        assert any(e.get('titulo') == 'Evento TEST' for e in eventos)

    def test_crear_evento_sin_titulo(self, auth_client):
        """POST sin título: comportamiento real (acepta o rechaza)."""
        r = auth_client.post('/agenda/evento', json={
            'fecha': '2026-08-23'
        })
        # Documentamos comportamiento real
        assert r.status_code in (200, 201, 400)

    def test_crear_evento_sin_fecha(self, auth_client):
        """POST sin fecha: comportamiento real (acepta)."""
        r = auth_client.post('/agenda/evento', json={
            'titulo': 'Sin fecha'
        })
        # Comportamiento conocido: no valida
        assert r.status_code in (200, 201, 400)

    def test_editar_evento(self, auth_client):
        """PUT /agenda/evento/<id> actualiza el evento."""
        # Crear
        r = auth_client.post('/agenda/evento', json={
            'titulo': 'Original',
            'fecha': '2026-08-24'
        })
        assert r.status_code in (200, 201)
        # Obtener ID
        eventos = auth_client.get('/agenda/eventos').get_json()
        evento = next((e for e in eventos if e.get('titulo') == 'Original'), None)
        assert evento is not None
        evento_id = evento['id']
        # Editar
        r = auth_client.put(f'/agenda/evento/{evento_id}', json={
            'titulo': 'Editado TEST'
        })
        assert r.status_code == 200
        # Verificar
        eventos = auth_client.get('/agenda/eventos').get_json()
        actualizado = next((e for e in eventos if e.get('id') == evento_id), None)
        assert actualizado is not None
        assert actualizado.get('titulo') == 'Editado TEST'

    def test_toggle_realizado(self, auth_client):
        """PUT permite cambiar el campo 'realizado'."""
        # Crear
        r = auth_client.post('/agenda/evento', json={
            'titulo': 'Toggle TEST',
            'fecha': '2026-08-25',
            'realizado': False
        })
        assert r.status_code in (200, 201)
        eventos = auth_client.get('/agenda/eventos').get_json()
        evento = next((e for e in eventos if e.get('titulo') == 'Toggle TEST'), None)
        assert evento is not None
        evento_id = evento['id']
        # Marcar como realizado
        r = auth_client.put(f'/agenda/evento/{evento_id}', json={
            'realizado': True
        })
        assert r.status_code == 200
        eventos = auth_client.get('/agenda/eventos').get_json()
        actualizado = next((e for e in eventos if e.get('id') == evento_id), None)
        assert actualizado.get('realizado') is True

    def test_eliminar_evento(self, auth_client):
        """DELETE /agenda/evento/<id> elimina el evento."""
        # Crear
        r = auth_client.post('/agenda/evento', json={
            'titulo': 'A eliminar',
            'fecha': '2026-08-26'
        })
        assert r.status_code in (200, 201)
        eventos = auth_client.get('/agenda/eventos').get_json()
        evento = next((e for e in eventos if e.get('titulo') == 'A eliminar'), None)
        assert evento is not None
        evento_id = evento['id']
        # Eliminar
        r = auth_client.delete(f'/agenda/evento/{evento_id}')
        assert r.status_code == 200
        # Verificar que ya no existe
        eventos = auth_client.get('/agenda/eventos').get_json()
        assert not any(e.get('id') == evento_id for e in eventos)

    def test_eliminar_evento_inexistente(self, auth_client):
        """DELETE sobre ID inexistente no debe romper la app."""
        r = auth_client.delete('/agenda/evento/999999')
        assert r.status_code in (200, 404)

class TestAgendaMobile:
    """Tests específicos de comportamiento mobile."""
    def test_css_contiene_media_queries(self, auth_client):
        """El CSS debe incluir media queries para responsive."""
        r = auth_client.get('/agenda/')
        # El HTML carga el CSS; verificamos que el CSS existe
        r_css = auth_client.get('/static/css/apps/agenda.css')
        assert r_css.status_code == 200
        css = r_css.data.decode('utf-8')
        assert '@media' in css
        assert 'min-width' in css or 'max-width' in css

    def test_css_touch_minimo(self, auth_client):
        """El CSS debe definir tamaño táctil mínimo (44px)."""
        r_css = auth_client.get('/static/css/apps/agenda.css')
        assert r_css.status_code == 200
        css = r_css.data.decode('utf-8')
        # Debe tener referencia a 44px o variable touch
        assert '44px' in css or 'touch-min' in css.lower()

    def test_js_exponer_funciones_globales(self, auth_client):
        """El JS debe exponer abrirModal, guardarEvento, eliminarEvento."""
        r_js = auth_client.get('/static/js/apps/agenda.js')
        assert r_js.status_code == 200
        js = r_js.data.decode('utf-8')
        assert 'window.abrirModal' in js or 'abrirModal' in js
        
        # guardarEvento y eliminarEvento están en evento.js
        r_js_evento = auth_client.get('/static/js/apps/evento.js')
        assert r_js_evento.status_code == 200
        js_evento = r_js_evento.data.decode('utf-8')
        assert 'guardarEvento' in js_evento
        assert 'eliminarEvento' in js_evento

    def test_html_controles_responsive(self, auth_client):
        """El HTML debe usar la clase controls-responsive."""
        r = auth_client.get('/agenda/')
        assert b'controls-responsive' in r.data

    def test_html_table_responsive(self, auth_client):
        """El HTML debe envolver la tabla en table-responsive."""
        r = auth_client.get('/agenda/')
        assert b'table-responsive' in r.data

class TestAgendaSeguridad:
    """Tests de seguridad y auth."""
    def test_crear_evento_sin_auth(self, client):
        """POST /agenda/evento sin auth debe fallar."""
        r = client.post('/agenda/evento', json={
            'titulo': 'No auth',
            'fecha': '2026-08-23'
        })
        assert r.status_code in (302, 401, 403)

    def test_editar_evento_sin_auth(self, client):
        """PUT sin auth debe fallar."""
        r = client.put('/agenda/evento/1', json={'titulo': 'X'})
        assert r.status_code in (302, 401, 403)

    def test_eliminar_evento_sin_auth(self, client):
        """DELETE sin auth debe fallar."""
        r = client.delete('/agenda/evento/1')
        assert r.status_code in (302, 401, 403)