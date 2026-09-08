"""
core/migrator.py
================
Migra datos desde JSON a SQL.
Uso: python -m core.migrator
"""
import sys
import os
import json
import re

# Asegurar que se ejecuta desde la raíz del proyecto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db_sql import db
from core.models import (
    Usuario, Evento, Tarea, Menu, Rubro, Almacen,
    Ubicacion, Tab, Estado, Repuesto, Pago,
    NodoBloqueo, OrdenTrabajo
)


def migrar_usuarios():
    ruta = 'users.json'
    if not os.path.exists(ruta):
        print("⚠️  No existe users.json")
        return 0
    with open(ruta, 'r', encoding='utf-8') as f:
        data = json.load(f)
    Usuario.query.delete()
    db.session.commit()
    for item in data:
        usuario = Usuario(
            id=str(item.get('id', '')),
            username=item.get('username', ''),
            password=item.get('password', ''),
            roles=item.get('roles', [])
        )
        db.session.add(usuario)
    db.session.commit()
    print(f"✅ Migrados {len(data)} usuarios")
    return len(data)


def migrar_eventos():
    ruta = 'DataBase/time/agenda.json'
    if not os.path.exists(ruta):
        print("⚠️  No existe agenda.json")
        return 0
    with open(ruta, 'r', encoding='utf-8') as f:
        data = json.load(f)
    Evento.query.delete()
    db.session.commit()
    for item in data:
        db.session.add(Evento(
            titulo=item.get('titulo', ''),
            fecha=item.get('fecha', ''),
            descripcion=item.get('descripcion', ''),
            email=item.get('email', ''),
            realizado=item.get('realizado', False),
            prioridad=item.get('prioridad', 'media')
        ))
    db.session.commit()
    print(f"✅ Migrados {len(data)} eventos")
    return len(data)


def migrar_tareas():
    ruta = 'DataBase/time/dataTask.json'
    if not os.path.exists(ruta):
        print("⚠️  No existe dataTask.json")
        return 0
    with open(ruta, 'r', encoding='utf-8') as f:
        data = json.load(f)
    Tarea.query.delete()
    db.session.commit()
    for item in data:
        db.session.add(Tarea(
            titulo=item.get('titulo', ''),
            fecha=item.get('fecha', ''),
            descripcion=item.get('descripcion', '')
        ))
    db.session.commit()
    print(f"✅ Migradas {len(data)} tareas")
    return len(data)


def _migrar_arbol(items, modelo_cls, clave_hijos, padre_id=None, ruta_padre='', sep='.'):
    count = 0
    for item in items:
        nombre = item.get('nombre', '')
        if not nombre:
            continue
        ruta_j = f"{ruta_padre}{sep}{nombre}" if ruta_padre else nombre
        nodo = modelo_cls(
            nombre=nombre,
            emoji=item.get('emoji', ''),
            ruta=item.get('ruta', ''),
            ruta_jerarquia=ruta_j,
            padre_id=padre_id
        )
        if hasattr(nodo, 'roles'):
            nodo.roles = item.get('roles', [])
        if hasattr(nodo, 'imagen'):
            nodo.imagen = item.get('imagen', '')
        db.session.add(nodo)
        db.session.flush()
        count += 1
        hijos = item.get(clave_hijos, [])
        if hijos:
            count += _migrar_arbol(hijos, modelo_cls, clave_hijos, nodo.id, ruta_j, sep)
    return count


def migrar_menu():
    ruta = 'DataBase/Config/menu.json'
    if not os.path.exists(ruta):
        print("⚠️  No existe menu.json")
        return 0
    with open(ruta, 'r', encoding='utf-8') as f:
        data = json.load(f)
    Menu.query.delete()
    db.session.commit()
    count = _migrar_arbol(data, Menu, 'submenues', sep='.')
    db.session.commit()
    print(f"✅ Migrados {count} nodos de menú")
    return count


def migrar_rubros():
    ruta = 'DataBase/hogar/rubro.json'
    if not os.path.exists(ruta):
        print("⚠️  No existe rubro.json")
        return 0
    with open(ruta, 'r', encoding='utf-8') as f:
        data = json.load(f)
    Rubro.query.delete()
    db.session.commit()
    count = _migrar_arbol(data, Rubro, 'submenues', sep='.')
    db.session.commit()
    print(f"✅ Migrados {count} rubros")
    return count


def migrar_almacenes():
    ruta = 'DataBase/dataRep/almacenes.json'
    if not os.path.exists(ruta):
        print("⚠️  No existe almacenes.json")
        return 0
    with open(ruta, 'r', encoding='utf-8') as f:
        data = json.load(f)
    Almacen.query.delete()
    db.session.commit()
    count = _migrar_arbol(data, Almacen, 'subcrear_almacenes', sep='.')
    db.session.commit()
    print(f"✅ Migrados {count} almacenes")
    return count


def migrar_ubicaciones():
    ruta = 'DataBase/dataRep/ubicacion_tecnica.json'
    if not os.path.exists(ruta):
        print("⚠️  No existe ubicacion_tecnica.json")
        return 0
    with open(ruta, 'r', encoding='utf-8') as f:
        data = json.load(f)
    Ubicacion.query.delete()
    db.session.commit()
    count = _migrar_arbol(data, Ubicacion, 'sububicaciones', sep='-')
    db.session.commit()
    print(f"✅ Migradas {count} ubicaciones")
    return count


def migrar_tabs():
    ruta = 'DataBase/tabs.json'
    if not os.path.exists(ruta):
        print("⚠️  No existe tabs.json")
        return 0
    with open(ruta, 'r', encoding='utf-8') as f:
        data = json.load(f)
    Tab.query.delete()
    db.session.commit()
    for item in data:
        tab_id = str(item.get('id', ''))
        s = re.sub(r'\s+', '-', tab_id)
        s = re.sub(r'[^\w\-]', '', s)
        db.session.add(Tab(
            tab_id=tab_id,
            title=item.get('title', ''),
            ruta_jerarquia=item.get('ruta_jerarquia', ''),
            sanitized_id=s
        ))
    db.session.commit()
    print(f"✅ Migrados {len(data)} tabs")
    return len(data)


def migrar_estados():
    ruta = 'DataBase/dataRep/estados.json'
    if not os.path.exists(ruta):
        print("⚠️  No existe estados.json")
        return 0
    with open(ruta, 'r', encoding='utf-8') as f:
        data = json.load(f)
    Estado.query.delete()
    db.session.commit()
    for item in data:
        db.session.add(Estado(nombre=item.get('nombre', ''), emoji=item.get('emoji', '')))
    db.session.commit()
    print(f"✅ Migrados {len(data)} estados")
    return len(data)


def migrar_repuestos():
    ruta = 'DataBase/dataRep/REPUESTOS.json'
    if not os.path.exists(ruta):
        print("⚠️  No existe REPUESTOS.json")
        return 0
    with open(ruta, 'r', encoding='utf-8') as f:
        data = json.load(f)
    Repuesto.query.delete()
    db.session.commit()
    count = 0
    for item in data:
        codigo = item.get('codigo', '')
        if not codigo:
            continue
        rutas = item.get('ruta_jerarquia', [])
        rutas_json = json.dumps(rutas if isinstance(rutas, list) else [])
        db.session.add(Repuesto(
            codigo=str(codigo),
            nombre=item.get('nombre', ''),
            cantidad=int(item.get('cantidad', 0) or 0),
            equipo=item.get('equipo', ''),
            imagen=item.get('imagen', ''),
            fecha_creacion=item.get('fecha_creacion', ''),
            fecha_fin=item.get('fecha_fin', ''),
            link=item.get('link', ''),
            estado=item.get('estado', ''),
            ruta_jerarquia_json=rutas_json
        ))
        count += 1
    db.session.commit()
    print(f"✅ Migrados {count} repuestos")
    return count


def migrar_pagos():
    base_dir = 'DataBase/hogar'
    archivo = os.path.join(base_dir, 'GASTOS.json')
    if not os.path.exists(archivo):
        print("⚠️  No existe GASTOS.json")
        return 0
    Pago.query.delete()
    db.session.commit()
    pagos = []
    claves = set()
    with open(archivo, 'r', encoding='utf-8') as f:
        for item in json.load(f):
            clave = f"{item.get('id','')}-{item.get('vencimiento','')}-{item.get('importe','')}"
            if clave not in claves:
                claves.add(clave)
                pagos.append(item)
    if os.path.exists(base_dir):
        for archivo in os.listdir(base_dir):
            if archivo.startswith('GASTO_') and archivo.endswith('.json'):
                try:
                    with open(os.path.join(base_dir, archivo), 'r', encoding='utf-8') as f:
                        for item in json.load(f):
                            clave = f"{item.get('id','')}-{item.get('vencimiento','')}-{item.get('importe','')}"
                            if clave not in claves:
                                claves.add(clave)
                                pagos.append(item)
                except Exception as e:
                    print(f"⚠️  Error: {e}")
    for item in pagos:
        db.session.add(Pago(
            rubro=item.get('rubro', ''),
            descripcion=item.get('descripcion', ''),
            importe=float(item.get('importe', 0) or 0),
            tipo=item.get('tipo', 'único'),
            cuotas=int(item.get('cuotas', 1) or 1),
            cuota_numero=item.get('cuota_numero'),
            cuota_total=item.get('cuota_total'),
            vencimiento=item.get('vencimiento', ''),
            pagado=bool(item.get('pagado', False))
        ))
    db.session.commit()
    print(f"✅ Migrados {len(pagos)} pagos")
    return len(pagos)


def migrar_nodos():
    ruta = 'DataBase/planos/nodo.json'
    if not os.path.exists(ruta):
        print("⚠️  No existe nodo.json")
        return 0
    with open(ruta, 'r', encoding='utf-8') as f:
        data = json.load(f)
    NodoBloqueo.query.delete()
    db.session.commit()
    for nodo_id, nd in data.items():
        db.session.add(NodoBloqueo(
            id=str(nodo_id),
            nombre=nd.get('nombre', 'Nodo'),
            estado=nd.get('estado', 'apagado'),
            descripcion=nd.get('descripcion', ''),
            padre_id=str(nd['padre']) if nd.get('padre') else None
        ))
    db.session.commit()
    print(f"✅ Migrados {len(data)} nodos")
    return len(data)


def migrar_ot():
    carpeta = 'DataBase/dataOT'
    if not os.path.exists(carpeta):
        print("⚠️  No existe carpeta dataOT")
        return 0
    OrdenTrabajo.query.delete()
    db.session.commit()
    count = 0
    for archivo in os.listdir(carpeta):
        if not archivo.endswith('.JSON'):
            continue
        try:
            with open(os.path.join(carpeta, archivo), 'r', encoding='utf-8') as f:
                for item in json.load(f):
                    db.session.add(OrdenTrabajo(
                        numero_orden=item.get('numero_orden', ''),
                        descripcion=item.get('descripcion', ''),
                        inicio_extremo=item.get('inicio_extremo', ''),
                        fin_extremo=item.get('fin_extremo', ''),
                        equipo_ut=item.get('equipo_ut', ''),
                        descripcion_equipo=item.get('descripcion_equipo', ''),
                        estado=item.get('estado', ''),
                        revision=item.get('revision', ''),
                        archivo_origen=archivo
                    ))
                    count += 1
        except Exception as e:
            print(f"⚠️  Error {archivo}: {e}")
    db.session.commit()
    print(f"✅ Migradas {count} órdenes de trabajo")
    return count


def migrar_todo():
    print("🚀 Iniciando migración de JSON a SQL...")
    print("=" * 60)
    total = 0
    total += migrar_usuarios()
    total += migrar_eventos()
    total += migrar_tareas()
    total += migrar_menu()
    total += migrar_rubros()
    total += migrar_almacenes()
    total += migrar_ubicaciones()
    total += migrar_tabs()
    total += migrar_estados()
    total += migrar_repuestos()
    total += migrar_pagos()
    total += migrar_nodos()
    total += migrar_ot()
    print("=" * 60)
    print(f"✅ Migración completada: {total} registros totales")


if __name__ == '__main__':
    from app import app
    with app.app_context():
        db.create_all()
        migrar_todo()