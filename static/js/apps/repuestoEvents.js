/**
 * repuestoEvents.js
 * Manejo de eventos del DOM y del ciclo de vida del modal.
 * Responsabilidad: Escuchar clicks y eventos de Bootstrap, delegar la lógica.
 */
document.addEventListener('DOMContentLoaded', () => {
    // 1. Inicializar plugins al cargar la página
    RepuestoUtils.initSelect2();

    const modal = document.getElementById('agregarModal');
    if (!modal) {
        console.error("❌ No se encontró el modal #agregarModal");
        return;
    }

    // 2. Evento: ANTES de que el modal se muestre
    modal.addEventListener('show.bs.modal', (event) => {
        const button = event.relatedTarget; // El botón que disparó el modal
        
        if (!button) {
            RepuestoForm.resetear();
            return;
        }

        if (button.classList.contains('btn-editar')) {
            // Modo Edición
            RepuestoForm.configurarAccion(true, button.getAttribute('data-tab_activo'));
            RepuestoForm.cargarDatos(button);
        } else if (button.classList.contains('btn-agregar')) {
            // Modo Agregar
            RepuestoForm.resetear();
            RepuestoForm.configurarAccion(false, button.getAttribute('data-sanitized_id'));
        }
    });

    // 3. Evento: DESPUÉS de que el modal se cierre (limpieza preventiva)
    modal.addEventListener('hidden.bs.modal', () => {
        RepuestoForm.resetear();
    });
});