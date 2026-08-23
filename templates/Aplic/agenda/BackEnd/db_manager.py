import json
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from flask_mail import Message
from db_json import JsonStore

DB_PATH = "DataBase/time/agenda.json"
_store = JsonStore(DB_PATH)


def cargar_eventos():
    return _store.cargar()


def guardar_eventos(eventos):
    _store.guardar(eventos)


def agregar_evento(evento):
    # Mantiene el comportamiento original: asegura campo 'realizado'
    return _store.agregar(evento, defaults={"realizado": False})


def editar_evento(evento_id, nuevos_datos):
    # Mantiene el comportamiento original: asegura 'realizado' si falta
    _store.editar(evento_id, nuevos_datos, ensure_fields={"realizado": False})


def eliminar_evento(evento_id):
    _store.eliminar(evento_id)


# =========================
# Job para recordatorios
# =========================
def enviar_recordatorios(app, mail, cargar_eventos_func=cargar_eventos):
    """Envía recordatorios por email para eventos del día siguiente."""
    tz = ZoneInfo("America/Argentina/Buenos_Aires")
    with app.app_context():
        try:
            eventos = cargar_eventos_func()
        except Exception as e:
            print(f"[ERROR] No se pudieron cargar eventos: {e}")
            return

        ahora = datetime.now(tz)
        manana = (ahora + timedelta(days=1)).date()

        for evento in eventos:
            try:
                fecha_evento = datetime.strptime(evento["fecha"], "%Y-%m-%d").date()
            except Exception:
                continue

            if fecha_evento == manana and not evento.get("realizado", False):
                email_destino = evento.get("email")
                if not email_destino:
                    continue

                try:
                    msg = Message(
                        subject=f"Recordatorio: {evento.get('titulo', 'Evento')}",
                        recipients=[email_destino],
                        body=(
                            f"Hola,\n\n"
                            f"Te recordamos que mañana ({fecha_evento}) tenés:\n\n"
                            f"Título: {evento.get('titulo', '')}\n"
                            f"Descripción: {evento.get('descripcion', '')}\n\n"
                            f"Saludos."
                        ),
                    )
                    mail.send(msg)
                    print(f"[OK] Recordatorio enviado a {email_destino}")
                except Exception as e:
                    print(f"[ERROR] Enviando correo a {email_destino}: {e}")