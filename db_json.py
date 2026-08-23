"""
COMPATIBILIDAD: Este archivo re-exporta desde core.db_json
Migración: usar directamente `from core.db_json import JsonStore`
"""
from core.db_json import JsonStore

__all__ = ['JsonStore']