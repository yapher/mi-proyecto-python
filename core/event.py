"""
core/event.py — VERSIÓN SQL
Lógica reutilizable para gestión de eventos.
Ahora usa SQL directamente (no más EventStore basado en JSON).
"""
from datetime import datetime, timedelta
from core.db_sql_store import evento_store


def enviar_recordatorios_eventos(app, mail, store=None):
    """
    Envía recordatorios por email para eventos del día siguiente.
    Ahora usa SQL directamente a través de evento_store.
    """
    from flask_mail import Message
    from zoneinfo import ZoneInfo

    tz = ZoneInfo("America/Argentina/Buenos_Aires")
    with app.app_context():
        try:
            # ✅ Usar el store SQL global
            eventos = evento_store.obtener_eventos_del_dia_siguiente()
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
                            f"Hola,\n"
                            f"Te recordamos que mañana ({fecha_evento}) tenés:\n"
                            f"Título: {evento.get('titulo', '')}\n"
                            f"Descripción: {evento.get('descripcion', '')}\n"
                            f"Saludos."
                        ),
                    )
                    mail.send(msg)
                    print(f"[OK] Recordatorio enviado a {email_destino}")
                except Exception as e:
                    print(f"[ERROR] Enviando correo a {email_destino}: {e}")