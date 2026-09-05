"""
core/db_sql_store.py
====================
Stores SQL que reemplazan a los JSON stores.
Mantienen la MISMA API pública para migrar módulo por módulo.

Stores disponibles:
- SQLStore: reemplaza JsonStore (listas planas con ID autoincremental)
- ArbolSQLStore: reemplaza lógica de arbol_bp.py (árboles jerárquicos)
- EventSQLStore: reemplaza EventStore (agenda)
- RepuestoSQLStore: reemplaza UniqueFieldStore(codigo) (repuestos)
- PagoSQLStore: reemplaza MesStore (pagos mensuales)
- NodoBloqueoSQLStore: reemplaza lógica de gestion_de_bloqueos.py
"""
import json
import re
from datetime import datetime
from calendar import monthrange
from sqlalchemy import func
from core.db_sql import db
from core.models import (
    Menu, Rubro, Almacen, Ubicacion, Tab, Estado,
    Repuesto, Pago, NodoBloqueo, Evento, Tarea
)


# ============================================================
# 1. SQLStore - Reemplaza JsonStore (listas planas con ID)
# ============================================================
class SQLStore:
    """
    Store SQL genérico que imita la API de JsonStore.
    Útil para listas planas con campo 'id' autoincremental.
    """
    def __init__(self, model_class):
        self.model = model_class

    def cargar(self):
        """Retorna todos los items como lista de dicts."""
        return [item.to_dict() for item in self.model.query.all()]

    def guardar(self, items_dicts):
        """Reemplaza TODOS los items (equivalente a JsonStore.guardar)."""
        self.model.query.delete()
        db.session.commit()
        for data in items_dicts:
            # Remover id para que SQLAlchemy lo auto-genere
            data_copy = {k: v for k, v in data.items() if k != 'id'}
            item = self.model(**data_copy)
            db.session.add(item)
        db.session.commit()

    def agregar(self, item_data, defaults=None):
        """Agrega un item con ID autoincremental."""
        if defaults:
            for clave, valor in defaults.items():
                item_data.setdefault(clave, valor)
        # Remover id si viene (SQLAlchemy lo genera)
        data_copy = {k: v for k, v in item_data.items() if k != 'id'}
        item = self.model(**data_copy)
        db.session.add(item)
        db.session.commit()
        return item.to_dict()

    def editar(self, item_id, nuevos_datos, ensure_fields=None):
        """Actualiza los campos de un item por ID."""
        item = self.model.query.get(item_id)
        if not item:
            return False
        for clave, valor in nuevos_datos.items():
            if hasattr(item, clave) and clave != 'id':
                setattr(item, clave, valor)
        if ensure_fields:
            for clave, valor in ensure_fields.items():
                if not getattr(item, clave, None):
                    setattr(item, clave, valor)
        db.session.commit()
        return True

    def eliminar(self, item_id):
        """Elimina un item por ID."""
        item = self.model.query.get(item_id)
        if item:
            db.session.delete(item)
            db.session.commit()
            return True
        return False

    def buscar(self, **criterios):
        """Busca items que cumplan todos los criterios."""
        query = self.model.query
        for clave, valor in criterios.items():
            if hasattr(self.model, clave):
                query = query.filter(getattr(self.model, clave) == valor)
        return [item.to_dict() for item in query.all()]

    def buscar_uno(self, **criterios):
        """Busca el primer item que cumpla los criterios."""
        resultados = self.buscar(**criterios)
        return resultados[0] if resultados else None

    def filtrar(self, predicate):
        """Filtra items usando una función predicate."""
        items = self.cargar()
        return [item for item in items if predicate(item)]

    def contar(self):
        """Retorna la cantidad de items."""
        return self.model.query.count()

    def existe(self, item_id):
        """Verifica si existe un item con el ID dado."""
        return self.model.query.get(item_id) is not None

    def limpiar(self):
        """Elimina todos los items."""
        self.model.query.delete()
        db.session.commit()


# ============================================================
# 2. ArbolSQLStore - Reemplaza lógica de arbol_bp.py
# ============================================================
class ArbolSQLStore:
    """
    Store SQL para árboles jerárquicos (menú, rubros, almacenes, ubicaciones).
    Imita la API que usa arbol_bp.py internamente.
    """
    def __init__(self, model_class, clave_hijos='submenues', separador='.'):
        self.model = model_class
        self.clave_hijos = clave_hijos
        self.separador = separador

    def cargar_arbol(self):
        """Retorna el árbol completo como lista de dicts anidados."""
        raices = self.model.query.filter_by(padre_id=None).order_by(self.model.id).all()
        return [self._construir_nodo(r) for r in raices]

    def _construir_nodo(self, nodo):
        """Construye un dict con la estructura jerárquica."""
        data = {
            'nombre': nodo.nombre,
            'emoji': nodo.emoji,
            'ruta': nodo.ruta,
            'ruta_jerarquia': nodo.ruta_jerarquia,
            self.clave_hijos: []
        }
        # Campo específico de Ubicacion
        if hasattr(nodo, 'imagen'):
            data['imagen'] = nodo.imagen
        for hijo in nodo.hijos:
            data[self.clave_hijos].append(self._construir_nodo(hijo))
        return data

    def buscar_por_ruta(self, ruta_jerarquia):
        """Busca un nodo por su ruta_jerarquia."""
        return self.model.query.filter_by(ruta_jerarquia=ruta_jerarquia).first()

    def agregar(self, nombre, emoji, ruta, ruta_padre):
        """
        Agrega un nodo hijo bajo ruta_padre.
        Retorna (exito, mensaje).
        """
        if ruta_padre:
            padre = self.model.query.filter_by(ruta_jerarquia=ruta_padre).first()
            if not padre:
                return False, "Padre no encontrado"
            padre_id = padre.id
            nueva_ruta = f"{ruta_padre}{self.separador}{nombre}"
        else:
            padre_id = None
            nueva_ruta = nombre

        # Verificar unicidad
        existente = self.model.query.filter_by(ruta_jerarquia=nueva_ruta).first()
        if existente:
            return False, f"Ya existe un nodo con esa ruta"

        nuevo = self.model(
            nombre=nombre,
            emoji=emoji,
            ruta=ruta,
            ruta_jerarquia=nueva_ruta,
            padre_id=padre_id
        )
        db.session.add(nuevo)
        db.session.commit()
        return True, "Agregado correctamente"

    def editar(self, ruta_original, nuevos_datos):
        """
        Edita un nodo por su ruta_jerarquia.
        Si cambia el nombre, actualiza la ruta_jerarquia de todos los descendientes.
        Retorna (exito, mensaje).
        """
        nodo = self.model.query.filter_by(ruta_jerarquia=ruta_original).first()
        if not nodo:
            return False, "Nodo no encontrado"

        nuevo_nombre = nuevos_datos.get('nombre', nodo.nombre)

        # Si cambió el nombre, actualizar ruta_jerarquia de descendientes
        if nuevo_nombre != nodo.nombre:
            partes = nodo.ruta_jerarquia.split(self.separador)
            partes[-1] = nuevo_nombre
            nueva_ruta = self.separador.join(partes)
            self._actualizar_rutas_descendientes(nodo, nueva_ruta)
            nodo.ruta_jerarquia = nueva_ruta

        nodo.nombre = nuevo_nombre
        nodo.emoji = nuevos_datos.get('emoji', nodo.emoji)
        if 'ruta' in nuevos_datos:
            nodo.ruta = nuevos_datos['ruta']
        if hasattr(nodo, 'imagen') and 'imagen' in nuevos_datos:
            nodo.imagen = nuevos_datos['imagen']

        db.session.commit()
        return True, "Actualizado correctamente"

    def _actualizar_rutas_descendientes(self, nodo, nueva_ruta_padre):
        """Actualiza recursivamente las rutas_jerarquia de los hijos."""
        for hijo in nodo.hijos:
            nueva_ruta_hijo = f"{nueva_ruta_padre}{self.separador}{hijo.nombre}"
            hijo.ruta_jerarquia = nueva_ruta_hijo
            self._actualizar_rutas_descendientes(hijo, nueva_ruta_hijo)

    def eliminar(self, ruta_jerarquia):
        """Elimina un nodo y todos sus descendientes (cascade)."""
        nodo = self.model.query.filter_by(ruta_jerarquia=ruta_jerarquia).first()
        if not nodo:
            return False, "Nodo no encontrado"
        db.session.delete(nodo)  # cascade='all, delete-orphan' elimina hijos
        db.session.commit()
        return True, "Eliminado correctamente"


# ============================================================
# 3. EventSQLStore - Reemplaza EventStore (agenda)
# ============================================================
class EventSQLStore:
    """
    Store SQL para eventos de agenda.
    Imita la API de EventStore de core/event.py.
    """
    CAMPOS_REQUERIDOS = ['titulo', 'fecha']
    PRIORIDADES_VALIDAS = ['alta', 'media', 'baja']

    def __init__(self):
        self.model = Evento

    def _validar(self, data):
        for campo in self.CAMPOS_REQUERIDOS:
            if not data.get(campo):
                raise ValueError(f"El campo '{campo}' es requerido")
        try:
            datetime.strptime(data['fecha'], '%Y-%m-%d')
        except ValueError:
            raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD")

    def listar(self):
        return [e.to_dict() for e in self.model.query.all()]

    def obtener(self, evento_id):
        e = self.model.query.get(evento_id)
        return e.to_dict() if e else None

    def agregar(self, data):
        self._validar(data)
        defaults = {
            'descripcion': '',
            'email': '',
            'realizado': False,
            'prioridad': 'media'
        }
        for k, v in defaults.items():
            data.setdefault(k, v)
        evento = self.model(
            titulo=data['titulo'],
            fecha=data['fecha'],
            descripcion=data.get('descripcion', ''),
            email=data.get('email', ''),
            realizado=data.get('realizado', False),
            prioridad=data.get('prioridad', 'media')
        )
        db.session.add(evento)
        db.session.commit()
        return evento.to_dict()

    def editar(self, evento_id, nuevos_datos):
        e = self.model.query.get(evento_id)
        if not e:
            return False
        for k, v in nuevos_datos.items():
            if hasattr(e, k) and k != 'id':
                setattr(e, k, v)
        db.session.commit()
        return True

    def eliminar(self, evento_id):
        e = self.model.query.get(evento_id)
        if not e:
            return False
        db.session.delete(e)
        db.session.commit()
        return True

    def toggle_realizado(self, evento_id):
        e = self.model.query.get(evento_id)
        if not e:
            return None
        e.realizado = not e.realizado
        db.session.commit()
        return e.realizado

    def obtener_por_fecha(self, fecha):
        return [e.to_dict() for e in self.model.query.filter_by(fecha=fecha).all()]

    def obtener_pendientes(self):
        return [e.to_dict() for e in self.model.query.filter_by(realizado=False).all()]

    def agrupar_por_fecha(self):
        agrupado = {}
        for e in self.listar():
            fecha = e.get('fecha')
            if fecha:
                agrupado.setdefault(fecha, []).append(e)
        return agrupado

    def obtener_eventos_del_dia_siguiente(self):
        from datetime import timedelta
        manana = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        return [
            e.to_dict() for e in self.model.query.filter_by(
                fecha=manana, realizado=False
            ).all()
        ]


# ============================================================
# 4. RepuestoSQLStore - Reemplaza UniqueFieldStore(codigo)
# ============================================================
class RepuestoSQLStore:
    """
    Store SQL para repuestos.
    Imita la API de UniqueFieldStore con campo único 'codigo'.
    """
    def __init__(self):
        self.model = Repuesto

    def cargar(self):
        return [r.to_dict() for r in self.model.query.all()]

    def guardar(self, repuestos_dicts):
        """Reemplaza todos los repuestos."""
        self.model.query.delete()
        db.session.commit()
        for data in repuestos_dicts:
            self._crear_desde_dict(data)
        db.session.commit()

    def _crear_desde_dict(self, data):
        """Crea un repuesto desde un dict (sin validar unicidad)."""
        rutas = data.get('ruta_jerarquia', [])
        rutas_json = json.dumps(rutas if isinstance(rutas, list) else [])
        r = self.model(
            codigo=str(data.get('codigo', '')),
            nombre=data.get('nombre', ''),
            cantidad=int(data.get('cantidad', 0) or 0),
            equipo=data.get('equipo', ''),
            imagen=data.get('imagen', ''),
            fecha_creacion=data.get('fecha_creacion', ''),
            fecha_fin=data.get('fecha_fin', ''),
            link=data.get('link', ''),
            estado=data.get('estado', ''),
            ruta_jerarquia_json=rutas_json
        )
        db.session.add(r)
        return r

    def buscar_por_codigo(self, codigo):
        r = self.model.query.filter_by(codigo=str(codigo)).first()
        return r.to_dict() if r else None

    # Alias para compatibilidad con UniqueFieldStore.buscar_por_unique
    buscar_por_unique = buscar_por_codigo

    def existe_codigo(self, codigo):
        return self.model.query.filter_by(codigo=str(codigo)).first() is not None

    # Alias para compatibilidad
    existe_por_unique = existe_codigo

    def crear(self, datos, skip_unique_check=False):
        """Crea un repuesto validando unicidad. Retorna (exito, mensaje)."""
        codigo = datos.get('codigo')
        if not codigo or str(codigo).strip() == '':
            return False, "El campo 'codigo' es obligatorio"
        if not skip_unique_check and self.existe_codigo(codigo):
            return False, f"Ya existe un repuesto con codigo='{codigo}'"
        self._crear_desde_dict(datos)
        db.session.commit()
        return True, "Creado correctamente"

    def actualizar_por_codigo(self, codigo_original, nuevos_datos, check_new_unique=True):
        """Actualiza un repuesto por código. Retorna (exito, mensaje)."""
        r = self.model.query.filter_by(codigo=str(codigo_original)).first()
        if not r:
            return False, f"No existe repuesto con codigo='{codigo_original}'"

        nuevo_codigo = nuevos_datos.get('codigo')
        if (check_new_unique and nuevo_codigo
                and str(nuevo_codigo) != str(codigo_original)
                and self.existe_codigo(nuevo_codigo)):
            return False, f"El nuevo codigo='{nuevo_codigo}' ya existe"

        # Actualizar campos
        for campo in ['nombre', 'equipo', 'imagen', 'fecha_creacion',
                      'fecha_fin', 'link', 'estado']:
            if campo in nuevos_datos:
                setattr(r, campo, nuevos_datos[campo])
        if 'cantidad' in nuevos_datos:
            r.cantidad = int(nuevos_datos['cantidad'] or 0)
        if 'codigo' in nuevos_datos:
            r.codigo = str(nuevos_datos['codigo'])
        if 'ruta_jerarquia' in nuevos_datos:
            rutas = nuevos_datos['ruta_jerarquia']
            r.ruta_jerarquia_json = json.dumps(
                rutas if isinstance(rutas, list) else []
            )

        db.session.commit()
        return True, "Actualizado correctamente"

    # Alias para compatibilidad con UniqueFieldStore
    def actualizar_por_unique(self, valor_original, nuevos_datos, check_new_unique=True):
        return self.actualizar_por_codigo(valor_original, nuevos_datos, check_new_unique)

    def eliminar_por_codigo(self, codigo):
        r = self.model.query.filter_by(codigo=str(codigo)).first()
        if not r:
            return False, f"No existe repuesto con codigo='{codigo}'"
        db.session.delete(r)
        db.session.commit()
        return True, "Eliminado correctamente"

    # Alias
    eliminar_por_unique = eliminar_por_codigo

    def contar(self):
        return self.model.query.count()

    def buscar(self, **criterios):
        """Busca repuestos que cumplan criterios."""
        # Para repuestos, la búsqueda por ruta_jerarquia es especial
        if 'ruta_jerarquia' in criterios:
            ruta = criterios.pop('ruta_jerarquia')
            resultados = []
            for r in self.model.query.all():
                try:
                    rutas = json.loads(r.ruta_jerarquia_json or '[]')
                except Exception:
                    rutas = []
                if ruta in rutas:
                    resultados.append(r.to_dict())
            return resultados
        # Búsqueda normal por campos
        query = self.model.query
        for clave, valor in criterios.items():
            if hasattr(self.model, clave):
                query = query.filter(getattr(self.model, clave) == valor)
        return [r.to_dict() for r in query.all()]


# ============================================================
# 5. PagoSQLStore - Reemplaza MesStore (pagos mensuales)
# ============================================================
class PagoSQLStore:
    """
    Store SQL para pagos/gastos.
    Reemplaza MesStore (que usaba archivos JSON).
    """
    def __init__(self):
        self.model = Pago

    # --- Archivo general ---
    def leer_general(self):
        """Lee todos los pagos."""
        return [p.to_dict() for p in self.model.query.all()]

    def guardar_general(self, pagos_dicts):
        """Reemplaza todos los pagos."""
        self.model.query.delete()
        db.session.commit()
        for data in pagos_dicts:
            self._crear_desde_dict(data)
        db.session.commit()

    def _crear_desde_dict(self, data):
        """Crea un pago desde un dict."""
        p = self.model(
            rubro=data.get('rubro', ''),
            descripcion=data.get('descripcion', ''),
            importe=float(data.get('importe', 0) or 0),
            tipo=data.get('tipo', 'único'),
            cuotas=int(data.get('cuotas', 1) or 1),
            cuota_numero=data.get('cuota_numero'),
            cuota_total=data.get('cuota_total'),
            vencimiento=data.get('vencimiento', ''),
            pagado=bool(data.get('pagado', False))
        )
        db.session.add(p)
        return p

    # --- MÉTODO FALTANTE: Agregar a general ---
    def agregar_a_general(self, registro):
        """Agrega un pago a la tabla general."""
        self._crear_desde_dict(registro)
        db.session.commit()

    # --- Archivo mensual ---
    def leer_mes(self, anio, mes):
        """Lee pagos de un mes específico."""
        prefix = f"{anio}-{mes:02d}"
        pagos = self.model.query.filter(
            self.model.vencimiento.like(f"{prefix}%")
        ).all()
        return [p.to_dict() for p in pagos]

    def guardar_mes(self, anio, mes, data):
        """No-op en SQL (todo está en una tabla)."""
        pass

    def existe_mes(self, anio, mes):
        """Verifica si hay pagos en ese mes."""
        prefix = f"{anio}-{mes:02d}"
        return self.model.query.filter(
            self.model.vencimiento.like(f"{prefix}%")
        ).count() > 0

    # --- Operaciones avanzadas ---
    def agregar_a_mes(self, anio, mes, registro):
        """Agrega un registro (en SQL es agregar a la tabla general)."""
        self._crear_desde_dict(registro)
        db.session.commit()

    def eliminar_de_mes(self, anio, mes, registro_id):
        """Elimina un pago por ID."""
        p = self.model.query.get(registro_id)
        if not p:
            return False
        db.session.delete(p)
        db.session.commit()
        return True

    # --- MÉTODO FALTANTE: Actualizar pago ---
    def actualizar_pago(self, pago_id, nuevos_datos):
        """Actualiza un pago por ID."""
        p = self.model.query.get(pago_id)
        if not p:
            return False
        for k, v in nuevos_datos.items():
            if hasattr(p, k) and k != 'id':
                setattr(p, k, v)
        db.session.commit()
        return True

    # --- MÉTODO FALTANTE: Eliminar pago ---
    def eliminar_pago(self, pago_id):
        """Elimina un pago por ID."""
        p = self.model.query.get(pago_id)
        if not p:
            return False
        db.session.delete(p)
        db.session.commit()
        return True

    # --- MÉTODO FALTANTE: Toggle pagado ---
    def toggle_pagado(self, pago_id):
        """Alterna el estado de pagado."""
        p = self.model.query.get(pago_id)
        if not p:
            return None
        p.pagado = not p.pagado
        db.session.commit()
        return p.pagado

    # --- Sincronización ---
    def sincronizar_registro(self, registro):
        """Sincroniza un registro (no-op en SQL)."""
        registro_id = registro.get('id')
        p = self.model.query.get(registro_id)
        if not p:
            return
        for k, v in registro.items():
            if hasattr(p, k) and k != 'id':
                setattr(p, k, v)
        db.session.commit()

    # --- Agregaciones ---
    def totales_por_rubro(self, anio, mes):
        """Calcula totales agrupados por rubro."""
        prefix = f"{anio}-{mes:02d}"
        pagos = self.model.query.filter(
            self.model.vencimiento.like(f"{prefix}%")
        ).all()
        totales = {}
        for p in pagos:
            rubro = p.rubro or 'Sin Rubro'
            totales[rubro] = totales.get(rubro, 0) + (p.importe or 0)
        return totales

    def total_mes(self, anio, mes):
        """Calcula el total de un mes."""
        prefix = f"{anio}-{mes:02d}"
        total = db.session.query(func.sum(self.model.importe)).filter(
            self.model.vencimiento.like(f"{prefix}%")
        ).scalar()
        return round(total or 0, 2)

    def listar_meses_disponibles(self):
        """Lista todos los meses que tienen pagos."""
        resultados = db.session.query(
            func.substr(self.model.vencimiento, 1, 4).label('anio'),
            func.substr(self.model.vencimiento, 6, 2).label('mes')
        ).filter(
            self.model.vencimiento.isnot(None),
            self.model.vencimiento != '',
            func.length(self.model.vencimiento) >= 7
        ).distinct().all()

        meses = []
        for r in resultados:
            try:
                meses.append((int(r.anio), int(r.mes)))
            except (ValueError, TypeError):
                pass
        meses.sort(reverse=True)
        return meses

    # --- Clonación ---
    def clonar_mes(self, anio_origen, mes_origen, anio_destino, mes_destino,
                   resetear_pagado=True):
        """Clona pagos de un mes a otro."""
        from calendar import monthrange

        pagos_origen = self.leer_mes(anio_origen, mes_origen)
        if not pagos_origen:
            raise ValueError(f"No hay pagos en {anio_origen}/{mes_origen:02d}")

        ultimo_dia = monthrange(anio_destino, mes_destino)[1]
        registros_clonados = []

        for p_dict in pagos_origen:
            nuevo = dict(p_dict)
            nuevo.pop('id', None)

            try:
                fecha_origen = datetime.strptime(p_dict['vencimiento'], "%Y-%m-%d")
                dia = min(fecha_origen.day, ultimo_dia)
                nuevo['vencimiento'] = f"{anio_destino}-{mes_destino:02d}-{dia:02d}"
            except (ValueError, KeyError):
                nuevo['vencimiento'] = f"{anio_destino}-{mes_destino:02d}-{ultimo_dia:02d}"

            if resetear_pagado:
                nuevo['pagado'] = False

            self._crear_desde_dict(nuevo)
            registros_clonados.append(nuevo)

        db.session.commit()
        return len(registros_clonados), registros_clonados

# ============================================================
# 6. NodoBloqueoSQLStore - Reemplaza lógica de gestion_de_bloqueos.py
# ============================================================
class NodoBloqueoSQLStore:
    """
    Store SQL para nodos de bloqueo (árbol de interruptores).
    Imita la API que usa gestion_de_bloqueos.py.
    """
    def __init__(self):
        self.model = NodoBloqueo

    def cargar_todos(self):
        """Retorna dict {id: {datos}} como el JSON original."""
        nodos = self.model.query.all()
        return {n.id: n.to_dict() for n in nodos}

    def obtener(self, nodo_id):
        n = self.model.query.get(str(nodo_id))
        return n.to_dict() if n else None

    def crear(self, nombre, padre_id=None):
        """Crea un nuevo nodo. Retorna (nuevo_id, datos)."""
        # Generar ID único
        todos = self.model.query.all()
        max_id = 0
        for n in todos:
            try:
                max_id = max(max_id, int(n.id))
            except (ValueError, TypeError):
                pass
        nuevo_id = str(max_id + 1)

        nodo = self.model(
            id=nuevo_id,
            nombre=nombre,
            estado='apagado',
            descripcion='',
            padre_id=str(padre_id) if padre_id else None
        )
        db.session.add(nodo)
        db.session.commit()
        return nuevo_id, nodo.to_dict()

    def actualizar(self, nodo_id, datos):
        """Actualiza un nodo. Retorna datos actualizados o None."""
        n = self.model.query.get(str(nodo_id))
        if not n:
            return None
        for k in ['nombre', 'estado', 'descripcion']:
            if k in datos:
                setattr(n, k, datos[k])
        if 'padre' in datos:
            n.padre_id = str(datos['padre']) if datos['padre'] else None
        db.session.commit()
        return n.to_dict()

    def eliminar(self, nodo_id):
        """Elimina un nodo."""
        n = self.model.query.get(str(nodo_id))
        if not n:
            return False
        db.session.delete(n)
        db.session.commit()
        return True

    def toggle_estado(self, nodo_id):
        """Alterna el estado de un nodo. Retorna nuevo estado o None."""
        n = self.model.query.get(str(nodo_id))
        if not n:
            return None
        n.estado = 'encendido' if n.estado == 'apagado' else 'apagado'
        db.session.commit()
        return n.estado


# ============================================================
# INSTANCIAS GLOBALES REUTILIZABLES
# ============================================================
# Para usar en blueprints (reemplazan las instancias JSON actuales)

# Árboles jerárquicos
menu_store = ArbolSQLStore(Menu, 'submenues', '.')
rubro_store = ArbolSQLStore(Rubro, 'submenues', '.')
almacen_store = ArbolSQLStore(Almacen, 'subcrear_almacenes', '.')
ubicacion_store = ArbolSQLStore(Ubicacion, 'sububicaciones', '-')

# Listas planas
tab_store = SQLStore(Tab)
estado_store = SQLStore(Estado)

# Stores especializados
evento_store = EventSQLStore()
tarea_store = SQLStore(Tarea)
repuesto_store = RepuestoSQLStore()
pago_store = PagoSQLStore()
nodo_bloqueo_store = NodoBloqueoSQLStore()