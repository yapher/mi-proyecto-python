# core/scheduler.py
"""Configuración centralizada del scheduler (recordatorios de agenda)."""
from apscheduler.schedulers.background import BackgroundScheduler
from functools import partial
from core.event import EventStore, enviar_recordatorios_eventos


def setup_scheduler(app, mail):
    """Crea y configura el scheduler. NO lo inicia (lo hace el caller)."""
    event_store = EventStore('DataBase/time/agenda.json')
    
    scheduler = BackgroundScheduler(timezone="America/Argentina/Buenos_Aires")
    
    job_func = partial(
        enviar_recordatorios_eventos,
        app=app,
        mail=mail,
        store=event_store
    )
    
    scheduler.add_job(job_func, "cron", hour=8, minute=0)
    return scheduler