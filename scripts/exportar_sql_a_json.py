"""
scripts/exportar_sql_a_json.py
===============================
Exporta TODOS los datos de SQL a archivos JSON.
Útil para tener respaldo o migrar a otra instancia.
"""
import sys
import os

# Agregar la raíz del proyecto al path para poder importar 'app'
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Cambiar al directorio raíz del proyecto
os.chdir(project_root)

import json
from datetime import datetime
from app import app
from core.db_sql import db
from core.models import (
    Usuario, Menu, Evento, Tarea, Estado, Repuesto,
    Pago, NodoBloqueo, OrdenTrabajo, Rubro, Almacen,
    Ubicacion, Tab
)


def exportar_menu():
    """Exporta menú completo con jerarquía."""
    def construir_arbol(nodos_padre):
        resultado = []
        for nodo in nodos_padre:
            item = {
                'nombre': nodo.nombre,
                'emoji': nodo.emoji,
                'ruta': nodo.ruta,
                'ruta_jerarquia': nodo.ruta_jerarquia,
                'roles': nodo.roles or [],
                'submenues': construir_arbol(nodo.hijos)
            }
            resultado.append(item)
        return resultado
    
    raices = Menu.query.filter_by(padre_id=None).order_by(Menu.id).all()
    return construir_arbol(raices)


def exportar_todo():
    """Exporta todos los datos a una carpeta de respaldo."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_sql_export_{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)
    os.makedirs(os.path.join(backup_dir, "DataBase", "Config"), exist_ok=True)
    os.makedirs(os.path.join(backup_dir, "DataBase", "time"), exist_ok=True)
    os.makedirs(os.path.join(backup_dir, "DataBase", "dataRep"), exist_ok=True)
    os.makedirs(os.path.join(backup_dir, "DataBase", "hogar"), exist_ok=True)
    os.makedirs(os.path.join(backup_dir, "DataBase", "planos"), exist_ok=True)
    
    with app.app_context():
        total = 0
        
        # 1. Usuarios
        usuarios = [u.to_dict() for u in Usuario.query.all()]
        with open(os.path.join(backup_dir, "users.json"), 'w', encoding='utf-8') as f:
            json.dump(usuarios, f, indent=4, ensure_ascii=False)
        print(f"✅ users.json: {len(usuarios)} usuarios")
        total += len(usuarios)
        
        # 2. Eventos (agenda)
        eventos = [e.to_dict() for e in Evento.query.all()]
        with open(os.path.join(backup_dir, "DataBase", "time", "agenda.json"), 'w', encoding='utf-8') as f:
            json.dump(eventos, f, indent=4, ensure_ascii=False)
        print(f"✅ agenda.json: {len(eventos)} eventos")
        total += len(eventos)
        
        # 3. Tareas
        tareas = [t.to_dict() for t in Tarea.query.all()]
        with open(os.path.join(backup_dir, "DataBase", "time", "dataTask.json"), 'w', encoding='utf-8') as f:
            json.dump(tareas, f, indent=4, ensure_ascii=False)
        print(f"✅ dataTask.json: {len(tareas)} tareas")
        total += len(tareas)
        
        # 4. Menú
        menu = exportar_menu()
        with open(os.path.join(backup_dir, "DataBase", "Config", "menu.json"), 'w', encoding='utf-8') as f:
            json.dump(menu, f, indent=4, ensure_ascii=False)
        print(f"✅ menu.json: {len(menu)} raíces")
        total += Menu.query.count()
        
        # 5. Estados
        estados = [e.to_dict() for e in Estado.query.all()]
        with open(os.path.join(backup_dir, "DataBase", "dataRep", "estados.json"), 'w', encoding='utf-8') as f:
            json.dump(estados, f, indent=4, ensure_ascii=False)
        print(f"✅ estados.json: {len(estados)} estados")
        total += len(estados)
        
        # 6. Repuestos
        repuestos = [r.to_dict() for r in Repuesto.query.all()]
        with open(os.path.join(backup_dir, "DataBase", "dataRep", "REPUESTOS.json"), 'w', encoding='utf-8') as f:
            json.dump(repuestos, f, indent=4, ensure_ascii=False)
        print(f"✅ REPUESTOS.json: {len(repuestos)} repuestos")
        total += len(repuestos)
        
        # 7. Pagos
        pagos = [p.to_dict() for p in Pago.query.all()]
        with open(os.path.join(backup_dir, "DataBase", "hogar", "GASTOS.json"), 'w', encoding='utf-8') as f:
            json.dump(pagos, f, indent=4, ensure_ascii=False)
        print(f"✅ GASTOS.json: {len(pagos)} pagos")
        total += len(pagos)
        
        # 8. Nodos de bloqueo
        nodos = {}
        for n in NodoBloqueo.query.all():
            nodos[n.id] = n.to_dict()
        with open(os.path.join(backup_dir, "DataBase", "planos", "nodo.json"), 'w', encoding='utf-8') as f:
            json.dump(nodos, f, indent=4, ensure_ascii=False)
        print(f"✅ nodo.json: {len(nodos)} nodos")
        total += len(nodos)
        
        # 9. Tabs
        tabs = [t.to_dict() for t in Tab.query.all()]
        with open(os.path.join(backup_dir, "DataBase", "tabs.json"), 'w', encoding='utf-8') as f:
            json.dump(tabs, f, indent=4, ensure_ascii=False)
        print(f"✅ tabs.json: {len(tabs)} tabs")
        total += len(tabs)
        
        # 10. Rubros
        def construir_arbol_rubros(nodos_padre):
            resultado = []
            for nodo in nodos_padre:
                item = {
                    'nombre': nodo.nombre,
                    'emoji': nodo.emoji,
                    'ruta': nodo.ruta,
                    'ruta_jerarquia': nodo.ruta_jerarquia,
                    'submenues': construir_arbol_rubros(nodo.hijos)
                }
                resultado.append(item)
            return resultado
        rubros = construir_arbol_rubros(Rubro.query.filter_by(padre_id=None).all())
        with open(os.path.join(backup_dir, "DataBase", "hogar", "rubro.json"), 'w', encoding='utf-8') as f:
            json.dump(rubros, f, indent=4, ensure_ascii=False)
        print(f"✅ rubro.json: {Rubro.query.count()} rubros")
        total += Rubro.query.count()
        
        # 11. Almacenes
        def construir_arbol_almacenes(nodos_padre):
            resultado = []
            for nodo in nodos_padre:
                item = {
                    'nombre': nodo.nombre,
                    'emoji': nodo.emoji,
                    'ruta': nodo.ruta,
                    'ruta_jerarquia': nodo.ruta_jerarquia,
                    'subcrear_almacenes': construir_arbol_almacenes(nodo.hijos)
                }
                resultado.append(item)
            return resultado
        almacenes = construir_arbol_almacenes(Almacen.query.filter_by(padre_id=None).all())
        with open(os.path.join(backup_dir, "DataBase", "dataRep", "almacenes.json"), 'w', encoding='utf-8') as f:
            json.dump(almacenes, f, indent=4, ensure_ascii=False)
        print(f"✅ almacenes.json: {Almacen.query.count()} almacenes")
        total += Almacen.query.count()
        
        # 12. Ubicaciones
        def construir_arbol_ubicaciones(nodos_padre):
            resultado = []
            for nodo in nodos_padre:
                item = {
                    'nombre': nodo.nombre,
                    'emoji': nodo.emoji,
                    'ruta': nodo.ruta,
                    'ruta_jerarquia': nodo.ruta_jerarquia,
                    'imagen': nodo.imagen,
                    'sububicaciones': construir_arbol_ubicaciones(nodo.hijos)
                }
                resultado.append(item)
            return resultado
        ubicaciones = construir_arbol_ubicaciones(Ubicacion.query.filter_by(padre_id=None).all())
        with open(os.path.join(backup_dir, "DataBase", "dataRep", "ubicacion_tecnica.json"), 'w', encoding='utf-8') as f:
            json.dump(ubicaciones, f, indent=4, ensure_ascii=False)
        print(f"✅ ubicacion_tecnica.json: {Ubicacion.query.count()} ubicaciones")
        total += Ubicacion.query.count()
        
        print("\n" + "=" * 60)
        print(f"✅ EXPORTACIÓN COMPLETA: {total} registros")
        print(f"📁 Carpeta de respaldo: {backup_dir}")
        print("=" * 60)


if __name__ == '__main__':
    exportar_todo()