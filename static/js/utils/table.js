// static/js/utils/table.js
(function () {
    'use strict';

    if (window.__tableFilterInitialized) {
        return;
    }

    window.__tableFilterInitialized = true;

    function findTable(root) {
        if (!root) {
            return null;
        }

        return (
            root.querySelector('table.js-tabla-repuestos') ||
            root.querySelector('#tabla') ||
            root.querySelector('.tabla') ||
            root.querySelector('table')
        );
    }

    function findRoot(input) {
        return (
            input.closest('[data-tabla-repuestos]') ||
            input.closest('.modal-body') ||
            input.closest('.tabla-container') ||
            input.closest('#tabla-container') ||
            input.closest('.repuestos-content-area') ||
            input.closest('.card') ||
            document
        );
    }

    function filter(input) {
        if (!input) {
            return;
        }

        const term = (input.value || '').toLowerCase().trim();
        const root = findRoot(input);
        const table = findTable(root);

        if (!table) {
            return;
        }

        const rows = table.querySelectorAll('tbody tr');

        rows.forEach(function (row) {
            const text = (row.textContent || '').toLowerCase();
            row.style.display = (!term || text.indexOf(term) !== -1) ? '' : 'none';
        });
    }

    function bind() {
        if (window.__tableFilterBound) {
            return;
        }

        window.__tableFilterBound = true;

        function handler(event) {
            const target = event.target;

            if (!target) {
                return;
            }

            if (
                target.id === 'buscarEnModal' ||
                target.id === 'buscarTabla' ||
                target.classList.contains('js-filtrar-tabla') ||
                target.classList.contains('filtro-tabla')
            ) {
                filter(target);
            }
        }

        document.addEventListener('input', handler);
        document.addEventListener('keyup', handler);

        // ✅ Exportar PDF: enviar el texto del buscador de la misma pestaña
        document.addEventListener('submit', function (event) {
            const form = event.target;

            if (!form || !form.classList || !form.classList.contains('js-exportar-pdf-repuestos')) {
                return;
            }

            const scope = form.closest('.tab-pane') || form.closest('[data-tabla-repuestos]') || document;
            const input = scope.querySelector('.js-filtrar-tabla');
            const hidden = form.querySelector('input[name="buscar"]');

            if (input && hidden && (input.value || '').trim()) {
                hidden.value = input.value.trim();
            }
        });
    }

    window.TableFilter = {
        filter: filter,
        bind: bind
    };

    bind();
})();