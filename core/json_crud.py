"""
core/json_crud.py
=================
Extensión de JsonStore que permite trabajar con campos únicos arbitrarios.

Mientras JsonStore asume que el identificador es "id" (autoincremental),
UniqueFieldStore permite configurar cualquier campo como identificador único
(ej: "codigo", "email", "username", etc.).

Usado por:
  - estadosderepuestos (identificador: "codigo")
  - (futuras apps que necesiten identificadores personalizados)

Uso:
    from core.json_crud import UniqueFieldStore
    
    # Store con campo único "codigo" (sin auto-incremento de ID)
    store = UniqueFieldStore('DataBase/dataRep/REPUESTOS.json', unique_field='codigo')
    
    # Crear (valida unicidad)
    exito, msg = store.crear({'codigo': 'ABC123', 'nombre': 'Repuesto X'})
    
    # Buscar por campo único
    item = store.buscar_por_codigo('ABC123')
    
    # Actualizar por campo único
    store.actualizar_por_codigo('ABC123', {'nombre': 'Nuevo nombre'})
    
    # Eliminar por campo único
    store.eliminar_por_codigo('ABC123')
    
    # También funciona con JsonStore estándar
    store2 = UniqueFieldStore('data.json')  # usa "id" por defecto
"""
from core.db_json import JsonStore


class UniqueFieldStore(JsonStore):
    """
    JsonStore con soporte para campo único personalizado.
    
    Características:
      - Hereda TODA la funcionalidad de JsonStore (cargar, guardar, buscar, etc.)
      - Agrega validación de unicidad al crear/actualizar
      - Métodos helper: buscar_por_<campo>, actualizar_por_<campo>, eliminar_por_<campo>
      - No auto-incrementa ID si el campo único no es "id"
    """
    
    def __init__(self, db_path, unique_field='id', auto_id=None):
        """
        Args:
            db_path: Ruta al archivo JSON
            unique_field: Nombre del campo que actúa como identificador único
                         (default: 'id')
            auto_id: Si True, auto-incrementa el campo único al crear.
                    Si None, se auto-detecta: True si unique_field='id', False si no.
        """
        super().__init__(db_path)
        self.unique_field = unique_field
        
        # Auto-detectar si debe auto-incrementar
        if auto_id is None:
            self.auto_id = (unique_field == 'id')
        else:
            self.auto_id = auto_id
    
    # ============================================================
    # MÉTODOS DE BÚSQUEDA POR CAMPO ÚNICO
    # ============================================================
    
    def buscar_por_unique(self, valor):
        """Busca un item por el campo único configurado."""
        return self.buscar_uno(**{self.unique_field: valor})
    
    def existe_por_unique(self, valor):
        """Verifica si existe un item con el valor dado en el campo único."""
        return self.existe(valor) if self.unique_field == 'id' else any(
            str(item.get(self.unique_field)) == str(valor)
            for item in self.cargar()
        )
    
    # ============================================================
    # CREAR CON VALIDACIÓN DE UNICIDAD
    # ============================================================
    
    def crear(self, item, skip_unique_check=False):
        """
        Crea un nuevo item validando unicidad del campo configurado.
        
        Args:
            item: Dict con los datos del item
            skip_unique_check: Si True, no valida unicidad (útil para migraciones)
        
        Returns:
            tuple: (exito: bool, mensaje: str)
                - (True, "Creado correctamente") si fue exitoso
                - (False, "Ya existe...") si hay duplicado
        """
        valor_unico = item.get(self.unique_field)
        
        # Validar que el campo único esté presente
        if valor_unico is None or str(valor_unico).strip() == '':
            return False, f"El campo '{self.unique_field}' es obligatorio"
        
        # Validar unicidad
        if not skip_unique_check and self.existe_por_unique(valor_unico):
            return False, f"Ya existe un item con {self.unique_field}='{valor_unico}'"
        
        # Auto-incrementar si corresponde
        if self.auto_id and self.unique_field == 'id':
            items = self.cargar()
            item['id'] = max([e.get('id', 0) for e in items], default=0) + 1
        
        # Guardar
        items = self.cargar()
        items.append(item)
        self.guardar(items)
        
        return True, "Creado correctamente"
    
    # ============================================================
    # ACTUALIZAR POR CAMPO ÚNICO
    # ============================================================
    
    def actualizar_por_unique(self, valor_original, nuevos_datos, check_new_unique=True):
        """
        Actualiza un item identificado por su campo único.
        
        Args:
            valor_original: Valor actual del campo único
            nuevos_datos: Dict con los campos a actualizar
            check_new_unique: Si True y se cambia el campo único, valida que el
                            nuevo valor no exista ya
        
        Returns:
            tuple: (exito: bool, mensaje: str)
        """
        items = self.cargar()
        encontrado = False
        
        # Si se está cambiando el campo único, validar que el nuevo valor no exista
        nuevo_valor = nuevos_datos.get(self.unique_field)
        if (check_new_unique and nuevo_valor is not None 
                and str(nuevo_valor) != str(valor_original)):
            if self.existe_por_unique(nuevo_valor):
                return False, f"El nuevo {self.unique_field}='{nuevo_valor}' ya existe"
        
        for i, item in enumerate(items):
            if str(item.get(self.unique_field)) == str(valor_original):
                items[i].update(nuevos_datos)
                encontrado = True
                break
        
        if not encontrado:
            return False, f"No se encontró item con {self.unique_field}='{valor_original}'"
        
        self.guardar(items)
        return True, "Actualizado correctamente"
    
    # ============================================================
    # ELIMINAR POR CAMPO ÚNICO
    # ============================================================
    
    def eliminar_por_unique(self, valor):
        """
        Elimina un item identificado por su campo único.
        
        Returns:
            tuple: (exito: bool, mensaje: str)
        """
        items = self.cargar()
        items_filtrados = [
            item for item in items
            if str(item.get(self.unique_field)) != str(valor)
        ]
        
        if len(items_filtrados) < len(items):
            self.guardar(items_filtrados)
            return True, "Eliminado correctamente"
        
        return False, f"No se encontró item con {self.unique_field}='{valor}'"


# ============================================================
# ALIAS PARA COMPATIBILIDAD
# ============================================================
# JsonCrudStore es un alias de UniqueFieldStore para quienes prefieran ese nombre
JsonCrudStore = UniqueFieldStore