import os, json, re, threading, webbrowser


# Funciones de menú
MENU_PATH = 'DataBase/Config/menu.json'

def cargar_menu():
    if os.path.exists(MENU_PATH):
        with open(MENU_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []
    
def guardar_menu(menu):
    with open(MENU_PATH, 'w', encoding='utf-8') as f:
        json.dump(menu, f, ensure_ascii=False, indent=4)