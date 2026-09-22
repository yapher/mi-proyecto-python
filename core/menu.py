"""
Gestión del menú de navegación.
AHORA USA SQL en lugar de JSON.
"""
from core.db_sql_store import menu_store


def cargar_menu():
    """Carga el menú desde SQL (retorna lista de dicts con submenues)."""
    return menu_store.cargar_arbol()


def guardar_menu(menu):
    """
    Reemplaza todo el menú.
    Nota: Esta función se mantiene por compatibilidad, pero idealmente
    se deberían usar las operaciones atómicas de menu_store.
    """
    from core.db_sql import db
    from core.models import Menu

    Menu.query.delete()
    db.session.commit()

    def _crear_nodos(items, padre_id=None, ruta_padre=''):
        for item in items:
            nombre = item.get('nombre', '')
            if not nombre:
                continue
            ruta_jerarquia = f"{ruta_padre}.{nombre}" if ruta_padre else nombre
            nodo = Menu(
                nombre=nombre,
                emoji=item.get('emoji', ''),
                ruta=item.get('ruta', ''),
                ruta_jerarquia=ruta_jerarquia,
                padre_id=padre_id
            )
            db.session.add(nodo)
            db.session.flush()
            submenues = item.get('submenues', [])
            if submenues:
                _crear_nodos(submenues, padre_id=nodo.id, ruta_padre=ruta_jerarquia)

    _crear_nodos(menu if isinstance(menu, list) else [])
    db.session.commit()


def obtener_roles_por_ruta(ruta):
    """
    Busca en el menú los roles requeridos para una ruta específica.
    Retorna lista de roles o [] si no hay restricciones.
    
    Uso:
        roles = obtener_roles_por_ruta('/gestion_usuarios')
        # Retorna: ['admin'] o [] si no hay restricciones
    """
    menu = cargar_menu()
    
    def buscar_en_nodos(nodos):
        for nodo in nodos:
            # Verificar ruta exacta
            if nodo.get('ruta') == ruta:
                return nodo.get('roles', [])
            # Buscar recursivamente en submenús
            sub = nodo.get('submenues', [])
            if sub:
                resultado = buscar_en_nodos(sub)
                if resultado is not None:
                    return resultado
        return None
    
    roles = buscar_en_nodos(menu)
    return roles if roles is not None else []