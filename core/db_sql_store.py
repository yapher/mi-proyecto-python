import json
import re
from datetime import datetime
from calendar import monthrange
from sqlalchemy import func
from core.db_sql import db
from core.models import (
    Menu, Rubro, Almacen, Ubicacion, Tab, Estado,
    Repuesto, Pago, NodoBloqueo, Evento, Tarea, Plano,
)
from core.models.repuesto import repuesto_ubicacion


class SQLStore:
    def __init__(self, model_class):
        self.model = model_class

    def cargar(self):
        return [item.to_dict() for item in self.model.query.all()]

    def guardar(self, items_dicts):
        self.model.query.delete()
        db.session.commit()
        for data in items_dicts:
            data_copy = {k: v for k, v in data.items() if k != 'id'}
            item = self.model(**data_copy)
            db.session.add(item)
        db.session.commit()

    def agregar(self, item_data, defaults=None):
        if defaults:
            for clave, valor in defaults.items():
                item_data.setdefault(clave, valor)

        data_copy = {k: v for k, v in item_data.items() if k != 'id'}
        item = self.model(**data_copy)
        db.session.add(item)
        db.session.commit()
        return item.to_dict()

    def editar(self, item_id, nuevos_datos, ensure_fields=None):
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
        item = self.model.query.get(item_id)
        if item:
            db.session.delete(item)
            db.session.commit()
            return True
        return False

    def buscar(self, **criterios):
        query = self.model.query
        for clave, valor in criterios.items():
            if hasattr(self.model, clave):
                query = query.filter(getattr(self.model, clave) == valor)
        return [item.to_dict() for item in query.all()]

    def buscar_uno(self, **criterios):
        resultados = self.buscar(**criterios)
        return resultados[0] if resultados else None

    def filtrar(self, predicate):
        items = self.cargar()
        return [item for item in items if predicate(item)]

    def contar(self):
        return self.model.query.count()

    def existe(self, item_id):
        return self.model.query.get(item_id) is not None

    def limpiar(self):
        self.model.query.delete()
        db.session.commit()


class ArbolSQLStore:
    def __init__(self, model_class, clave_hijos='submenues', separador='.'):
        self.model = model_class
        self.clave_hijos = clave_hijos
        self.separador = separador

    def cargar_arbol(self):
        raices = self.model.query.filter_by(padre_id=None).order_by(self.model.nombre).all()
        return [self._construir_nodo(r) for r in raices]

    def _construir_nodo(self, nodo):
        data = {
            'nombre': nodo.nombre,
            'emoji': nodo.emoji,
            'ruta': nodo.ruta,
            'ruta_jerarquia': nodo.ruta_jerarquia,
            self.clave_hijos: []
        }

        if hasattr(nodo, 'imagen'):
            data['imagen'] = nodo.imagen

        if hasattr(nodo, 'roles'):
            data['roles'] = nodo.roles or []

        for hijo in sorted(nodo.hijos, key=lambda h: h.nombre):
            data[self.clave_hijos].append(self._construir_nodo(hijo))

        return data

    def buscar_por_ruta(self, ruta_jerarquia):
        return self.model.query.filter_by(ruta_jerarquia=ruta_jerarquia).first()

    def agregar(self, nombre, emoji, ruta, ruta_padre, roles=None):
        if ruta_padre:
            padre = self.model.query.filter_by(ruta_jerarquia=ruta_padre).first()
            if not padre:
                return False, "Padre no encontrado"
            padre_id = padre.id
            nueva_ruta = f"{ruta_padre}{self.separador}{nombre}"
        else:
            padre_id = None
            nueva_ruta = nombre

        existente = self.model.query.filter_by(ruta_jerarquia=nueva_ruta).first()
        if existente:
            return False, "Ya existe un nodo con esa ruta"

        nuevo = self.model(
            nombre=nombre,
            emoji=emoji,
            ruta=ruta,
            ruta_jerarquia=nueva_ruta,
            padre_id=padre_id
        )

        if roles is not None and hasattr(nuevo, 'roles'):
            nuevo.roles = roles

        db.session.add(nuevo)
        db.session.commit()
        return True, "Agregado correctamente"

    def editar(self, ruta_original, nuevos_datos):
        nodo = self.model.query.filter_by(ruta_jerarquia=ruta_original).first()
        if not nodo:
            return False, "Nodo no encontrado"

        nuevo_nombre = nuevos_datos.get('nombre', nodo.nombre)

        if nuevo_nombre != nodo.nombre:
            if nodo.padre is not None:
                nueva_ruta = f"{nodo.padre.ruta_jerarquia}{self.separador}{nuevo_nombre}"
            else:
                nueva_ruta = nuevo_nombre
            self._actualizar_rutas_descendientes(nodo, nueva_ruta)
            nodo.ruta_jerarquia = nueva_ruta

        nodo.nombre = nuevo_nombre
        nodo.emoji = nuevos_datos.get('emoji', nodo.emoji)

        if 'ruta' in nuevos_datos:
            nodo.ruta = nuevos_datos['ruta']

        if hasattr(nodo, 'imagen') and 'imagen' in nuevos_datos:
            nodo.imagen = nuevos_datos['imagen']

        if hasattr(nodo, 'roles') and 'roles' in nuevos_datos:
            nodo.roles = nuevos_datos['roles']

        db.session.commit()
        return True, "Actualizado correctamente"

    

    def _actualizar_rutas_descendientes(self, nodo, nueva_ruta_padre):
        for hijo in nodo.hijos:
            nueva_ruta_hijo = f"{nueva_ruta_padre}{self.separador}{hijo.nombre}"
            hijo.ruta_jerarquia = nueva_ruta_hijo
            self._actualizar_rutas_descendientes(hijo, nueva_ruta_hijo)

    def eliminar(self, ruta_jerarquia):
        nodo = self.model.query.filter_by(ruta_jerarquia=ruta_jerarquia).first()
        if not nodo:
            return False, "Nodo no encontrado"

        if self.model is Almacen:
            ids = self._ids_subarbol(nodo)
            cantidad = Repuesto.query.filter(Repuesto.almacen_id.in_(ids)).count()
            if cantidad:
                return False, (
                    f"No se puede eliminar: hay {cantidad} repuesto(s) en este "
                    f"almacén o en sus sub-almacenes. Movelos antes."
                )

        elif self.model is Ubicacion:
            ids = self._ids_subarbol(nodo)

            cantidad = Repuesto.query.filter(
                Repuesto.ubicaciones.any(Ubicacion.id.in_(ids))
            ).count()
            if cantidad:
                return False, (
                    f"No se puede eliminar: hay {cantidad} repuesto(s) con esta "
                    f"ubicación técnica (o sus sub-ubicaciones). Quitala de esos repuestos antes."
                )

            pestanias = Tab.query.filter(Tab.ubicacion_id.in_(ids)).count()
            if pestanias:
                return False, (
                    f"No se puede eliminar: hay {pestanias} pestaña(s) de repuestos "
                    f"asociadas a esta ubicación técnica (o sus sub-ubicaciones)."
                )
            
            planos = Plano.query.filter(Plano.ubicacion_id.in_(ids)).count()
            if planos:
                return False, (
                    f"No se puede eliminar: hay {planos} plano(s) PDF asociados "
                    f"a esta ubicación técnica (o sus sub-ubicaciones)."
                )

        db.session.delete(nodo)
        db.session.commit()
        return True, "Eliminado correctamente"

    def _ids_subarbol(self, nodo):
        ids = [nodo.id]
        for hijo in nodo.hijos:
            ids.extend(self._ids_subarbol(hijo))
        return ids


class EventSQLStore:
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


class RepuestoSQLStore:
    def __init__(self):
        self.model = Repuesto

    def cargar(self):
        return [r.to_dict() for r in self.model.query.all()]

    def guardar(self, repuestos_dicts):
        db.session.execute(repuesto_ubicacion.delete())
        self.model.query.delete()
        db.session.commit()
        for data in repuestos_dicts:
            self._crear_desde_dict(data)
        db.session.commit()

    def _crear_desde_dict(self, data):
        rutas = data.get('ruta_jerarquia', [])
        rutas_json = json.dumps(rutas if isinstance(rutas, list) else [])

        comentario = data.get('comentario', '')
        if comentario is None:
            comentario = ''

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
            comentario=str(comentario),
            ruta_jerarquia_json=rutas_json
        )
        db.session.add(r)
        return r

    def buscar_por_codigo(self, codigo):
        r = self.model.query.filter_by(codigo=str(codigo)).first()
        return r.to_dict() if r else None

    buscar_por_unique = buscar_por_codigo

    def existe_codigo(self, codigo):
        return self.model.query.filter_by(codigo=str(codigo)).first() is not None

    existe_por_unique = existe_codigo

    def crear(self, datos, skip_unique_check=False):
        codigo = datos.get('codigo')
        if not codigo or str(codigo).strip() == '':
            return False, "El campo 'codigo' es obligatorio"

        if not skip_unique_check and self.existe_codigo(codigo):
            return False, f"Ya existe un repuesto con codigo='{codigo}'"

        self._crear_desde_dict(datos)
        db.session.commit()
        return True, "Creado correctamente"

    def actualizar_por_codigo(self, codigo_original, nuevos_datos, check_new_unique=True):
        r = self.model.query.filter_by(codigo=str(codigo_original)).first()
        if not r:
            return False, f"No existe repuesto con codigo='{codigo_original}'"

        nuevo_codigo = nuevos_datos.get('codigo')
        if (
            check_new_unique
            and nuevo_codigo
            and str(nuevo_codigo) != str(codigo_original)
            and self.existe_codigo(nuevo_codigo)
        ):
            return False, f"El nuevo codigo='{nuevo_codigo}' ya existe"

        for campo in [
            'nombre', 'imagen', 'fecha_creacion',
            'fecha_fin', 'link', 'estado', 'comentario'
        ]:
            if campo in nuevos_datos:
                valor = nuevos_datos[campo]
                if campo == 'comentario':
                    valor = '' if valor is None else str(valor)
                setattr(r, campo, valor)

        # ✅ NUEVO: almacén por clave foránea
        if 'equipo' in nuevos_datos or 'almacen_id' in nuevos_datos:
            r.almacen_id, r.equipo_legacy = self._resolver_almacen(nuevos_datos)

        if 'cantidad' in nuevos_datos:
            r.cantidad = int(nuevos_datos['cantidad'] or 0)

        if 'codigo' in nuevos_datos:
            r.codigo = str(nuevos_datos['codigo'])

        if 'ruta_jerarquia' in nuevos_datos:
            ubicaciones, sueltas = self._resolver_ubicaciones(nuevos_datos['ruta_jerarquia'])
            r.ubicaciones = ubicaciones
            r.ruta_jerarquia_json = json.dumps(sueltas)

        db.session.commit()
        return True, "Actualizado correctamente"

    def actualizar_por_unique(self, valor_original, nuevos_datos, check_new_unique=True):
        return self.actualizar_por_codigo(valor_original, nuevos_datos, check_new_unique)

    def eliminar_por_codigo(self, codigo):
        r = self.model.query.filter_by(codigo=str(codigo)).first()
        if not r:
            return False, f"No existe repuesto con codigo='{codigo}'"

        db.session.delete(r)
        db.session.commit()
        return True, "Eliminado correctamente"

    eliminar_por_unique = eliminar_por_codigo

    def contar(self):
        return self.model.query.count()

    def buscar(self, **criterios):
        if 'ruta_jerarquia' in criterios:
            ruta = criterios.pop('ruta_jerarquia')
            repuestos = self.model.query.filter(
                self.model.ubicaciones.any(Ubicacion.ruta_jerarquia == ruta)
            ).all()
            return [r.to_dict() for r in repuestos]

        query = self.model.query
        for clave, valor in criterios.items():
            if hasattr(self.model, clave):
                query = query.filter(getattr(self.model, clave) == valor)
        return [r.to_dict() for r in query.all()]
    
    def _resolver_almacen(self, data):
        """
        Devuelve (almacen_id, texto_legacy).
        Acepta 'almacen_id' o 'equipo' (ruta_jerarquia que manda el select).
        """
        aid = data.get('almacen_id')
        if aid not in (None, ''):
            try:
                aid = int(aid)
                if Almacen.query.get(aid):
                    return aid, ''
            except (ValueError, TypeError):
                pass

        ruta = (data.get('equipo') or '').strip()
        if not ruta:
            return None, ''

        almacen = Almacen.query.filter_by(ruta_jerarquia=ruta).first()
        if almacen:
            return almacen.id, ''
        return None, ruta  # texto libre que no coincide con ningún almacén


    def _resolver_ubicaciones(self, rutas):
        """
        Convierte una lista de rutas (texto) en (objetos Ubicacion, rutas sueltas).
        Las sueltas son las que no coinciden con ninguna ubicación existente.
        """
        if not isinstance(rutas, (list, tuple)):
            rutas = []

        limpias = []
        for x in rutas:
            x = str(x).strip()
            if x and x not in limpias:
                limpias.append(x)

        if not limpias:
            return [], []

        encontradas = {
            u.ruta_jerarquia: u
            for u in Ubicacion.query.filter(Ubicacion.ruta_jerarquia.in_(limpias)).all()
        }
        ubicaciones = [encontradas[x] for x in limpias if x in encontradas]
        sueltas = [x for x in limpias if x not in encontradas]
        return ubicaciones, sueltas


class PagoSQLStore:
    def __init__(self):
        self.model = Pago

    def leer_general(self):
        return [p.to_dict() for p in self.model.query.all()]

    def guardar_general(self, pagos_dicts):
        self.model.query.delete()
        db.session.commit()
        for data in pagos_dicts:
            self._crear_desde_dict(data)
        db.session.commit()

    def _crear_desde_dict(self, data):
        ubicaciones, sueltas = self._resolver_ubicaciones(data.get('ruta_jerarquia', []))

        comentario = data.get('comentario', '')
        if comentario is None:
            comentario = ''

        almacen_id, equipo_txt = self._resolver_almacen(data)

        r = self.model(
            codigo=str(data.get('codigo', '')),
            nombre=data.get('nombre', ''),
            cantidad=int(data.get('cantidad', 0) or 0),
            almacen_id=almacen_id,
            equipo_legacy=equipo_txt,
            imagen=data.get('imagen', ''),
            fecha_creacion=data.get('fecha_creacion', ''),
            fecha_fin=data.get('fecha_fin', ''),
            link=data.get('link', ''),
            estado=data.get('estado', ''),
            comentario=str(comentario),
            ruta_jerarquia_json=json.dumps(sueltas)
        )
        r.ubicaciones = ubicaciones
        db.session.add(r)
        return r

    def agregar_a_general(self, registro):
        self._crear_desde_dict(registro)
        db.session.commit()

    def leer_mes(self, anio, mes):
        prefix = f"{anio}-{mes:02d}"
        pagos = self.model.query.filter(
            self.model.vencimiento.like(f"{prefix}%")
        ).all()
        return [p.to_dict() for p in pagos]

    def guardar_mes(self, anio, mes, data):
        pass

    def existe_mes(self, anio, mes):
        prefix = f"{anio}-{mes:02d}"
        return self.model.query.filter(
            self.model.vencimiento.like(f"{prefix}%")
        ).count() > 0

    def agregar_a_mes(self, anio, mes, registro):
        self._crear_desde_dict(registro)
        db.session.commit()

    def eliminar_de_mes(self, anio, mes, registro_id):
        p = self.model.query.get(registro_id)
        if not p:
            return False
        db.session.delete(p)
        db.session.commit()
        return True

    def actualizar_pago(self, pago_id, nuevos_datos):
        p = self.model.query.get(pago_id)
        if not p:
            return False

        for k, v in nuevos_datos.items():
            if hasattr(p, k) and k != 'id':
                setattr(p, k, v)

        db.session.commit()
        return True

    def eliminar_pago(self, pago_id):
        p = self.model.query.get(pago_id)
        if not p:
            return False

        db.session.delete(p)
        db.session.commit()
        return True

    def toggle_pagado(self, pago_id):
        p = self.model.query.get(pago_id)
        if not p:
            return None

        p.pagado = not p.pagado
        db.session.commit()
        return p.pagado

    def sincronizar_registro(self, registro):
        registro_id = registro.get('id')
        p = self.model.query.get(registro_id)
        if not p:
            return

        for k, v in registro.items():
            if hasattr(p, k) and k != 'id':
                setattr(p, k, v)
        db.session.commit()

    def totales_por_rubro(self, anio, mes):
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
        prefix = f"{anio}-{mes:02d}"
        total = db.session.query(func.sum(self.model.importe)).filter(
            self.model.vencimiento.like(f"{prefix}%")
        ).scalar()
        return round(total or 0, 2)

    def listar_meses_disponibles(self):
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

    def clonar_mes(self, anio_origen, mes_origen, anio_destino, mes_destino,
                   resetear_pagado=True):
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


class NodoBloqueoSQLStore:
    def __init__(self):
        self.model = NodoBloqueo

    def cargar_todos(self):
        nodos = self.model.query.all()
        return {n.id: n.to_dict() for n in nodos}

    def obtener(self, nodo_id):
        n = self.model.query.get(str(nodo_id))
        return n.to_dict() if n else None

    def crear(self, nombre, padre_id=None):
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
        n = self.model.query.get(str(nodo_id))
        if not n:
            return False

        db.session.delete(n)
        db.session.commit()
        return True

    def toggle_estado(self, nodo_id):
        n = self.model.query.get(str(nodo_id))
        if not n:
            return None

        n.estado = 'encendido' if n.estado == 'apagado' else 'apagado'
        db.session.commit()
        return n.estado


class PlanoSQLStore:
    def __init__(self):
        self.model = Plano

    def cargar_todos(self):
        planos = self.model.query.all()
        planos.sort(key=lambda p: (p.nombre_linea or '').lower())
        return [p.to_dict() for p in planos]

    def obtener(self, plano_id):
        return self.model.query.get(plano_id)

    def existe(self, ubicacion_id, nombre_archivo):
        return self.model.query.filter_by(
            ubicacion_id=ubicacion_id, nombre_archivo=nombre_archivo
        ).first() is not None

    def agregar(self, ubicacion, carpeta, nombre_archivo, descripcion, usuario):
        nuevo = self.model(
            ubicacion_id=ubicacion.id,
            nombre_linea_legacy=(ubicacion.ruta_jerarquia or '')[:100],
            carpeta=carpeta,
            nombre_archivo=nombre_archivo,
            descripcion=descripcion,
            usuario_carga=usuario,
        )
        db.session.add(nuevo)
        db.session.commit()
        return nuevo.id

    def editar_descripcion(self, plano_id, descripcion):
        plano = self.model.query.get(plano_id)
        if not plano:
            return False
        plano.descripcion = descripcion
        db.session.commit()
        return True

    def eliminar(self, plano_id):
        plano = self.model.query.get(plano_id)
        if not plano:
            return False
        db.session.delete(plano)
        db.session.commit()
        return True


menu_store = ArbolSQLStore(Menu, 'submenues', '.')
rubro_store = ArbolSQLStore(Rubro, 'submenues', '.')
almacen_store = ArbolSQLStore(Almacen, 'subcrear_almacenes', '.')
ubicacion_store = ArbolSQLStore(Ubicacion, 'sububicaciones', '-')

tab_store = SQLStore(Tab)
estado_store = SQLStore(Estado)

evento_store = EventSQLStore()
tarea_store = SQLStore(Tarea)
repuesto_store = RepuestoSQLStore()
pago_store = PagoSQLStore()
nodo_bloqueo_store = NodoBloqueoSQLStore()
plano_store = PlanoSQLStore()