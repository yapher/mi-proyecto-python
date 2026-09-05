"""
core/mes_store.py
=================
Módulo reutilizable para gestión de datos mensuales en archivos JSON.
Encapsula la lógica de:
  - Leer/guardar archivos mensuales (GASTO_YYYY_MM.json)
  - Sincronización entre archivo general y mensuales
  - Clonación de datos entre meses
  - Cálculo de totales y agregaciones

Usado por:
  - pagos (gestión de gastos mensuales)
  - estadisticas (análisis de gastos por mes)
  - (futuras apps que necesiten datos mensuales)

Uso:
    from core.mes_store import MesStore
    
    store = MesStore(base_dir='DataBase/hogar')
    
    # Leer pagos de un mes
    pagos = store.leer_mes(2026, 9)
    
    # Guardar pagos de un mes
    store.guardar_mes(2026, 9, pagos)
    
    # Clonar mes
    store.clonar_mes(2026, 8, 2026, 9)
    
    # Totales por rubro
    totales = store.totales_por_rubro(2026, 9, campo_rubro='rubro', campo_importe='importe')
"""
import os
import json
from datetime import datetime
from calendar import monthrange
from typing import List, Dict, Optional, Tuple


class MesStore:
    """
    Gestor de datos mensuales en archivos JSON.
    
    Estructura de archivos:
      - Archivo general: {base_dir}/{archivo_general}.json
      - Archivos mensuales: {base_dir}/{prefijo}_{YYYY}_{MM}.json
    
    Ejemplo:
      base_dir='DataBase/hogar'
      archivo_general='GASTOS'
      prefijo='GASTO'
      
      → DataBase/hogar/GASTOS.json
      → DataBase/hogar/GASTO_2026_09.json
    """
    
    def __init__(
        self,
        base_dir: str = 'DataBase/hogar',
        archivo_general: str = 'GASTOS',
        prefijo_mensual: str = 'GASTO'
    ):
        """
        Inicializa el MesStore.
        
        Args:
            base_dir: Directorio base donde se guardan los archivos
            archivo_general: Nombre del archivo general (sin extensión)
            prefijo_mensual: Prefijo de los archivos mensuales
        """
        self.base_dir = base_dir
        self.archivo_general = archivo_general
        self.prefijo_mensual = prefijo_mensual
        
        # Asegurar que el directorio exista
        os.makedirs(self.base_dir, exist_ok=True)
    
    # ============================================================
    # RUTAS DE ARCHIVOS
    # ============================================================
    
    def ruta_general(self) -> str:
        """Retorna la ruta del archivo general."""
        return os.path.join(self.base_dir, f'{self.archivo_general}.json')
    
    def ruta_mes(self, anio: int, mes: int) -> str:
        """
        Retorna la ruta del archivo de un mes específico.
        
        Args:
            anio: Año (ej: 2026)
            mes: Mes (1-12)
        
        Returns:
            Ruta completa al archivo (ej: DataBase/hogar/GASTO_2026_09.json)
        """
        return os.path.join(
            self.base_dir,
            f'{self.prefijo_mensual}_{anio}_{mes:02d}.json'
        )
    
    # ============================================================
    # OPERACIONES BÁSICAS: ARCHIVO GENERAL
    # ============================================================
    
    def leer_general(self) -> List[Dict]:
        """Lee todos los datos del archivo general."""
        ruta = self.ruta_general()
        if not os.path.exists(ruta):
            return []
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError) as e:
            print(f"[ERROR] Leyendo {ruta}: {e}")
            return []
    
    def guardar_general(self, data: List[Dict]) -> None:
        """Guarda datos en el archivo general."""
        ruta = self.ruta_general()
        try:
            with open(ruta, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except OSError as e:
            print(f"[ERROR] Guardando {ruta}: {e}")
            raise
    
    # ============================================================
    # OPERACIONES BÁSICAS: ARCHIVOS MENSUALES
    # ============================================================
    
    def leer_mes(self, anio: int, mes: int) -> List[Dict]:
        """
        Lee los datos de un mes específico.
        
        Args:
            anio: Año (ej: 2026)
            mes: Mes (1-12)
        
        Returns:
            Lista de registros del mes
        """
        ruta = self.ruta_mes(anio, mes)
        if not os.path.exists(ruta):
            return []
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError) as e:
            print(f"[ERROR] Leyendo {ruta}: {e}")
            return []
    
    def guardar_mes(self, anio: int, mes: int, data: List[Dict]) -> None:
        """
        Guarda datos en un archivo mensual específico.
        
        Args:
            anio: Año (ej: 2026)
            mes: Mes (1-12)
            data: Lista de registros a guardar
        """
        ruta = self.ruta_mes(anio, mes)
        try:
            with open(ruta, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except OSError as e:
            print(f"[ERROR] Guardando {ruta}: {e}")
            raise
    
    def existe_mes(self, anio: int, mes: int) -> bool:
        """Verifica si existe un archivo para el mes especificado."""
        return os.path.exists(self.ruta_mes(anio, mes))
    
    # ============================================================
    # OPERACIONES AVANZADAS
    # ============================================================
    
    def agregar_a_mes(self, anio: int, mes: int, registro: Dict) -> None:
        """
        Agrega un registro al mes correspondiente.
        Si ya existe un registro con el mismo ID, lo reemplaza.
        
        Args:
            anio: Año
            mes: Mes
            registro: Registro a agregar (debe tener campo 'id')
        """
        data = self.leer_mes(anio, mes)
        
        # Reemplazar si ya existe el ID
        registro_id = registro.get('id')
        if registro_id is not None:
            data = [r for r in data if r.get('id') != registro_id]
        
        data.append(registro)
        self.guardar_mes(anio, mes, data)
    
    def eliminar_de_mes(self, anio: int, mes: int, registro_id) -> bool:
        """
        Elimina un registro de un mes específico.
        
        Args:
            anio: Año
            mes: Mes
            registro_id: ID del registro a eliminar
        
        Returns:
            True si se eliminó, False si no se encontró
        """
        data = self.leer_mes(anio, mes)
        data_filtrada = [r for r in data if r.get('id') != registro_id]
        
        if len(data_filtrada) < len(data):
            self.guardar_mes(anio, mes, data_filtrada)
            return True
        return False
    
    def actualizar_en_mes(self, anio: int, mes: int, registro: Dict) -> bool:
        """
        Actualiza un registro en un mes específico.
        
        Args:
            anio: Año
            mes: Mes
            registro: Registro actualizado (debe tener campo 'id')
        
        Returns:
            True si se actualizó, False si no se encontró
        """
        data = self.leer_mes(anio, mes)
        registro_id = registro.get('id')
        
        for i, r in enumerate(data):
            if r.get('id') == registro_id:
                data[i].update(registro)
                self.guardar_mes(anio, mes, data)
                return True
        
        return False
    
    # ============================================================
    # CLONACIÓN
    # ============================================================
    
    def clonar_mes(
        self,
        anio_origen: int,
        mes_origen: int,
        anio_destino: int,
        mes_destino: int,
        resetear_pagado: bool = True
    ) -> Tuple[int, List[Dict]]:
        """
        Clona todos los registros de un mes a otro.
        
        Args:
            anio_origen: Año de origen
            mes_origen: Mes de origen
            anio_destino: Año de destino
            mes_destino: Mes de destino
            resetear_pagado: Si True, marca todos los registros como no pagados
        
        Returns:
            Tupla (cantidad_clonada, lista_de_registros_clonados)
        
        Raises:
            ValueError: Si no hay datos en el mes de origen
        """
        data_origen = self.leer_mes(anio_origen, mes_origen)
        
        if not data_origen:
            raise ValueError(f"No hay datos en {anio_origen}/{mes_origen:02d}")
        
        # Calcular último día del mes destino
        ultimo_dia = monthrange(anio_destino, mes_destino)[1]
        
        # Clonar registros
        registros_clonados = []
        timestamp_base = int(datetime.now().timestamp() * 1000)
        
        for i, registro in enumerate(data_origen):
            nuevo = dict(registro)
            
            # Generar nuevo ID único
            nuevo['id'] = timestamp_base + i
            
            # Ajustar fecha de vencimiento
            try:
                fecha_origen = datetime.strptime(registro.get('vencimiento', ''), "%Y-%m-%d")
                dia_original = fecha_origen.day
                dia_final = min(dia_original, ultimo_dia)
                nuevo['vencimiento'] = f"{anio_destino}-{mes_destino:02d}-{dia_final:02d}"
            except (ValueError, KeyError):
                # Si no hay fecha válida, usar el último día del mes
                nuevo['vencimiento'] = f"{anio_destino}-{mes_destino:02d}-{ultimo_dia:02d}"
            
            # Resetear estado de pago si se solicita
            if resetear_pagado:
                nuevo['pagado'] = False
            
            registros_clonados.append(nuevo)
        
        # Guardar en mes destino
        data_destino = self.leer_mes(anio_destino, mes_destino)
        data_destino.extend(registros_clonados)
        self.guardar_mes(anio_destino, mes_destino, data_destino)
        
        # También agregar al archivo general
        data_general = self.leer_general()
        data_general.extend(registros_clonados)
        self.guardar_general(data_general)
        
        return len(registros_clonados), registros_clonados
    
    # ============================================================
    # AGREGACIONES Y CONSULTAS
    # ============================================================
    
    def totales_por_rubro(
        self,
        anio: int,
        mes: int,
        campo_rubro: str = 'rubro',
        campo_importe: str = 'importe'
    ) -> Dict[str, float]:
        """
        Calcula totales agrupados por rubro en un mes específico.
        
        Args:
            anio: Año
            mes: Mes
            campo_rubro: Nombre del campo que contiene el rubro
            campo_importe: Nombre del campo que contiene el importe
        
        Returns:
            Diccionario {rubro: total_importe}
        """
        data = self.leer_mes(anio, mes)
        totales = {}
        
        for registro in data:
            rubro = registro.get(campo_rubro, 'Sin Rubro')
            importe = registro.get(campo_importe, 0)
            
            try:
                importe = float(importe)
            except (ValueError, TypeError):
                importe = 0.0
            
            totales[rubro] = totales.get(rubro, 0.0) + importe
        
        return totales
    
    def total_mes(
        self,
        anio: int,
        mes: int,
        campo_importe: str = 'importe'
    ) -> float:
        """
        Calcula el total de un mes específico.
        
        Args:
            anio: Año
            mes: Mes
            campo_importe: Nombre del campo que contiene el importe
        
        Returns:
            Total del mes
        """
        data = self.leer_mes(anio, mes)
        total = 0.0
        
        for registro in data:
            importe = registro.get(campo_importe, 0)
            try:
                total += float(importe)
            except (ValueError, TypeError):
                pass
        
        return round(total, 2)
    
    def listar_meses_disponibles(self) -> List[Tuple[int, int]]:
        """
        Lista todos los meses que tienen archivos de datos.
        
        Returns:
            Lista de tuplas (anio, mes) ordenadas cronológicamente
        """
        meses = []
        
        if not os.path.exists(self.base_dir):
            return meses
        
        patron = f'{self.prefijo_mensual}_'
        
        for archivo in os.listdir(self.base_dir):
            if archivo.startswith(patron) and archivo.endswith('.json'):
                # Extraer año y mes del nombre del archivo
                try:
                    nombre = archivo.replace(patron, '').replace('.json', '')
                    partes = nombre.split('_')
                    if len(partes) == 2:
                        anio = int(partes[0])
                        mes = int(partes[1])
                        meses.append((anio, mes))
                except (ValueError, IndexError):
                    continue
        
        # Ordenar cronológicamente
        meses.sort(reverse=True)
        return meses
    
    # ============================================================
    # SINCRONIZACIÓN
    # ============================================================
    
    def sincronizar_registro(self, registro: Dict) -> None:
        """
        Sincroniza un registro entre el archivo general y el mensual.
        Útil cuando se actualiza un registro y hay que reflejarlo en ambos archivos.
        
        Args:
            registro: Registro actualizado (debe tener 'id' y 'vencimiento')
        """
        registro_id = registro.get('id')
        vencimiento = registro.get('vencimiento')
        
        if not registro_id or not vencimiento:
            return
        
        # Extraer año y mes de la fecha de vencimiento
        try:
            fecha = datetime.strptime(vencimiento, "%Y-%m-%d")
            anio = fecha.year
            mes = fecha.month
        except ValueError:
            return
        
        # Actualizar en archivo general
        data_general = self.leer_general()
        for i, r in enumerate(data_general):
            if r.get('id') == registro_id:
                data_general[i].update(registro)
                break
        self.guardar_general(data_general)
        
        # Actualizar en archivo mensual
        self.actualizar_en_mes(anio, mes, registro)