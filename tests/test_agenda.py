class TestAgendaRoutes:
    """Tests para las rutas HTTP de la agenda."""
    
    def test_index_agenda(self, auth_client):
        """La vista principal debe renderizar correctamente."""
        response = auth_client.get('/agenda/')
        assert response.status_code == 200
        assert b'Agenda Mensual' in response.data
    
    def test_listar_eventos_vacio(self, auth_client):
        """Listar eventos cuando no hay ninguno."""
        response = auth_client.get('/agenda/eventos')
        assert response.status_code == 200
        data = response.get_json()
        assert data == []
    
    def test_crear_evento(self, auth_client):
        """Crear un nuevo evento."""
        response = auth_client.post('/agenda/evento', json={
            'titulo': 'Test',
            'fecha': '2026-08-28',
            'email': 'test@example.com'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['status'] == 'ok'
        assert 'evento' in data
    
    def test_crear_evento_sin_campos(self, auth_client):
        """Crear un evento sin campos requeridos."""
        response = auth_client.post('/agenda/evento', json={})
        assert response.status_code == 400
    
    def test_editar_evento(self, auth_client):
        """Editar un evento existente."""
        # Crear primero
        res = auth_client.post('/agenda/evento', json={
            'titulo': 'Original',
            'fecha': '2026-08-28'
        })
        evento_id = res.get_json()['evento']['id']
        
        # Editar
        response = auth_client.put(f'/agenda/evento/{evento_id}', json={
            'titulo': 'Editado'
        })
        assert response.status_code == 200
    
    def test_eliminar_evento(self, auth_client):
        """Eliminar un evento."""
        # Crear primero
        res = auth_client.post('/agenda/evento', json={
            'titulo': 'A eliminar',
            'fecha': '2026-08-28'
        })
        evento_id = res.get_json()['evento']['id']
        
        # Eliminar
        response = auth_client.delete(f'/agenda/evento/{evento_id}')
        assert response.status_code == 200
    
    def test_toggle_realizado(self, auth_client):
        """Alternar el estado realizado."""
        # Crear
        res = auth_client.post('/agenda/evento', json={
            'titulo': 'Test',
            'fecha': '2026-08-28'
        })
        evento_id = res.get_json()['evento']['id']
        
        # Toggle
        response = auth_client.patch(f'/agenda/evento/{evento_id}/toggle')
        assert response.status_code == 200
        data = response.get_json()
        assert data['realizado'] == True