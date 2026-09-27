"""
scripts/normalizar_almacenes.py
================================
Normaliza el campo 'equipo' de la tabla 'repuestos'.
Convierte formato de ubicaciones (-) a formato de almacenes (.)
solo cuando el valor corresponde a un almacén existente.

Ejecutar: python scripts/normalizar_almacenes.py
"""
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.chdir(project_root)

from app import app
from core.db_sql import db
from core.models import Repuesto, Almacen
from sqlalchemy import text


def normalizar():
    with app.app_context():
        # 1. Obtener todos los almacenes con sus ruta_jerarquia
        almacenes = Almacen.query.all()
        rutas_validas = set()
        mapa_guion_a_punto = {}

        for a in almacenes:
            rutas_validas.add(a.ruta_jerarquia)
            # Crear mapeo: versión con guiones -> versión con puntos
            version_guiones = a.ruta_jerarquia.replace('.', '-')
            mapa_guion_a_punto[version_guiones] = a.ruta_jerarquia

        print(f"📦 Almacenes encontrados: {len(almacenes)}")
        print(f"   Ejemplos: {list(rutas_validas)[:5]}")

        # 2. Buscar repuestos con equipo en formato guion
        repuestos = Repuesto.query.all()
        corregidos = 0
        no_encontrados = []

        for rep in repuestos:
            equipo = rep.equipo or ''
            if not equipo:
                continue

            # Si ya tiene formato correcto, saltar
            if equipo in rutas_validas:
                continue

            # Intentar convertir guiones a puntos
            if equipo in mapa_guion_a_punto:
                nuevo_valor = mapa_guion_a_punto[equipo]
                print(f"  ✅ '{equipo}' → '{nuevo_valor}'")
                rep.equipo = nuevo_valor
                corregidos += 1
            else:
                # No coincide con ningún almacén
                if '-' in equipo:
                    no_encontrados.append(equipo)

        db.session.commit()

        print(f"\n{'='*50}")
        print(f"✅ Repuestos corregidos: {corregidos}")
        if no_encontrados:
            print(f"⚠️  Valores con '-' que NO son almacenes: {len(no_encontrados)}")
            for v in no_encontrados[:10]:
                print(f"   - {v}")
            if len(no_encontrados) > 10:
                print(f"   ... y {len(no_encontrados) - 10} más")
            print("\n   Estos valores probablemente son ubicaciones técnicas")
            print("   guardadas por error en el campo 'equipo'.")
            print("   Revisá manualmente si corresponde moverlos a ruta_jerarquia.")


if __name__ == '__main__':
    normalizar()