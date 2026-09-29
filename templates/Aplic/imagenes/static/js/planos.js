/**
 * planos.js
 * Lógica específica de la vista de planos.
 * - Toggle de flechas en collapse
 * - Confirmación de edición/eliminación con SweetAlert2
 */
(function () {
    'use strict';

    if (window.__planosInitialized) return;
    window.__planosInitialized = true;

    document.addEventListener('DOMContentLoaded', function () {
        if (typeof Swal === 'undefined') {
            console.warn('SweetAlert2 no está disponible en planos.js');
            return;
        }

        // Toggle de flechas en collapse
        document.querySelectorAll('.btn-toggle').forEach(function (btn) {
            btn.addEventListener('click', function () {
                const icon = btn.querySelector('i');
                if (!icon) return;
                setTimeout(function () {
                    if (btn.getAttribute('aria-expanded') === 'true') {
                        icon.classList.remove('bi-caret-right-fill');
                        icon.classList.add('bi-caret-down-fill');
                    } else {
                        icon.classList.remove('bi-caret-down-fill');
                        icon.classList.add('bi-caret-right-fill');
                    }
                }, 120);
            });
        });

        // Confirmación para editar planos
        document.querySelectorAll('.btn-editar-plano').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                const form = btn.closest('form');
                if (!form) return;
                Swal.fire({
                    title: '¿Guardar cambios?',
                    text: '¿Deseas actualizar este plano?',
                    icon: 'question',
                    showCancelButton: true,
                    confirmButtonColor: '#88c999',
                    cancelButtonColor: '#dc3545',
                    confirmButtonText: 'Sí, actualizar',
                    cancelButtonText: 'Cancelar'
                }).then(function (result) {
                    if (result.isConfirmed) form.submit();
                });
            });
        });

        // Confirmación para eliminar planos
        document.querySelectorAll('.btn-eliminar-plano').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                const form = btn.closest('form');
                if (!form) return;
                Swal.fire({
                    title: '¿Estás seguro?',
                    text: 'Esta acción eliminará el plano definitivamente.',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#dc3545',
                    cancelButtonColor: '#88c999',
                    confirmButtonText: 'Sí, eliminar',
                    cancelButtonText: 'Cancelar'
                }).then(function (result) {
                    if (result.isConfirmed) form.submit();
                });
            });
        });
    });
})();