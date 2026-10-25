/**
* listarepuestos.js
* - Toggle entre vista cards y lista, con persistencia en localStorage
* - Búsqueda dinámica (mientras se escribe), sin distinguir tildes ni mayúsculas
*/
(function () {
    'use strict';

    // ------------------------------------------------------------
    // Utilidades
    // ------------------------------------------------------------
    function normalizar(texto) {
        return String(texto == null ? '' : texto)
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .trim();
    }

    // ------------------------------------------------------------
    // Toggle de vista (cards / lista)
    // ------------------------------------------------------------
    function initToggleVista() {
        const toggleBtns = document.querySelectorAll('.lr-view-btn');
        const container = document.getElementById('repuestosContainer');
        if (!toggleBtns.length || !container) return;

        const setView = (view) => {
            toggleBtns.forEach(b => b.classList.toggle('active', b.dataset.view === view));
            container.classList.toggle('lr-grid--list', view === 'list');
            try { localStorage.setItem('lr-view', view); } catch (e) {}
        };

        toggleBtns.forEach(btn => {
            btn.addEventListener('click', () => setView(btn.dataset.view));
        });

        try {
            const saved = localStorage.getItem('lr-view');
            if (saved === 'list') setView('list');
        } catch (e) {}
    }

    // ------------------------------------------------------------
    // Búsqueda dinámica
    // ------------------------------------------------------------
    function initBusquedaDinamica() {
        const inputNombre = document.getElementById('filtroNombre');
        const inputCodigo = document.getElementById('filtroCodigo');
        const container = document.getElementById('repuestosContainer');
        if (!container || (!inputNombre && !inputCodigo)) return;

        const cards = Array.from(container.querySelectorAll('.rep-card'));
        const contador = document.getElementById('repuestosContador');
        const sinResultados = document.getElementById('repuestosSinResultados');
        const exportNombre = document.getElementById('exportNombre');
        const exportCodigo = document.getElementById('exportCodigo');

        // Texto normalizado de cada card (se calcula una sola vez)
        const indice = cards.map(card => ({
            card: card,
            nombre: normalizar(card.dataset.nombre),
            comentario: normalizar(card.dataset.comentario),
            codigo: normalizar(card.dataset.codigo)
        }));

        function filtrar() {
            const termNombre = normalizar(inputNombre ? inputNombre.value : '');
            const termCodigo = normalizar(inputCodigo ? inputCodigo.value : '');
            let visibles = 0;

            indice.forEach(item => {
                const okNombre = !termNombre ||
                    item.nombre.indexOf(termNombre) !== -1 ||
                    item.comentario.indexOf(termNombre) !== -1;
                const okCodigo = !termCodigo || item.codigo.indexOf(termCodigo) !== -1;
                const mostrar = okNombre && okCodigo;

                item.card.style.display = mostrar ? '' : 'none';
                if (mostrar) visibles++;
            });

            if (contador) contador.textContent = visibles;
            if (sinResultados) sinResultados.classList.toggle('d-none', visibles > 0);

            // El PDF sale con lo mismo que se ve en pantalla
            if (exportNombre && inputNombre) exportNombre.value = inputNombre.value.trim();
            if (exportCodigo && inputCodigo) exportCodigo.value = inputCodigo.value.trim();
        }

        let timer = null;
        function programar() {
            clearTimeout(timer);
            timer = setTimeout(filtrar, 80);
        }

        if (inputNombre) inputNombre.addEventListener('input', programar);
        if (inputCodigo) inputCodigo.addEventListener('input', programar);

        // Si la página cargó con un filtro ya escrito, aplicarlo
        filtrar();
    }

    document.addEventListener('DOMContentLoaded', function () {
        initToggleVista();
        initBusquedaDinamica();
    });
})();