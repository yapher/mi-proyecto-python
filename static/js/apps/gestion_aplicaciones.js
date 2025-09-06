/**
 * JavaScript para el componente Gestión de Aplicaciones
 * Maneja la creación de nuevas aplicaciones
 */

// Variables globales para los elementos del DOM
let nombreInput;
let btnAgregar;

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Obtener elementos del DOM
    nombreInput = document.getElementById('nombre');
    btnAgregar = document.getElementById('btnAgregar');

    // Event listener para mostrar/ocultar botón
    if (nombreInput && btnAgregar) {
        nombreInput.addEventListener('input', () => {
            if (nombreInput.value.trim().length > 0) {
                btnAgregar.classList.add('active');
            } else {
                btnAgregar.classList.remove('active');
            }
        });
    }
});

/**
 * Función para crear una nueva aplicación
 */
async function crear() {
    const nombre = nombreInput.value.trim();
    if (!nombre) {
        alert("Por favor, ingresa un nombre.");
        return;
    }

    try {
        const response = await fetch('/crear_app', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nombre })
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.msg);
            nombreInput.value = '';
            btnAgregar.classList.remove('active');
        } else {
            alert("Error: " + data.msg);
        }
    } catch (error) {
        alert("Error de conexión: " + error.message);
    }
}
