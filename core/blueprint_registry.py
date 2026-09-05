# core/blueprint_registry.py
"""
Auto-descubrimiento y registro de Blueprints.
Escanea templates/Aplic/*/BackEnd/*.py y registra cualquier
variable que sea instancia de flask.Blueprint.

Ventajas:
- Agregar una app nueva = solo crear su carpeta, NO tocar app.py
- Elimina 30+ líneas de imports manuales
- tolerante a errores: si un módulo falla, sigue cargando los demás
"""
import importlib
import pkgutil
import os
from pathlib import Path
from flask import Blueprint


def _iter_app_modules(base_dir="templates/Aplic"):
    """Itera todos los módulos .py dentro de templates/Aplic/**/BackEnd/."""
    base_path = Path(base_dir)
    if not base_path.exists():
        return

    for backend_dir in base_path.glob("*/BackEnd"):
        if not backend_dir.is_dir():
            continue
        app_name = backend_dir.parent.name  # ej: "agenda"
        for py_file in backend_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
            module_name = py_file.stem  # ej: "agenda"
            # Ruta como módulo python: templates.Aplic.agenda.BackEnd.agenda
            yield f"templates.Aplic.{app_name}.BackEnd.{module_name}"


def auto_register_blueprints(app, base_dir="templates/Aplic"):
    """
    Escanea el directorio de aplicaciones y registra automáticamente
    todos los Blueprint que encuentre.

    Uso en app.py:
        from core.blueprint_registry import auto_register_blueprints
        auto_register_blueprints(app)
    """
    registered = []
    errors = []

    for module_path in _iter_app_modules(base_dir):
        try:
            module = importlib.import_module(module_path)
        except Exception as e:
            errors.append((module_path, f"import error: {e}"))
            continue

        # Buscar todas las variables que sean Blueprint
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, Blueprint):
                try:
                    # Evitar registrar el mismo blueprint dos veces
                    if attr.name not in [b.name for b in app.blueprints.values()]:
                        app.register_blueprint(attr)
                        registered.append(f"{attr.name} <- {module_path}")
                except Exception as e:
                    errors.append((attr.name, f"register error: {e}"))

    # Log opcional (útil en desarrollo)
    if os.environ.get("FLASK_DEBUG") == "1" or os.environ.get("TESTING") != "1":
        print(f"[auto_register] {len(registered)} blueprints registrados:")
        for r in registered:
            print(f"  ✓ {r}")
        if errors:
            print(f"[auto_register] {len(errors)} errores:")
            for path, err in errors:
                print(f"  ✗ {path}: {err}")

    return registered, errors