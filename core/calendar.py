"""
core/calendar.py
================
Lógica reutilizable para generación de calendarios mensuales.
Puede ser importada por cualquier aplicación que necesite un calendario.

Uso:
    from core.calendar import generar_calendario, obtener_dias_mes
    
    calendario = generar_calendario(2026, 8)
"""
from datetime import date, timedelta
import calendar


def obtener_dias_mes(year: int, month: int) -> int:
    """Retorna la cantidad de días de un mes específico."""
    return calendar.monthrange(year, month)[1]


def obtener_primer_dia_semana(year: int, month: int) -> int:
    """
    Retorna el día de la semana del primer día del mes (0=Lunes ... 6=Domingo).
    Compatible con la convención ISO de Python.
    """
    return date(year, month, 1).weekday()


def generar_calendario(year: int, month: int, eventos_por_fecha: dict = None) -> list:
    """
    Genera una estructura de calendario mensual como lista de semanas.
    Cada semana es una lista de 7 días (lunes a domingo).
    
    Args:
        year: Año del calendario
        month: Mes del calendario (1-12)
        eventos_por_fecha: Diccionario opcional { 'YYYY-MM-DD': [eventos] }
    
    Returns:
        Lista de semanas, donde cada semana es una lista de 7 dicts:
        [
            {
                'dia': 1-31 o None (si es espacio vacío),
                'fecha': 'YYYY-MM-DD' o None,
                'es_hoy': bool,
                'eventos': [lista de eventos para ese día]
            },
            ... (7 días por semana)
        ]
    """
    eventos_por_fecha = eventos_por_fecha or {}
    hoy = date.today()
    
    dias_mes = obtener_dias_mes(year, month)
    primer_dia = obtener_primer_dia_semana(year, month)
    
    semanas = []
    semana_actual = []
    
    # Espacios vacíos antes del primer día del mes
    for _ in range(primer_dia):
        semana_actual.append({
            'dia': None,
            'fecha': None,
            'es_hoy': False,
            'eventos': []
        })
    
    # Días del mes
    for dia in range(1, dias_mes + 1):
        fecha = date(year, month, dia)
        fecha_str = fecha.strftime('%Y-%m-%d')
        
        semana_actual.append({
            'dia': dia,
            'fecha': fecha_str,
            'es_hoy': (fecha == hoy),
            'eventos': eventos_por_fecha.get(fecha_str, [])
        })
        
        # Si la semana está completa (7 días), guardarla
        if len(semana_actual) == 7:
            semanas.append(semana_actual)
            semana_actual = []
    
    # Completar la última semana si quedó incompleta
    if semana_actual:
        while len(semana_actual) < 7:
            semana_actual.append({
                'dia': None,
                'fecha': None,
                'es_hoy': False,
                'eventos': []
            })
        semanas.append(semana_actual)
    
    return semanas


def obtener_meses():
    """Retorna lista de meses para selects."""
    meses = [
        (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
        (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
        (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
    ]
    return meses


def obtener_rango_anios(inicio: int = 2020, fin: int = None) -> list:
    """Retorna lista de años para selects."""
    if fin is None:
        fin = date.today().year + 5
    return list(range(inicio, fin + 1))