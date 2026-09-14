# scripts/migrar_equipos.py
"""
Migra el campo 'equipo' de repuestos de '-' a '.'
Ejemplo: 'GMP-PUERTA1-ESTANTE1' → 'GMP.PUERTA1.ESTANTE1'

Uso:
    python scripts/migrar_equipos.py              # Ejecuta la migración
    python scripts/migrar_equipos.py --dry-run    # Solo muestra qué cambiaría
"""
import sys
import os

# Asegurar que se ejecuta desde la raíz del proyecto
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.chdir(project_root)

from app import app
from core.db_sql import db
from core.models import Repuesto, Almacen


def migrar(dry_run=False):
    with app.app_context():
        # 1. Obtener todas las rutas_jerarquia válidas de almacenes
        almacenes = Almacen.query.all()
        rutas_validas = set()
        for a in almacenes:
            if a.ruta_jerarquia:
                rutas_validas.add(a.ruta_jerarquia.strip())

        print(f"✅ Almacenes encontrados: {len(rutas_validas)}")
        for r in sorted(rutas_validas)[:10]:
            print(f"   • {r}")
        if len(rutas_validas) > 10:
            print(f"   ... y {len(rutas_validas) - 10} más")
        print()

        # 2. Construir mapa: versión con '-' → versión con '.'
        mapa = {}
        for ruta in rutas_validas:
            version_guion = ruta.replace('.', '-')
            if version_guion != ruta:
                mapa[version_guion] = ruta

        # 3. Recorrer repuestos y corregir
        repuestos = Repuesto.query.all()
        corregidos = 0
        ya_ok = 0
        sin_equipo = 0
        no_encontrados = []

        for rep in repuestos:
            equipo = (rep.equipo or '').strip()

            if not equipo:
                sin_equipo += 1
                continue

            # Ya está correcto
            if equipo in rutas_validas:
                ya_ok += 1
                continue

            # Intentar convertir '-' → '.'
            equipo_punto = equipo.replace('-', '.')

            if equipo_punto in rutas_validas:
                if not dry_run:
                    rep.equipo = equipo_punto
                corregidos += 1
                print(f"   {'[SIM] ' if dry_run else ''}✅ {rep.codigo}: '{equipo}' → '{equipo_punto}'")
            elif equipo in mapa:
                ruta_correcta = mapa[equipo]
                if not dry_run:
                    rep.equipo = ruta_correcta
                corregidos += 1
                print(f"   {'[SIM] ' if dry_run else ''}✅ {rep.codigo}: '{equipo}' → '{ruta_correcta}'")
            else:
                no_encontrados.append((rep.codigo, equipo))

        if not dry_run:
            db.session.commit()

        # 4. Resumen
        print()
        print("=" * 60)
        print(f"  Total repuestos:       {len(repuestos)}")
        print(f"  Ya correctos:          {ya_ok}")
        print(f"  {'Se corregirían' if dry_run else 'Corregidos'}:        {corregidos}")
        print(f"  Sin equipo:            {sin_equipo}")
        print(f"  No encontrados:        {len(no_encontrados)}")
        print("=" * 60)

        if no_encontrados:
            print("\n  ⚠️  No se pudieron mapear (revisar manualmente):")
            for codigo, equipo in no_encontrados[:20]:
                print(f"     {codigo}: '{equipo}'")
            if len(no_encontrados) > 20:
                print(f"     ... y {len(no_encontrados) - 20} más")

        if dry_run:
            print("\n  💡 Era simulación. Ejecutar sin --dry-run para aplicar.")
        else:
            print("\n  🎉 Migración completada.")


if __name__ == '__main__':
    dry_run = '--dry-run' in sys.argv
    print("=" * 60)
    if dry_run:
        print("  🔍 SIMULACIÓN (no se modifican datos)")
    else:
        print("  🔧 MIGRANDO campo 'equipo' de repuestos")
    print("=" * 60)
    print()
    migrar(dry_run=dry_run)