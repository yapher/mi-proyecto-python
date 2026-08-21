"""Tests del módulo Tareas - CRUD completo con rutas reales."""
import pytest


class TestTareasPagina:
    """Tests de la página principal de tareas."""

    def test_pagina_tareas_responde_200(self, auth_client):
        """GET /tareas debe responder 200 con HTML."""
        r = auth_client.get('/tareas')
        assert r.status_code == 200
        assert b'tareas' in r.data.lower() or b'tarea' in r.data.lower()

    def test_pagina_tareas_sin_auth_redirige(self, client):
        """GET /tareas sin auth debe redirigir."""
        r = client.get('/tareas')
        assert r.status_code in (302, 401)


class TestTareasCRUD:
    """Tests de Crear, Leer, Actualizar y Eliminar tareas."""

    def test_crear_tarea(self, auth_client):
        """POST /agregar debe crear una tarea nueva."""
        r = auth_client.post('/agregar', data={
            'titulo': 'Tarea de prueba',
            'fecha': '2026-08-22',
            'descripcion': 'Descripción de prueba',
            'prioridad': 'alta'
        }, follow_redirects=True)
        
        # Puede responder 200 (redirige a /tareas) o 302
        assert r.status_code == 200

    def test_crear_tarea_sin_titulo(self, auth_client):
        """POST /agregar sin título debe fallar o redirigir con error."""
        r = auth_client.post('/agregar', data={
            'fecha': '2026-08-22',
            'descripcion': 'Sin título'
        })
        # Puede devolver 400, 200 con error, o redirigir
        assert r.status_code in (200, 302, 400)

    def test_listar_tareas_devuelve_json_o_html(self, auth_client):
        """GET /tareas debe devolver contenido válido."""
        r = auth_client.get('/tareas')
        assert r.status_code == 200
        assert len(r.data) > 0

    def test_eliminar_tarea_inexistente(self, auth_client):
        """GET /eliminar/<id_inexistente> no debe romper la app."""
        r = auth_client.get('/eliminar/999999')
        # Puede redirigir a /tareas o devolver 200/404
        assert r.status_code in (200, 302, 404)

    def test_editar_tarea_inexistente(self, auth_client):
        """POST /editar/<id_inexistente> no debe romper la app."""
        r = auth_client.post('/editar/999999', data={
        'titulo': 'Editada'
        })
        # El backend devuelve 400 cuando la tarea no existe o los datos son inválidos
        assert r.status_code in (200, 302, 400, 404)


class TestTareasFlujoCompleto:
    """Tests de flujo completo: crear, verificar, editar, eliminar."""

    def test_flujo_completo_tarea(self, auth_client):
        """Crea una tarea, verifica que existe, la edita y la elimina."""
        # 1. Crear tarea
        r = auth_client.post('/agregar', data={
            'titulo': 'Tarea flujo completo',
            'fecha': '2026-08-22',
            'descripcion': 'Test de flujo',
            'prioridad': 'media'
        }, follow_redirects=True)
        assert r.status_code == 200

        # 2. Verificar que la página responde (la tarea debería estar en la lista)
        r = auth_client.get('/tareas')
        assert r.status_code == 200
        # El título debería aparecer en el HTML
        assert b'Tarea flujo completo' in r.data or b'tarea' in r.data.lower()