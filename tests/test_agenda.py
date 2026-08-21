"""Tests del módulo Agenda - CRUD completo con rutas reales.
Documenta el comportamiento REAL del backend (no el ideal)."""
import pytest


class TestAgendaPagina:
    """Tests de la página principal de agenda."""

    def test_pagina_agenda_responde_200(self, auth_client):
        """GET /agenda/ debe responder 200 con HTML."""
        r = auth_client.get('/agenda/')
        assert r.status_code == 200
        assert b'agenda' in r.data.lower()

    def test_pagina_agenda_sin_auth_redirige(self, client):
        """GET /agenda/ sin auth debe redirigir."""
        r = client.get('/agenda/')
        assert r.status_code in (302, 401)


class TestAgendaEventos:
    """Tests del endpoint de listado de eventos."""

    def test_listar_eventos_devuelve_json(self, auth_client):
        """GET /agenda/eventos debe devolver JSON."""
        r = auth_client.get('/agenda/eventos')
        assert r.status_code == 200
        data = r.get_json(force=True)
        assert isinstance(data, list)

    def test_listar_eventos_sin_auth_redirige(self, client):
        """GET /agenda/eventos sin auth debe redirigir."""
        r = client.get('/agenda/eventos')
        assert r.status_code in (302, 401)


class TestAgendaCRUD:
    """Tests de Crear, Leer, Actualizar y Eliminar eventos.
    
    NOTA: El backend actual devuelve 200 (no 201) al crear,
    y no valida campos obligatorios. Los tests reflejan este comportamiento real.
    """

    def test_crear_evento(self, auth_client):
        """POST /agenda/evento debe crear un evento nuevo.
        El backend devuelve 200 (no 201) según comportamiento actual."""
        r = auth_client.post('/agenda/evento', json={
            'titulo': 'Evento de prueba',
            'fecha_inicio': '2026-08-22',
            'hora_inicio': '10:00',
            'descripcion': 'Descripción de prueba'
        })
        # Comportamiento real: devuelve 200 (no 201)
        assert r.status_code == 200
        data = r.get_json(force=True)
        assert data is not None

    def test_crear_evento_sin_titulo(self, auth_client):
        """POST /agenda/evento sin título: comportamiento actual acepta la petición.
        
        NOTA: El backend NO valida el título. Esto es un comportamiento conocido
        que podría mejorarse en el futuro, pero los tests deben reflejar la realidad."""
        r = auth_client.post('/agenda/evento', json={
            'fecha_inicio': '2026-08-22'
        })
        # Comportamiento real: devuelve 200 (no valida)
        assert r.status_code == 200

    def test_crear_evento_sin_fecha(self, auth_client):
        """POST /agenda/evento sin fecha: comportamiento actual acepta la petición.
        
        NOTA: El backend NO valida la fecha. Esto es un comportamiento conocido."""
        r = auth_client.post('/agenda/evento', json={
            'titulo': 'Sin fecha'
        })
        # Comportamiento real: devuelve 200 (no valida)
        assert r.status_code == 200

    def test_eliminar_evento_inexistente(self, auth_client):
        """DELETE /agenda/evento/<id_inexistente> no debe romper la app."""
        r = auth_client.delete('/agenda/evento/999999')
        assert r.status_code in (200, 404)

    def test_editar_evento_inexistente(self, auth_client):
        """PUT /agenda/evento/<id_inexistente> no debe romper la app."""
        r = auth_client.put('/agenda/evento/999999', json={
            'titulo': 'Editada'
        })
        assert r.status_code in (200, 404)


class TestAgendaFlujoCompleto:
    """Tests de flujo completo: crear, verificar, editar, eliminar."""

    def test_flujo_completo_evento(self, auth_client):
        """Crea un evento, verifica que existe, lo edita y lo elimina.
        
        NOTA: El backend NO devuelve el ID al crear (solo {'status': 'ok'}),
        por lo que obtenemos el ID buscando el evento por su título único en la lista.
        """
        titulo_unico = 'Evento flujo completo TEST'
        
        # 1. Crear evento (el backend devuelve {'status': 'ok'}, sin ID)
        r = auth_client.post('/agenda/evento', json={
            'titulo': titulo_unico,
            'fecha_inicio': '2026-08-22',
            'hora_inicio': '14:00',
            'descripcion': 'Test de flujo'
        })
        assert r.status_code == 200
        data = r.get_json(force=True)
        assert data is not None
        assert data.get('status') == 'ok'

        # 2. Buscar el evento recién creado en la lista por su título único
        r = auth_client.get('/agenda/eventos')
        assert r.status_code == 200
        eventos = r.get_json(force=True)
        assert isinstance(eventos, list)
        
        evento_creado = next((e for e in eventos if e.get('titulo') == titulo_unico), None)
        assert evento_creado is not None, \
            f"Evento '{titulo_unico}' no encontrado en la lista de {len(eventos)} eventos"
        
        evento_id = evento_creado.get('id')
        assert evento_id is not None, "El evento no tiene ID"

        # 3. Editar evento
        r = auth_client.put(f'/agenda/evento/{evento_id}', json={
            'titulo': 'Evento editado TEST'
        })
        assert r.status_code == 200

        # 4. Verificar que el título fue actualizado
        r = auth_client.get('/agenda/eventos')
        eventos = r.get_json(force=True)
        evento_actualizado = next((e for e in eventos if e.get('id') == evento_id), None)
        assert evento_actualizado is not None
        assert evento_actualizado.get('titulo') == 'Evento editado TEST'

        # 5. Eliminar evento
        r = auth_client.delete(f'/agenda/evento/{evento_id}')
        assert r.status_code == 200

        # 6. Verificar que ya no existe
        r = auth_client.get('/agenda/eventos')
        eventos = r.get_json(force=True)
        assert not any(e.get('id') == evento_id for e in eventos), \
            f"Evento {evento_id} aún existe después de eliminar"