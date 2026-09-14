// templates/Aplic/listarot/static/js/filtroTorta.js
/**
 * filtroTorta.js — Abre el modal automáticamente al cargar
 */
document.addEventListener('DOMContentLoaded', function () {
    const modalEl = document.getElementById('filtroTortaModal');
    if (modalEl) {
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    }
});