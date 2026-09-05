"""
core/event.py
=============
Lógica reutilizable para gestión de eventos (CRUD sobre JSON).
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from core.db_json import JsonStore


class EventStore:
    CAMPOS_REQUERIDOS = ['titulo', 'fecha']
    PRIORIDADES_VALIDAS = ['alta', 'media', 'baja']
    
    def __init__(self, db_path: str):
        self._store = JsonStore(db_path)
        self.db_path = db_path
    
    def listar(self) -> List[Dict]:
        return self._store.cargar()
    
    def obtener(self, evento_id: int) -> Optional[Dict]:
        return self._store.buscar_uno(id=evento_id)
    
    def agregar(self, data: Dict) -> Dict:
        self._validar(data)
        defaults = {
            'descripcion': '',
            'email': '',
            'realizado': False,
            'prioridad': 'media'
        }
        return self._store.agregar(data, defaults=defaults)
    
    def editar(self, evento_id: int, nuevos_datos: Dict) -> bool:
        if not self._store.existe(evento_id):
            return False
        self._store.editar(evento_id, nuevos_datos, ensure_fields={'realizado': False})
        return True
    
    def eliminar(self, evento_id: int) -> bool:
        if not self._store.existe(evento_id):
            return False
        self._store.eliminar(evento_id)
        return True
    
    def toggle_realizado(self, evento_id: int) -> Optional[bool]:
        evento = self.obtener(evento_id)
        if not evento:
            return None
        nuevo_estado = not evento.get('realizado', False)
        self._store.editar(evento_id, {'realizado': nuevo_estado})
        return nuevo_estado
    
    def obtener_por_fecha(self, fecha: str) -> List[Dict]:
        return self._store.buscar(fecha=fecha)
    
    def obtener_pendientes(self) -> List[Dict]:
        return [e for e in self.listar() if not e.get('realizado', False)]
    
    def agrupar_por_fecha(self) -> Dict[str, List[Dict]]:
        agrupado = {}
        for evento in self.listar():
            fecha = evento.get('fecha')
            if fecha:
                agrupado.setdefault(fecha, []).append(evento)
        return agrupado
    
    def obtener_eventos_del_dia_siguiente(self) -> List[Dict]:
        manana = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        return [
            e for e in self.listar()
            if e.get('fecha') == manana and not e.get('realizado', False)
        ]
    
    def _validar(self, data: Dict):
        for campo in self.CAMPOS_REQUERIDOS:
            if not data.get(campo):
                raise ValueError(f"El campo '{campo}' es requerido")
        try:
            datetime.strptime(data['fecha'], '%Y-%m-%d')
        except ValueError:
            raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD")


def enviar_recordatorios_eventos(app, mail, store: EventStore):
    """Envía recordatorios por email para eventos del día siguiente."""
    from flask_mail import Message
    from zoneinfo import ZoneInfo
    
    tz = ZoneInfo("America/Argentina/Buenos_Aires")
    
    with app.app_context():
        try:
            eventos = store.obtener_eventos_del_dia_siguiente()
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
                            f"Te recordamos que mañana ({fecha_evento}) tenés:\n"
                            f"Título: {evento.get('titulo', '')}\n"
                            f"Descripción: {evento.get('descripcion', '')}\n\n"
                            f"Saludos."
                        ),
                    )
                    mail.send(msg)
                    print(f"[OK] Recordatorio enviado a {email_destino}")
                except Exception as e:
                    print(f"[ERROR] Enviando correo a {email_destino}: {e}")