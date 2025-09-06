/**
 * JavaScript para el componente Tareas
 * Maneja la funcionalidad del modal de edición de tareas
 */

// Variables globales
let popupModal;

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function () {
    // Obtener el modal de Bootstrap
    var popupModalEl = document.getElementById('popup');
    popupModal = new bootstrap.Modal(popupModalEl, { keyboard: false });

    const form = document.getElementById('edit-form');

    // Configurar event listeners para los elementos de tareas
    document.querySelectorAll('.event-info').forEach(function (div) {
        div.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            const titulo = this.getAttribute('data-titulo');
            const fecha = this.getAttribute('data-fecha');
            const descripcion = this.getAttribute('data-descripcion');

            // Llenar el formulario con los datos de la tarea
            document.getElementById('edit-id').value = id;
            document.getElementById('edit-titulo').value = titulo;
            document.getElementById('edit-fecha').value = fecha;
            document.getElementById('edit-descripcion').value = descripcion;

            // Configurar la acción del formulario
            form.action = '/editar/' + id;

            // Mostrar el modal usando Bootstrap API
            popupModal.show();
        });
    });

    // El botón cancelar y el botón cerrar ya manejan el cierre por data-bs-dismiss="modal"
    // No hace falta un listener extra para cerrar el modal
});
