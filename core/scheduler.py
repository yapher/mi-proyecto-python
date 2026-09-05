# core/scheduler.py - VERSIÓN SQL
"""Configuración centralizada del scheduler (recordatorios de agenda).
Ahora usa SQL en lugar de JSON.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from functools import partial
from core.event import enviar_recordatorios_eventos


def setup_scheduler(app, mail):
    """Crea y configura el scheduler. NO lo inicia (lo hace el caller)."""
    scheduler = BackgroundScheduler(timezone="America/Argentina/Buenos_Aires")
    job_func = partial(
        enviar_recordatorios_eventos,
        app=app,
        mail=mail,
        store=None  # Ya no se usa, la función lee de SQL directamente
    )
    scheduler.add_job(job_func, "cron", hour=8, minute=0)
    return scheduler