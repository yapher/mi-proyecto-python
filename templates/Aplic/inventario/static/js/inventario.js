// templates/Aplic/inventario/static/js/inventario.js
/**
 * inventario.js — Lógica específica de la aplicación Inventario
 */
document.addEventListener('DOMContentLoaded', function () {
    if (typeof Logger !== 'undefined') {
        Logger.moduleInit('Inventario');
    }

    // Asegurar que el tab activo se muestre correctamente al cargar
    const activeTab = document.querySelector('.inventario-tabs .nav-link.active');
    if (activeTab) {
        const target = activeTab.getAttribute('data-bs-target');
        if (target) {
            const pane = document.querySelector(target);
            if (pane) {
                pane.classList.add('show', 'active');
            }
        }
    }

    if (typeof Logger !== 'undefined') {
        Logger.success('Módulo Inventario inicializado');
    }
});