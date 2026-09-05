"""
Gestión del menú de navegación.
Carga y guarda la estructura del menú desde/hacia JSON.
"""
import os
import json

MENU_PATH = 'DataBase/Config/menu.json'


def cargar_menu():
    """Carga el menú desde el archivo JSON."""
    if os.path.exists(MENU_PATH):
        with open(MENU_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def guardar_menu(menu):
    """Guarda el menú en el archivo JSON."""
    with open(MENU_PATH, 'w', encoding='utf-8') as f:
        json.dump(menu, f, ensure_ascii=False, indent=4)