/**
 * modal_agregar_plano.js
 * Maneja la carga dinámica de rutas en el modal de agregar plano.
 * Usa la variable global window.rutasPlanos inyectada desde el template principal.
 */
document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('modalAgregarPlano');
    if (!modal) return;

    modal.addEventListener('show.bs.modal', function () {
        const select = document.getElementById('nombre_linea');
        if (!select) return;

        // 1. Limpiar opciones existentes (mantener solo la opción por defecto deshabilitada)
        select.querySelectorAll('option:not([disabled])').forEach(o => o.remove());

        // 2. Usar la variable global inyectada de forma segura
        const rutas = window.rutasPlanos || [];
        const emptyWarning = document.getElementById('rutas-empty');

        // 3. Poblar el select
        if (Array.isArray(rutas) && rutas.length > 0) {
            rutas.forEach(r => {
                const opt = document.createElement('option');
                opt.value = r;
                opt.textContent = r;
                select.appendChild(opt);
            });
            
            // Ocultar advertencia de vacío
            if (emptyWarning) emptyWarning.classList.add('d-none');
        } else {
            // Mostrar advertencia si no hay rutas
            if (emptyWarning) emptyWarning.classList.remove('d-none');
            console.warn('⚠️ No se encontraron rutas técnicas para cargar en el select.');
        }
    });
});