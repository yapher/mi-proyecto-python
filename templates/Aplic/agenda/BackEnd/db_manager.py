import json
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from flask_mail import Message

DB_PATH = "DataBase/time/agenda.json"

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
    evento["realizado"] = evento.get("realizado", False)  # nuevo campo
    eventos.append(evento)
    guardar_eventos(eventos)

def editar_evento(evento_id, nuevos_datos):
    eventos = cargar_eventos()
    for evento in eventos:
        if evento["id"] == evento_id:
            evento.update(nuevos_datos)
            if "realizado" not in evento:
                evento["realizado"] = False
            break
    guardar_eventos(eventos)

def eliminar_evento(evento_id):
    eventos = cargar_eventos()
    eventos = [e for e in eventos if e["id"] != evento_id]
    guardar_eventos(eventos)

# =========================
# Job para recordatorios
# =========================
def enviar_recordatorios(app, mail, cargar_eventos_func=cargar_eventos):
    """
    Debe ser llamado por APScheduler pasando `app` y `mail`.
    Ejecuta dentro de app.app_context() para que Flask-Mail tenga contexto.
    """
    # Zona horaria del usuario (AR)
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
                # Salta eventos con fecha inválida
                continue

            if fecha_evento == manana:
                email_destino = evento.get("email", app.config.get("MAIL_DEFAULT_SENDER"))
                titulo = evento.get("titulo", "Evento")
                descripcion = evento.get("descripcion", "")

                # IMPORTANTE: setear sender explícito evita que Flask-Mail busque default_sender fuera de contexto
                msg = Message(
                    subject=f"⏰ Recordatorio: {titulo} es mañana",
                    recipients=[email_destino],
                    sender=app.config.get("MAIL_DEFAULT_SENDER"),
                    body=(
                        "Hola!\n\n"
                        f"Te recordamos que mañana ({fecha_evento.strftime('%d/%m/%Y')}) tienes el evento:\n\n"
                        f"{titulo}\n{descripcion}\n\n"
                        "— Agenda"
                    ),
                )

                try:
                    mail.send(msg)
                    print(f"[OK] Recordatorio enviado a {email_destino}")
                except Exception as e:
                    print(f"[ERROR] Enviando correo a {email_destino}: {e}")
