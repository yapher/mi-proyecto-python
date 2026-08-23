"""
COMPATIBILIDAD: Este archivo re-exporta desde core.menu
Migración: usar directamente `from core.menu import cargar_menu, guardar_menu`
"""
from core.menu import cargar_menu, guardar_menu, MENU_PATH

__all__ = ['cargar_menu', 'guardar_menu', 'MENU_PATH']