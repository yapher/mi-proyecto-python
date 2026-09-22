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

        // Limpiar opciones existentes (excepto la primera deshabilitada)
        select.querySelectorAll('option:not([disabled])').forEach(o => o.remove());

        // Usar la variable global inyectada de forma segura
        const rutas = window.rutasPlanos || [];

        const emptyWarning = document.getElementById('rutas-empty');

        if (Array.isArray(rutas) && rutas.length) {
            rutas.forEach(r => {
                const opt = document.createElement('option');
                opt.value = r;
                opt.textContent = r;
                select.appendChild(opt);
            });
            if (emptyWarning) emptyWarning.classList.add('d-none');
        } else {
            if (emptyWarning) emptyWarning.classList.remove('d-none');
        }
    });
});