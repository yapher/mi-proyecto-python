"""
Tests para la aplicacion de Tareas (API REST).
Rutas:
  GET    /tareas              -> Vista HTML
  GET    /api/tareas          -> Listar tareas (JSON)
  POST   /api/tareas          -> Crear tarea (JSON)
  PUT    /api/tareas/<id>     -> Actualizar tarea (JSON)
  DELETE /api/tareas/<id>     -> Eliminar tarea (JSON)
"""
import pytest
import json


# ============================================================
# TESTS DE VISTA PRINCIPAL
# ============================================================

class TestTareasVista:
    """Tests de la vista HTML principal."""

    def test_vista_tareas_requiere_login(self, client):
        """Sin autenticacion, debe redirigir al login."""
        response = client.get("/tareas")
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_vista_tareas_autenticado(self, auth_client):
        """La vista debe renderizar correctamente."""
        response = auth_client.get("/tareas")
        assert response.status_code == 200

    def test_vista_tareas_contiene_titulo(self, auth_client):
        """La vista debe contener el titulo de la app."""
        response = auth_client.get("/tareas")
        html = response.data.decode('utf-8')
        assert "Tareas" in html

    def test_vista_tareas_contiene_formulario(self, auth_client):
        """La vista debe contener el formulario de agregar."""
        response = auth_client.get("/tareas")
        html = response.data.decode('utf-8')
        assert 'id="formAgregarTarea"' in html
        assert 'id="titulo"' in html
        assert 'id="fecha"' in html
        assert 'id="descripcion"' in html

    def test_vista_tareas_contiene_lista(self, auth_client):
        """La vista debe contener el contenedor de la lista."""
        response = auth_client.get("/tareas")
        html = response.data.decode('utf-8')
        assert 'id="listaTareas"' in html

    def test_vista_tareas_contiene_modal_edicion(self, auth_client):
        """La vista debe contener el modal de edicion."""
        response = auth_client.get("/tareas")
        html = response.data.decode('utf-8')
        assert 'id="modalEditarTarea"' in html
        assert 'id="formEditarTarea"' in html

    def test_vista_tareas_carga_js(self, auth_client):
        """La vista debe cargar el JS de la app."""
        response = auth_client.get("/tareas")
        html = response.data.decode('utf-8')
        assert '/tareas/static/js/tareas.js' in html

    def test_vista_tareas_carga_css(self, auth_client):
        """La vista debe cargar el CSS de la app."""
        response = auth_client.get("/tareas")
        html = response.data.decode('utf-8')
        assert 'tareas.css' in html


# ============================================================
# TESTS DE ARCHIVOS ESTATICOS
# ============================================================

class TestTareasEstaticos:
    """Tests de archivos estaticos de la app."""

    def test_css_estatico_accesible(self, auth_client):
        """El CSS estatico de la app debe ser accesible."""
        response = auth_client.get("/tareas/static/css/tareas.css")
        assert response.status_code == 200
        assert b"tareas-container" in response.data

    def test_js_estatico_accesible(self, auth_client):
        """El JS estatico de la app debe ser accesible."""
        response = auth_client.get("/tareas/static/js/tareas.js")
        assert response.status_code == 200
        assert b"API_BASE" in response.data


# ============================================================
# TESTS DE API REST: LISTAR
# ============================================================

class TestTareasListar:
    """Tests de GET /api/tareas."""

    def test_listar_tareas_vacio(self, auth_client):
        """Debe retornar lista vacia inicialmente."""
        response = auth_client.get("/api/tareas")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_listar_tareas_sin_auth(self, client):
        """Sin autenticacion debe redirigir."""
        response = client.get("/api/tareas")
        assert response.status_code == 302

    def test_listar_tareas_con_datos(self, auth_client):
        """Debe retornar las tareas creadas."""
        auth_client.post("/api/tareas", json={
            "titulo": "Tarea 1",
            "fecha": "2026-08-28",
            "descripcion": "Desc 1"
        })
        auth_client.post("/api/tareas", json={
            "titulo": "Tarea 2",
            "fecha": "2026-08-29",
            "descripcion": "Desc 2"
        })
        response = auth_client.get("/api/tareas")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 2


# ============================================================
# TESTS DE API REST: CREAR
# ============================================================

class TestTareasCrear:
    """Tests de POST /api/tareas."""

    def test_crear_tarea(self, auth_client):
        """Debe crear una tarea correctamente."""
        response = auth_client.post("/api/tareas", json={
            "titulo": "Tarea de prueba",
            "fecha": "2026-08-28",
            "descripcion": "Descripcion de prueba"
        })
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["status"] == "ok"
        assert data["item"]["titulo"] == "Tarea de prueba"
        assert data["item"]["fecha"] == "2026-08-28"
        assert "id" in data["item"]

    def test_crear_tarea_sin_titulo(self, auth_client):
        """Debe fallar sin titulo."""
        response = auth_client.post("/api/tareas", json={
            "fecha": "2026-08-28",
            "descripcion": "Sin titulo"
        })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["status"] == "error"

    def test_crear_tarea_sin_fecha(self, auth_client):
        """Debe fallar sin fecha."""
        response = auth_client.post("/api/tareas", json={
            "titulo": "Test",
            "descripcion": "Sin fecha"
        })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["status"] == "error"

    def test_crear_tarea_sin_descripcion(self, auth_client):
        """Debe permitir crear sin descripcion (campo opcional)."""
        response = auth_client.post("/api/tareas", json={
            "titulo": "Sin descripcion",
            "fecha": "2026-08-28"
        })
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["status"] == "ok"

    def test_crear_tarea_con_caracteres_especiales(self, auth_client):
        """Debe manejar caracteres especiales correctamente."""
        response = auth_client.post("/api/tareas", json={
            "titulo": "Tarea con acentos y eñe",
            "fecha": "2026-08-28",
            "descripcion": "Descripcion con caracteres: a, e, i, o, u, ñ"
        })
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["status"] == "ok"
        assert data["item"]["titulo"] == "Tarea con acentos y eñe"

    def test_crear_tarea_sin_auth(self, client):
        """Sin autenticacion debe redirigir."""
        response = client.post("/api/tareas", json={
            "titulo": "Test",
            "fecha": "2026-08-28"
        })
        assert response.status_code == 302


# ============================================================
# TESTS DE API REST: ACTUALIZAR
# ============================================================

class TestTareasActualizar:
    """Tests de PUT /api/tareas/<id>."""

    def test_actualizar_tarea(self, auth_client):
        """Debe actualizar una tarea existente."""
        # Crear tarea
        res = auth_client.post("/api/tareas", json={
            "titulo": "Original",
            "fecha": "2026-08-28",
            "descripcion": "Desc original"
        })
        tarea_id = json.loads(res.data)["item"]["id"]

        # Actualizar
        response = auth_client.put(f"/api/tareas/{tarea_id}", json={
            "titulo": "Actualizada",
            "fecha": "2026-08-30",
            "descripcion": "Nueva descripcion"
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "ok"

        # Verificar que se actualizo
        response = auth_client.get("/api/tareas")
        tareas = json.loads(response.data)
        tarea = next((t for t in tareas if t["id"] == tarea_id), None)
        assert tarea is not None
        assert tarea["titulo"] == "Actualizada"
        assert tarea["fecha"] == "2026-08-30"

    def test_actualizar_tarea_inexistente(self, auth_client):
        """Debe retornar 404 al actualizar tarea inexistente."""
        response = auth_client.put("/api/tareas/99999", json={
            "titulo": "Test",
            "fecha": "2026-08-28",
            "descripcion": "Desc"
        })
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["status"] == "error"

    def test_actualizar_tarea_sin_titulo(self, auth_client):
        """Debe fallar si se intenta actualizar sin titulo."""
        # Crear tarea
        res = auth_client.post("/api/tareas", json={
            "titulo": "Para editar",
            "fecha": "2026-08-28"
        })
        tarea_id = json.loads(res.data)["item"]["id"]

        # Intentar actualizar sin titulo
        response = auth_client.put(f"/api/tareas/{tarea_id}", json={
            "titulo": "",
            "fecha": "2026-08-28",
            "descripcion": "Sin titulo"
        })
        assert response.status_code == 400

    def test_actualizar_sin_auth(self, client):
        """Sin autenticacion debe redirigir."""
        response = client.put("/api/tareas/1", json={
            "titulo": "Test",
            "fecha": "2026-08-28"
        })
        assert response.status_code == 302


# ============================================================
# TESTS DE API REST: ELIMINAR
# ============================================================

class TestTareasEliminar:
    """Tests de DELETE /api/tareas/<id>."""

    def test_eliminar_tarea(self, auth_client):
        """Debe eliminar una tarea."""
        # Crear tarea
        res = auth_client.post("/api/tareas", json={
            "titulo": "A eliminar",
            "fecha": "2026-08-28",
            "descripcion": "Desc"
        })
        tarea_id = json.loads(res.data)["item"]["id"]

        # Eliminar
        response = auth_client.delete(f"/api/tareas/{tarea_id}")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "ok"

        # Verificar que se elimino
        response = auth_client.get("/api/tareas")
        tareas = json.loads(response.data)
        tarea = next((t for t in tareas if t["id"] == tarea_id), None)
        assert tarea is None

    def test_eliminar_tarea_inexistente(self, auth_client):
        """Debe retornar 404 al eliminar tarea inexistente."""
        response = auth_client.delete("/api/tareas/99999")
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["status"] == "error"

    def test_eliminar_sin_auth(self, client):
        """Sin autenticacion debe redirigir."""
        response = client.delete("/api/tareas/1")
        assert response.status_code == 302


# ============================================================
# TESTS DE ORDENAMIENTO
# ============================================================

class TestTareasOrdenamiento:
    """Tests de ordenamiento de tareas."""

    def test_tareas_ordenadas_por_fecha(self, auth_client):
        """Las tareas deben estar ordenadas por fecha (mas recientes primero)."""
        auth_client.post("/api/tareas", json={
            "titulo": "Vieja",
            "fecha": "2026-01-01"
        })
        auth_client.post("/api/tareas", json={
            "titulo": "Nueva",
            "fecha": "2026-12-31"
        })

        response = auth_client.get("/api/tareas")
        tareas = json.loads(response.data)

        # Filtrar solo las que creamos
        titulos = [t["titulo"] for t in tareas]
        assert "Vieja" in titulos
        assert "Nueva" in titulos

        # La mas reciente debe estar primero
        idx_nueva = titulos.index("Nueva")
        idx_vieja = titulos.index("Vieja")
        assert idx_nueva < idx_vieja


# ============================================================
# TESTS DE FLUJO COMPLETO
# ============================================================

class TestTareasFlujoCompleto:
    """Tests de flujo completo CRUD."""

    def test_flujo_completo_tarea(self, auth_client):
        """Prueba el flujo completo: crear, listar, editar, eliminar."""
        # 1. Crear
        res = auth_client.post("/api/tareas", json={
            "titulo": "Flujo completo",
            "fecha": "2026-09-01",
            "descripcion": "Tarea de prueba de flujo"
        })
        assert res.status_code == 201
        tarea_id = json.loads(res.data)["item"]["id"]

        # 2. Verificar que existe en la lista
        response = auth_client.get("/api/tareas")
        tareas = json.loads(response.data)
        tarea = next((t for t in tareas if t["id"] == tarea_id), None)
        assert tarea is not None
        assert tarea["titulo"] == "Flujo completo"

        # 3. Editar
        response = auth_client.put(f"/api/tareas/{tarea_id}", json={
            "titulo": "Flujo editado",
            "fecha": "2026-09-02",
            "descripcion": "Tarea editada"
        })
        assert response.status_code == 200

        # 4. Verificar edicion
        response = auth_client.get("/api/tareas")
        tareas = json.loads(response.data)
        tarea = next((t for t in tareas if t["id"] == tarea_id), None)
        assert tarea is not None
        assert tarea["titulo"] == "Flujo editado"
        assert tarea["fecha"] == "2026-09-02"

        # 5. Eliminar
        response = auth_client.delete(f"/api/tareas/{tarea_id}")
        assert response.status_code == 200

        # 6. Verificar eliminacion
        response = auth_client.get("/api/tareas")
        tareas = json.loads(response.data)
        tarea = next((t for t in tareas if t["id"] == tarea_id), None)
        assert tarea is None