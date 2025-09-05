# Estilos CSS para Aplicaciones

Esta carpeta contiene los archivos CSS específicos para cada aplicación, separados del código HTML para mantener una mejor organización y mantenibilidad.

## Estructura de Archivos

```
static/css/aplic/
├── main.css                    # Archivo principal que importa todos los estilos
├── agenda.css                  # Estilos específicos para la aplicación Agenda
├── tareas.css                  # Estilos específicos para la aplicación Tareas
├── inventario.css              # Estilos específicos para la aplicación Inventario
├── gestiondeherramientas.css   # Estilos específicos para la aplicación Gestión de Herramientas
└── README.md                   # Este archivo de documentación
```

## Cómo Usar

### 1. En el HTML de cada aplicación
Agregar el siguiente código en la sección `<head>` o al inicio del `{% block content %}`:

```html
<!-- Incluir estilos específicos de la aplicación -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/aplic/NOMBRE_APP.css') }}">
```

### 2. En el layout principal
Para usar todos los estilos de aplicaciones, incluir:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/aplic/main.css') }}">
```

## Beneficios de esta Estructura

1. **Separación de Responsabilidades**: Los estilos están separados del código HTML
2. **Mantenibilidad**: Es más fácil modificar estilos sin tocar el código
3. **Reutilización**: Los estilos pueden ser reutilizados entre aplicaciones
4. **Organización**: Cada aplicación tiene sus propios estilos organizados
5. **Performance**: Los navegadores pueden cachear los archivos CSS por separado

## Convenciones de Nomenclatura

- **Archivos CSS**: `nombreapp.css` (en minúsculas, sin espacios)
- **Clases CSS**: `.app-nombre-clase` (prefijo `app-` para evitar conflictos)
- **IDs**: `#nombre-app-elemento` (prefijo `nombre-app-`)

## Estilos Comunes

El archivo `main.css` incluye estilos comunes que pueden ser utilizados por todas las aplicaciones:

- `.app-container` - Contenedor principal de la aplicación
- `.app-header` - Encabezado de la aplicación
- `.app-btn` - Botones estilizados
- `.app-form-control` - Controles de formulario
- `.app-table` - Tablas estilizadas
- `.app-card` - Tarjetas de contenido
- `.app-alert` - Alertas y notificaciones

## Responsive Design

Todos los archivos CSS incluyen media queries para dispositivos móviles:

```css
@media (max-width: 768px) {
    /* Estilos para móviles */
}
```

## Colores del Tema

- **Primario**: `#88c999` (verde)
- **Secundario**: `#4b376a` (púrpura oscuro)
- **Fondo**: `#3e2d59` (púrpura más oscuro)
- **Texto**: `#ffffff` (blanco)
- **Acentos**: `#8e67c7` (púrpura claro)

## Agregar Nueva Aplicación

Para agregar estilos para una nueva aplicación:

1. Crear el archivo CSS: `static/css/aplic/nuevaapp.css`
2. Agregar la importación en `main.css`
3. Incluir el CSS en el HTML de la aplicación
4. Documentar los estilos específicos

## Ejemplo de Uso

```html
{% extends 'layout.html' %}
{% block content %}

<!-- Incluir estilos específicos de la aplicación -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/aplic/miapp.css') }}">

<div class="app-container">
    <div class="app-header">
        <h1>Mi Aplicación</h1>
    </div>
    
    <div class="app-form-container">
        <form>
            <div class="app-form-group">
                <label class="app-form-label">Campo:</label>
                <input type="text" class="app-form-control">
            </div>
            <button class="app-btn app-btn-primary">Enviar</button>
        </form>
    </div>
</div>

{% endblock %}
```
