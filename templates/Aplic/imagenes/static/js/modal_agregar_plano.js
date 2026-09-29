/**
 * modal_agregar_plano.js
 * Carga dinámica de rutas en el modal de agregar plano.
 * Lee los datos desde data-attributes del DOM.
 */
(function () {
    'use strict';

    if (window.__modalAgregarPlanoInitialized) return;
    window.__modalAgregarPlanoInitialized = true;

    document.addEventListener('DOMContentLoaded', function () {
        const modal = document.getElementById('modalAgregarPlano');
        if (!modal) return;

        modal.addEventListener('show.bs.modal', function () {
            const select = document.getElementById('nombre_linea');
            if (!select) return;

            // Limpiar opciones (mantener solo la disabled)
            select.querySelectorAll('option:not([disabled])').forEach(function (o) {
                o.remove();
            });

            // Leer rutas desde data-attribute
            const dataNode = document.getElementById('planos-data');
            let rutas = [];
            try {
                const raw = dataNode ? dataNode.getAttribute('data-rutas') : null;
                rutas = raw ? JSON.parse(raw) : [];
            } catch (error) {
                console.error('Error parseando rutas de planos:', error);
                rutas = [];
            }

            const emptyWarning = document.getElementById('rutas-empty');

            if (Array.isArray(rutas) && rutas.length > 0) {
                rutas.forEach(function (r) {
                    const opt = document.createElement('option');
                    opt.value = r;
                    opt.textContent = r;
                    select.appendChild(opt);
                });
                if (emptyWarning) emptyWarning.classList.add('d-none');
            } else {
                if (emptyWarning) emptyWarning.classList.remove('d-none');
                console.warn('No se encontraron rutas técnicas para cargar en el select.');
            }
        });
    });
})();