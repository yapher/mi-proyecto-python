# core/repuestos.py
"""
Módulo reutilizable para operaciones con repuestos.
Usado por: inventario, listarepuestos, estadosderepuestos, graficosrepuestos.
"""
from core.db_sql_store import repuesto_store, almacen_store


# ============================================================
# LECTURA
# ============================================================

def cargar_todos_repuestos():
    """Carga todos los repuestos desde SQL."""
    return repuesto_store.cargar()


def cargar_arbol_almacenes():
    """Carga el árbol completo de almacenes."""
    return almacen_store.cargar_arbol()


def obtener_repuesto_por_codigo(codigo):
    """Busca un repuesto por su código."""
    return repuesto_store.buscar_por_codigo(codigo)


def existe_codigo(codigo):
    """Verifica si existe un repuesto con el código dado."""
    return repuesto_store.existe_codigo(codigo)


# ============================================================
# ESCRITURA (CRUD)
# ============================================================

def crear_repuesto(datos):
    """
    Crea un nuevo repuesto. Retorna (exito, mensaje).
    Valida que no exista otro con el mismo código.
    """
    return repuesto_store.crear(datos, skip_unique_check=False)


def actualizar_repuesto(codigo_original, nuevos_datos):
    """
    Actualiza un repuesto existente. Retorna (exito, mensaje).
    Valida que el nuevo código (si cambia) no exista ya.
    """
    return repuesto_store.actualizar_por_codigo(
        codigo_original=codigo_original,
        nuevos_datos=nuevos_datos,
        check_new_unique=True
    )


def eliminar_repuesto(codigo):
    """Elimina un repuesto por código. Retorna (exito, mensaje)."""
    return repuesto_store.eliminar_por_codigo(codigo)


def guardar_todos_repuestos(repuestos):
    """Reemplaza TODOS los repuestos (uso en migraciones o bulk)."""
    repuesto_store.guardar(repuestos)


# ============================================================
# CONSULTAS / MAPEO
# ============================================================

def _extraer_todas_rutas_almacenes(arbol):
    """Extrae recursivamente todas las rutas_jerarquia y nombres."""
    resultado = {}

    def _recorrer(items):
        if not items:
            return
        for item in items:
            if not isinstance(item, dict):
                continue
            ruta_jer = (item.get('ruta_jerarquia') or '').strip()
            nombre = (item.get('nombre') or '').strip()
            if ruta_jer:
                resultado[ruta_jer] = {'ruta_jerarquia': ruta_jer, 'nombre': nombre}
            if nombre:
                resultado[nombre] = {'ruta_jerarquia': ruta_jer, 'nombre': nombre}
            if '.' in ruta_jer:
                ultimo = ruta_jer.split('.')[-1].strip()
                if ultimo:
                    resultado[ultimo] = {'ruta_jerarquia': ruta_jer, 'nombre': nombre}
            subs = (
                item.get('subcrear_almacenes')
                or item.get('subalmacenes')
                or item.get('sububicaciones')
                or []
            )
            if subs:
                _recorrer(subs)

    _recorrer(arbol)
    return resultado


def construir_mapeo_repuestos_por_almacen(repuestos=None, almacenes=None):
    """
    Construye un mapeo robusto de repuestos por almacén.
    Cubre TODOS los casos posibles de asignación.
    """
    if repuestos is None:
        repuestos = cargar_todos_repuestos()
    if almacenes is None:
        almacenes = cargar_arbol_almacenes()

    claves_almacen = _extraer_todas_rutas_almacenes(almacenes)
    mapeo = {}

    for rep in repuestos:
        equipo = (rep.get('equipo') or '').strip()
        if not equipo:
            continue

        mapeo.setdefault(equipo, []).append(rep)

        if '.' in equipo:
            ultimo = equipo.split('.')[-1].strip()
            if ultimo and ultimo != equipo:
                mapeo.setdefault(ultimo, []).append(rep)

        if equipo not in claves_almacen:
            for clave, info in claves_almacen.items():
                if clave.endswith('.' + equipo) or clave == equipo:
                    mapeo.setdefault(clave, []).append(rep)
                    break

    return mapeo


def obtener_repuestos_para_almacen(mapeo, almacen):
    """Obtiene todos los repuestos de un almacén específico."""
    ruta_jer = (almacen.get('ruta_jerarquia') or '').strip()
    nombre = (almacen.get('nombre') or '').strip()

    if ruta_jer and ruta_jer in mapeo:
        return mapeo[ruta_jer]
    if nombre and nombre in mapeo:
        return mapeo[nombre]
    if '.' in ruta_jer:
        ultimo = ruta_jer.split('.')[-1].strip()
        if ultimo in mapeo:
            return mapeo[ultimo]
    return []


def contar_repuestos_por_estado(repuestos=None, filtro_jerarquia=None):
    """Cuenta repuestos agrupados por estado."""
    from core.data_loaders import cargar_estados

    if repuestos is None:
        repuestos = cargar_todos_repuestos()

    estados = cargar_estados()
    mapa_estados = {e['emoji']: e['nombre'] for e in estados}

    contador = {}
    for item in repuestos:
        if filtro_jerarquia:
            rutas = item.get("ruta_jerarquia", [])
            if filtro_jerarquia not in rutas:
                continue

        estado = item.get("estado", "Otros")
        estado_legible = mapa_estados.get(estado, "Otros")
        contador[estado_legible] = contador.get(estado_legible, 0) + 1

    return contador


def filtrar_repuestos(repuestos, filtros):
    """Filtra repuestos según múltiples criterios."""
    from datetime import datetime

    resultado = []
    hoy = datetime.today().date()
    mostrar_vencidos = filtros.get('vencidos') == '1'

    for rep in repuestos:
        cumple = True

        fecha_fin_str = rep.get('fecha_fin')
        esta_vencido = False
        if fecha_fin_str:
            try:
                fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
                if fecha_fin < hoy:
                    esta_vencido = True
            except ValueError:
                pass

        if mostrar_vencidos and not esta_vencido:
            continue

        if filtros.get('nombre') and filtros['nombre'].lower() not in rep.get('nombre', '').lower():
            cumple = False
        if filtros.get('codigo') and filtros['codigo'].lower() not in rep.get('codigo', '').lower():
            cumple = False
        if filtros.get('estado') and filtros['estado'] != rep.get('estado', ''):
            cumple = False

        if filtros.get('fecha_alta'):
            try:
                fecha_alta = datetime.strptime(filtros['fecha_alta'], '%Y-%m-%d')
                rep_fecha = datetime.strptime(rep.get('fecha_creacion', ''), '%Y-%m-%d')
                if rep_fecha.date() != fecha_alta.date():
                    cumple = False
            except Exception:
                pass

        if filtros.get('fecha_baja'):
            try:
                fecha_baja = datetime.strptime(filtros['fecha_baja'], '%Y-%m-%d')
                rep_fecha = datetime.strptime(rep.get('fecha_fin', ''), '%Y-%m-%d')
                if rep_fecha.date() != fecha_baja.date():
                    cumple = False
            except Exception:
                if rep.get('fecha_fin'):
                    cumple = False

        if cumple:
            resultado.append(rep)

    return resultado