import json
import os

DB_PATH = "DataBase/time/dataTask.json"

def cargar_eventos():
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_eventos(eventos):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(eventos, f, indent=4, ensure_ascii=False)

def agregar_evento(evento):
    eventos = cargar_eventos()
    evento["id"] = max([e["id"] for e in eventos], default=0) + 1
    eventos.append(evento)
    guardar_eventos(eventos)

def editar_evento(evento_id, nuevos_datos):
    eventos = cargar_eventos()
    for evento in eventos:
        if evento["id"] == evento_id:
            evento.update(nuevos_datos)
            break
    guardar_eventos(eventos)

def eliminar_evento(evento_id):
    eventos = cargar_eventos()
    eventos = [e for e in eventos if e["id"] != evento_id]
    guardar_eventos(eventos)
