"""Tests para la aplicación Instalaciones."""
import pytest
import json
import os
import io
from werkzeug.datastructures import FileStorage

TEST_USER_DATA = {
    'id': 'test_user', 'username': 'test_user',
    'password': 'test_password', 'roles': ['viewer', 'admin', 'editor']
}

@pytest.fixture
def client(app, monkeypatch):
    client = app.test_client()
    monkeypatch.setattr('auth.login.usuarios', [TEST_USER_DATA])
    monkeypatch.setattr('auth.login.usuarios_dict',
                        {TEST_USER_DATA['username']: TEST_USER_DATA})
    with client.session_transaction() as sess:
        sess['_user_id'] = TEST_USER_DATA['id']
        sess['_fresh'] = True
        sess['_id'] = 'test_session_id'
    return client

@pytest.fixture
def ubicacion_tecnica_file(tmp_path, monkeypatch):
    archivo = tmp_path / "ubicacion_tecnica.json"
    archivo.write_text(json.dumps([{
        "nombre": "Planta Principal", "emoji": "🏭", "ruta": "/planta",
        "ruta_jerarquia": "Planta Principal", "imagen": "existente.png",
        "sububicaciones": [{
            "nombre": "Sector A", "emoji": "🅰️", "ruta": "/planta/a",
            "ruta_jerarquia": "Planta Principal-Sector A",
            "imagen": "", "sububicaciones": []
        }]
    }]), encoding="utf-8")
    monkeypatch.setattr(
        "templates.Aplic.instalaciones.BackEnd.instalaciones.UBI_TEC", str(archivo))
    return archivo

@pytest.fixture
def upload_folder(tmp_path, monkeypatch, app):
    uploads = tmp_path / "templates" / "Aplic" / "instalaciones" / "static" / "img"
    uploads.mkdir(parents=True)
    monkeypatch.setattr(
        "templates.Aplic.instalaciones.BackEnd.instalaciones.UPLOAD_FOLDER", str(uploads))
    return uploads


class TestSubirImagen:
    def test_subir_imagen_png_exitoso(self, client, upload_folder):
        data = {'imagen': (io.BytesIO(b"fake_png_data"), 'test.png')}
        r = client.post('/api/subir_imagen', data=data, content_type='multipart/form-data')
        assert r.status_code == 200
        j = r.get_json()
        assert j['status'] == 'ok'
        assert j['filename'].endswith('.png')

    def test_subir_imagen_jpg_exitoso(self, client, upload_folder):
        data = {'imagen': (io.BytesIO(b"fake_jpg_data"), 'foto.jpg')}
        r = client.post('/api/subir_imagen', data=data, content_type='multipart/form-data')
        assert r.status_code == 200
        assert r.get_json()['filename'].endswith('.jpg')

    def test_subir_imagen_extension_invalida(self, client, upload_folder):
        data = {'imagen': (io.BytesIO(b"fake_exe_data"), 'virus.exe')}
        r = client.post('/api/subir_imagen', data=data, content_type='multipart/form-data')
        assert r.status_code == 400
        assert 'Formato no permitido' in r.get_json()['msg']

    def test_subir_sin_archivo(self, client):
        r = client.post('/api/subir_imagen')
        assert r.status_code == 400

    def test_subir_archivo_vacio(self, client, upload_folder):
        data = {'imagen': (io.BytesIO(b""), '')}
        r = client.post('/api/subir_imagen', data=data, content_type='multipart/form-data')
        assert r.status_code in [200, 400]


class TestReutilizacionImagenes:
    def test_no_duplicar_imagen_identica(self, client, upload_folder):
        contenido = b"contenido_imagen_identica_12345"
        data1 = {'imagen': (io.BytesIO(contenido), 'logo.png')}
        r1 = client.post('/api/subir_imagen', data=data1, content_type='multipart/form-data')
        assert r1.status_code == 200
        assert r1.get_json()['filename'] == 'logo.png'
        assert len(list(upload_folder.glob('logo*.png'))) == 1

        data2 = {'imagen': (io.BytesIO(contenido), 'logo.png')}
        r2 = client.post('/api/subir_imagen', data=data2, content_type='multipart/form-data')
        assert r2.status_code == 200
        assert r2.get_json()['filename'] == 'logo.png'
        assert len(list(upload_folder.glob('logo*.png'))) == 1

    def test_duplicar_si_contenido_diferente(self, client, upload_folder):
        data1 = {'imagen': (io.BytesIO(b"contenido_AAA"), 'logo.png')}
        r1 = client.post('/api/subir_imagen', data=data1, content_type='multipart/form-data')
        assert r1.status_code == 200
        assert r1.get_json()['filename'] == 'logo.png'

        data2 = {'imagen': (io.BytesIO(b"contenido_BBB_diferente"), 'logo.png')}
        r2 = client.post('/api/subir_imagen', data=data2, content_type='multipart/form-data')
        assert r2.status_code == 200
        nombre2 = r2.get_json()['filename']
        assert nombre2 != 'logo.png'
        assert nombre2.startswith('logo_')
        assert len(list(upload_folder.glob('logo*.png'))) == 2


class TestEditarUbicacion:
    def test_editar_con_nueva_imagen(self, client, ubicacion_tecnica_file, upload_folder):
        data = {
            'ruta_jerarquia': 'Planta Principal-Sector A',
            'nombre': 'Sector A Modificado', 'emoji': '🅰️', 'ruta': '/planta/a-nueva',
            'imagen': (io.BytesIO(b"fake_png_data"), 'nueva.png')
        }
        r = client.put('/api/editar_ubicacion', data=data, content_type='multipart/form-data')
        assert r.status_code == 200
        with open(ubicacion_tecnica_file, 'r', encoding='utf-8') as f:
            ubis = json.load(f)
        sector = ubis[0]['sububicaciones'][0]
        assert sector['nombre'] == 'Sector A Modificado'
        assert sector['imagen'].endswith('.png')

    def test_editar_sin_imagen_mantiene_actual(self, client, ubicacion_tecnica_file):
        data = {
            'ruta_jerarquia': 'Planta Principal', 'nombre': 'Planta Principal',
            'emoji': '🏭', 'ruta': '/planta', 'imagen': 'existente.png'
        }
        r = client.put('/api/editar_ubicacion', data=json.dumps(data),
                       content_type='application/json')
        assert r.status_code == 200
        with open(ubicacion_tecnica_file, 'r', encoding='utf-8') as f:
            ubis = json.load(f)
        assert ubis[0]['imagen'] == 'existente.png'

    def test_quitar_imagen_existente(self, client, ubicacion_tecnica_file):
        data = {
            'ruta_jerarquia': 'Planta Principal', 'nombre': 'Planta Principal',
            'emoji': '🏭', 'ruta': '/planta', 'eliminar_imagen': 'true'
        }
        r = client.put('/api/editar_ubicacion', data=json.dumps(data),
                       content_type='application/json')
        assert r.status_code == 200
        j = r.get_json()
        assert j['status'] == 'ok'
        assert j.get('imagen_eliminada') is True
        with open(ubicacion_tecnica_file, 'r', encoding='utf-8') as f:
            ubis = json.load(f)
        assert ubis[0]['imagen'] == ''

    def test_editar_ruta_inexistente(self, client, ubicacion_tecnica_file):
        data = {'ruta_jerarquia': 'No-Existe', 'nombre': 'Test'}
        r = client.put('/api/editar_ubicacion', data=json.dumps(data),
                       content_type='application/json')
        assert r.status_code == 404


class TestAgregarSububicacion:
    def test_agregar_con_imagen(self, client, ubicacion_tecnica_file, upload_folder):
        data = {
            'ruta_padre': 'Planta Principal', 'nombre': 'Sector Nuevo',
            'emoji': '🆕', 'ruta': '/planta/nuevo',
            'imagen': (io.BytesIO(b"fake_png_data"), 'sector.png')
        }
        r = client.post('/api/agregar_sububicacion', data=data,
                        content_type='multipart/form-data')
        assert r.status_code == 200
        with open(ubicacion_tecnica_file, 'r', encoding='utf-8') as f:
            ubis = json.load(f)
        nueva = next((s for s in ubis[0]['sububicaciones']
                      if s['nombre'] == 'Sector Nuevo'), None)
        assert nueva is not None
        assert nueva['imagen'].endswith('.png')

    def test_agregar_sin_imagen(self, client, ubicacion_tecnica_file):
        data = {
            'ruta_padre': 'Planta Principal',
            'nuevo_hijo': {'nombre': 'Sector Sin Imagen', 'emoji': '🆕', 'ruta': '/planta/sin'}
        }
        r = client.post('/api/agregar_sububicacion', data=json.dumps(data),
                        content_type='application/json')
        assert r.status_code == 200


class TestFuncionesAuxiliares:
    def test_allowed_file_valido(self):
        from templates.Aplic.instalaciones.BackEnd.instalaciones import allowed_file
        assert allowed_file('foto.png') is True
        assert allowed_file('foto.jpg') is True
        assert allowed_file('foto.jpeg') is True
        assert allowed_file('foto.gif') is True
        assert allowed_file('foto.webp') is True

    def test_allowed_file_invalido(self):
        from templates.Aplic.instalaciones.BackEnd.instalaciones import allowed_file
        assert allowed_file('archivo.exe') is False
        assert allowed_file('script.py') is False
        assert allowed_file('sin_extension') is False

    def test_procesar_imagen_exitoso(self, app, upload_folder):
        from templates.Aplic.instalaciones.BackEnd.instalaciones import procesar_imagen
        with app.app_context():
            archivo = FileStorage(stream=io.BytesIO(b"fake_image_data"),
                                  filename="test.png", content_type="image/png")
            filename, error = procesar_imagen(archivo)
            assert error is None
            assert filename is not None
            assert filename.endswith('.png')
            assert os.path.exists(os.path.join(str(upload_folder), filename))

    def test_procesar_imagen_extension_invalida(self, app, upload_folder):
        from templates.Aplic.instalaciones.BackEnd.instalaciones import procesar_imagen
        with app.app_context():
            archivo = FileStorage(stream=io.BytesIO(b"fake"),
                                  filename="virus.exe", content_type="application/octet-stream")
            filename, error = procesar_imagen(archivo)
            assert filename is None
            assert 'Formato no permitido' in error

    def test_procesar_imagen_vacia(self, app, upload_folder):
        from templates.Aplic.instalaciones.BackEnd.instalaciones import procesar_imagen
        with app.app_context():
            archivo = FileStorage(stream=io.BytesIO(b""), filename="")
            filename, error = procesar_imagen(archivo)
            assert filename is None
            assert error is None

    def test_calcular_hash_archivo(self, app, upload_folder):
        from templates.Aplic.instalaciones.BackEnd.instalaciones import (
            calcular_hash_archivo, calcular_hash_bytes)
        contenido = b"contenido_de_prueba_para_hash"
        ruta = os.path.join(str(upload_folder), "test_hash.txt")
        with open(ruta, "wb") as f: f.write(contenido)
        assert calcular_hash_archivo(ruta) == calcular_hash_bytes(contenido)

    def test_calcular_hash_archivo_no_existe(self, app, upload_folder):
        from templates.Aplic.instalaciones.BackEnd.instalaciones import calcular_hash_archivo
        with app.app_context():
            assert calcular_hash_archivo("/ruta/inexistente/archivo.txt") is None