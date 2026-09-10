"""
scripts/sincronizar.py
======================
Sincroniza datos entre SQLite local y PostgreSQL de Render.
Versión corregida para manejar jerarquías, claves foráneas y mapeo de columnas especiales (como Tab).
"""
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Asegurar que se ejecuta desde la raíz
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.chdir(project_root)

from app import app
from core.db_sql import db
from core.models import (
    Usuario, Menu, Evento, Tarea, Estado, Repuesto,
    Pago, NodoBloqueo, Rubro, Almacen, Ubicacion, Tab, OrdenTrabajo
)


def exportar_datos():
    """Exporta todos los datos de la DB actual a JSON"""
    with app.app_context():
        datos = {
            'usuarios': [u.to_dict() for u in Usuario.query.all()],
            'menus': [m.to_dict(include_hijos=True) for m in Menu.query.filter_by(padre_id=None).all()],
            'eventos': [e.to_dict() for e in Evento.query.all()],
            'tareas': [t.to_dict() for t in Tarea.query.all()],
            'estados': [e.to_dict() for e in Estado.query.all()],
            'repuestos': [r.to_dict() for r in Repuesto.query.all()],
            'pagos': [p.to_dict() for p in Pago.query.all()],
            'nodos_bloqueo': {n.id: n.to_dict() for n in NodoBloqueo.query.all()},
            'ordenes_trabajo': [o.to_dict() for o in OrdenTrabajo.query.all()],
            'rubros': [r.to_dict(include_hijos=True) for r in Rubro.query.filter_by(padre_id=None).all()],
            'almacenes': [a.to_dict(include_hijos=True) for a in Almacen.query.filter_by(padre_id=None).all()],
            'ubicaciones': [u.to_dict(include_hijos=True) for u in Ubicacion.query.filter_by(padre_id=None).all()],
            'tabs': [t.to_dict() for t in Tab.query.all()],
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo = f"backup_datos_{timestamp}.json"
        
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        
        total = sum(len(v) if isinstance(v, list) else len(v) for v in datos.values())
        print(f"✅ Exportados {total} registros a {archivo}")
        return archivo


def importar_dict_a_db(datos, db_uri):
    """Importa un diccionario de datos a una DB respetando jerarquías y mapeos especiales."""
    from flask import Flask
    from core.db_sql import db as _db
    from core.models import (
        Usuario, Menu, Evento, Tarea, Estado, Repuesto,
        Pago, NodoBloqueo, Rubro, Almacen, Ubicacion, Tab, OrdenTrabajo
    )
    
    app_temp = Flask(__name__)
    app_temp.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app_temp.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    _db.init_app(app_temp)
    
    with app_temp.app_context():
        _db.create_all()
        
        # 1. Limpiar tablas (en orden por dependencias)
        for modelo in [OrdenTrabajo, Pago, Repuesto, Tab, Estado, 
                       Ubicacion, Almacen, Rubro, Menu, NodoBloqueo, 
                       Tarea, Evento, Usuario]:
            modelo.query.delete()
        _db.session.commit()
        
        # 2. Importar datos planos
        for u in datos.get('usuarios', []):
            _db.session.add(Usuario(**u))
        
        for e in datos.get('eventos', []):
            e_copy = e.copy()
            e_copy.pop('id', None)
            _db.session.add(Evento(**e_copy))
        
        for t in datos.get('tareas', []):
            t_copy = t.copy()
            t_copy.pop('id', None)
            _db.session.add(Tarea(**t_copy))
        
        for e in datos.get('estados', []):
            e_copy = e.copy()
            e_copy.pop('id', None)
            _db.session.add(Estado(**e_copy))
        
        # ✅ CORRECCIÓN AQUÍ: Mapear 'id' de vuelta a 'tab_id'
        for t in datos.get('tabs', []):
            t_copy = t.copy()
            tab_id_val = t_copy.pop('id', None)
            t_copy['tab_id'] = tab_id_val
            _db.session.add(Tab(**t_copy))
        
        for r in datos.get('repuestos', []):
            r_copy = r.copy()
            r_copy.pop('id', None)
            if 'ruta_jerarquia' in r_copy:
                r_copy['ruta_jerarquia_json'] = json.dumps(r_copy.pop('ruta_jerarquia'))
            _db.session.add(Repuesto(**r_copy))
        
        for p in datos.get('pagos', []):
            p_copy = p.copy()
            p_copy.pop('id', None)
            _db.session.add(Pago(**p_copy))
            
        for o in datos.get('ordenes_trabajo', []):
            o_copy = o.copy()
            o_copy.pop('id', None)
            _db.session.add(OrdenTrabajo(**o_copy))
        
        # 3. Importar nodos de bloqueo (ORDENADO PARA EVITAR FK VIOLATION)
        nodos_data = datos.get('nodos_bloqueo', {})
        if isinstance(nodos_data, dict):
            # 3a. Insertar primero los nodos raíz (sin padre)
            for n_id, n_data in nodos_data.items():
                if not n_data.get('padre') and not n_data.get('padre_id'):
                    nodo = NodoBloqueo(
                        id=str(n_data.get('id', n_id)),
                        nombre=n_data.get('nombre', ''),
                        estado=n_data.get('estado', 'apagado'),
                        descripcion=n_data.get('descripcion', ''),
                        padre_id=None
                    )
                    _db.session.add(nodo)
            
            _db.session.flush() # Asegurar que los padres existen en la DB antes de insertar hijos
            
            # 3b. Insertar los nodos hijos
            for n_id, n_data in nodos_data.items():
                padre = n_data.get('padre') or n_data.get('padre_id')
                if padre:
                    nodo = NodoBloqueo(
                        id=str(n_data.get('id', n_id)),
                        nombre=n_data.get('nombre', ''),
                        estado=n_data.get('estado', 'apagado'),
                        descripcion=n_data.get('descripcion', ''),
                        padre_id=str(padre)
                    )
                    _db.session.add(nodo)
        
        # 4. Función auxiliar para importar árboles jerárquicos
        def importar_arbol(items, modelo_cls, clave_hijos, padre_id=None):
            for item in items:
                nombre = item.get('nombre', '')
                if not nombre:
                    continue
                nodo = modelo_cls(
                    nombre=nombre,
                    emoji=item.get('emoji', ''),
                    ruta=item.get('ruta', ''),
                    ruta_jerarquia=item.get('ruta_jerarquia', nombre),
                    padre_id=padre_id
                )
                if hasattr(nodo, 'roles'):
                    nodo.roles = item.get('roles', [])
                if hasattr(nodo, 'imagen'):
                    nodo.imagen = item.get('imagen', '')
                _db.session.add(nodo)
                _db.session.flush() # Flush para obtener el ID generado y usarlo como padre_id en hijos
                hijos = item.get(clave_hijos, [])
                if hijos:
                    importar_arbol(hijos, modelo_cls, clave_hijos, nodo.id)
        
        importar_arbol(datos.get('menus', []), Menu, 'submenues')
        importar_arbol(datos.get('rubros', []), Rubro, 'submenues')
        importar_arbol(datos.get('almacenes', []), Almacen, 'subcrear_almacenes')
        importar_arbol(datos.get('ubicaciones', []), Ubicacion, 'sububicaciones')
        
        _db.session.commit()
        print(f"✅ Datos importados correctamente")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python scripts/sincronizar.py exportar  → Exportar datos actuales")
        print("  python scripts/sincronizar.py importar <archivo.json>  → Importar datos")
    elif sys.argv[1] == 'exportar':
        exportar_datos()
    elif sys.argv[1] == 'importar' and len(sys.argv) > 2:
        # Leer el archivo y pasar los datos
        archivo_json = sys.argv[2]
        if not os.path.exists(archivo_json):
            print(f"❌ No existe el archivo: {archivo_json}")
        else:
            with open(archivo_json, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            # Usar la URI de la app actual
            importar_dict_a_db(datos, app.config['SQLALCHEMY_DATABASE_URI'])
            print(f"🎉 Sincronización completada desde {archivo_json}")
    else:
        print("Comando no válido")