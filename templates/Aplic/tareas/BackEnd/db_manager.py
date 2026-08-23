import json
import os
from db_json import JsonStore

DB_PATH = "DataBase/time/dataTask.json"
_store = JsonStore(DB_PATH)


def cargar_eventos():
    return _store.cargar()


def guardar_eventos(eventos):
    _store.guardar(eventos)


def agregar_evento(evento):
    return _store.agregar(evento)


def editar_evento(evento_id, nuevos_datos):
    _store.editar(evento_id, nuevos_datos)


def eliminar_evento(evento_id):
    _store.eliminar(evento_id)