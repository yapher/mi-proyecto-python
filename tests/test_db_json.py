"""
Tests del módulo genérico db_json.JsonStore.
Son autocontenidos: usan 'tmp_path' (fixture nativo de pytest),
por lo que NO tocan los JSON reales de DataBase/.
Ejecutar con:  pytest tests/test_db_json.py -v
"""
import json
import sys
from pathlib import Path

# Asegura que la raíz del proyecto esté en el path
sys.path.insert(0, str(Path(__file__).parent.parent))

# ✅ Import actualizado: ahora desde core.db_json (no desde la raíz)
from core.db_json import JsonStore


# =========================================================
# Fixtures
# =========================================================
def make_store(tmp_path):
    """Crea un JsonStore apuntando a un JSON temporal."""
    return JsonStore(str(tmp_path / "test_data.json"))


def store_vacio(tmp_path):
    """Store sin archivo todavía."""
    return make_store(tmp_path)


def store_con_datos(tmp_path):
    """Store precargado con 2 items."""
    store = make_store(tmp_path)
    store.guardar([
        {"id": 1, "titulo": "Evento 1", "realizado": False},
        {"id": 2, "titulo": "Evento 2", "realizado": True},
    ])
    return store


# =========================================================
# cargar()
# =========================================================
def test_cargar_archivo_no_existe(tmp_path):
    """Si el archivo no existe, devuelve lista vacía."""
    store = store_vacio(tmp_path)
    assert store.cargar() == []


def test_cargar_archivo_valido(tmp_path):
    """Lee correctamente una lista de items."""
    store = store_con_datos(tmp_path)
    datos = store.cargar()
    assert len(datos) == 2
    assert datos[0]["titulo"] == "Evento 1"


def test_cargar_archivo_corrupto(tmp_path):
    """Si el JSON está corrupto, devuelve lista vacía (no lanza excepción)."""
    store = make_store(tmp_path)
    with open(store.db_path, "w", encoding="utf-8") as f:
        f.write("{esto no es json válido")
    assert store.cargar() == []


def test_cargar_archivo_no_es_lista(tmp_path):
    """Si el JSON contiene algo que no es lista, devuelve lista vacía."""
    store = make_store(tmp_path)
    with open(store.db_path, "w", encoding="utf-8") as f:
        json.dump({"clave": "valor"}, f)
    assert store.cargar() == []


# =========================================================
# guardar()
# =========================================================
def test_guardar_crea_archivo(tmp_path):
    """guardar() crea el archivo si no existe."""
    store = store_vacio(tmp_path)
    store.guardar([{"id": 1, "titulo": "Nuevo"}])
    assert Path(store.db_path).exists()
    assert store.cargar() == [{"id": 1, "titulo": "Nuevo"}]


def test_guardar_crea_directorio(tmp_path):
    """guardar() crea los directorios intermedios si no existen."""
    ruta = tmp_path / "sub" / "carpeta" / "data.json"
    store = JsonStore(str(ruta))
    store.guardar([{"id": 1}])
    assert ruta.exists()


# =========================================================
# agregar()
# =========================================================
def test_agregar_asigna_id_incremental(tmp_path):
    """agregar() asigna el siguiente ID disponible."""
    store = store_con_datos(tmp_path)
    nuevo = store.agregar({"titulo": "Evento 3"})
    assert nuevo["id"] == 3
    assert len(store.cargar()) == 3


def test_agregar_en_vacio_id_es_1(tmp_path):
    """El primer item agregado tiene id=1."""
    store = store_vacio(tmp_path)
    nuevo = store.agregar({"titulo": "Primero"})
    assert nuevo["id"] == 1


def test_agregar_con_defaults(tmp_path):
    """agregar() aplica 'defaults' solo a campos que faltan."""
    store = store_vacio(tmp_path)
    nuevo = store.agregar(
        {"titulo": "Con default"},
        defaults={"realizado": False, "descripcion": ""},
    )
    assert nuevo["realizado"] is False
    assert nuevo["descripcion"] == ""


def test_agregar_defaults_no_pisa_valor_existente(tmp_path):
    """agregar() NO sobrescribe campos ya presentes."""
    store = store_vacio(tmp_path)
    nuevo = store.agregar(
        {"titulo": "Ya tiene realizado", "realizado": True},
        defaults={"realizado": False},
    )
    assert nuevo["realizado"] is True


# =========================================================
# editar()
# =========================================================
def test_editar_actualiza_campos(tmp_path):
    """editar() actualiza solo los campos indicados."""
    store = store_con_datos(tmp_path)
    store.editar(1, {"titulo": "Título cambiado"})
    datos = store.cargar()
    assert datos[0]["titulo"] == "Título cambiado"
    # Los demás campos se mantienen
    assert datos[0]["realizado"] is False


def test_editar_no_modifica_otros_items(tmp_path):
    """editar() solo toca el item con el id indicado."""
    store = store_con_datos(tmp_path)
    store.editar(1, {"titulo": "Cambiado"})
    datos = store.cargar()
    assert datos[1]["titulo"] == "Evento 2"


def test_editar_id_inexistente_no_rompe(tmp_path):
    """editar() con id inexistente no lanza excepción."""
    store = store_con_datos(tmp_path)
    store.editar(999, {"titulo": "No existe"})
    assert len(store.cargar()) == 2


def test_editar_con_ensure_fields(tmp_path):
    """editar() con ensure_fields setea campos si faltan tras el update."""
    store = store_vacio(tmp_path)
    store.guardar([{"id": 1, "titulo": "Sin realizado"}])
    store.editar(1, {"titulo": "Actualizado"}, ensure_fields={"realizado": False})
    datos = store.cargar()
    assert datos[0]["realizado"] is False


# =========================================================
# eliminar()
# =========================================================
def test_eliminar_por_id(tmp_path):
    """eliminar() quita el item con el id indicado."""
    store = store_con_datos(tmp_path)
    store.eliminar(1)
    datos = store.cargar()
    assert len(datos) == 1
    assert datos[0]["id"] == 2


def test_eliminar_id_inexistente_no_rompe(tmp_path):
    """eliminar() con id inexistente no lanza excepción."""
    store = store_con_datos(tmp_path)
    store.eliminar(999)
    assert len(store.cargar()) == 2


def test_eliminar_ultimo_item(tmp_path):
    """eliminar() el único item deja lista vacía."""
    store = store_vacio(tmp_path)
    store.agregar({"titulo": "Único"})
    store.eliminar(1)
    assert store.cargar() == []