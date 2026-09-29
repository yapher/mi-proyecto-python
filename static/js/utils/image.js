// static/js/utils/image.js
(function () {
    'use strict';

    if (window.__imageViewerInitialized) {
        return;
    }

    window.__imageViewerInitialized = true;

    const Logger = window.Logger || {
        error: function () {}
    };

    function getInstance(element) {
        if (!element) {
            return null;
        }

        if (!window.bootstrap || !window.bootstrap.Modal) {
            Logger.error('Bootstrap no está disponible para abrir modales de imagen.');
            return null;
        }

        let instance = window.bootstrap.Modal.getInstance(element);

        if (!instance) {
            instance = new window.bootstrap.Modal(element);
        }

        return instance;
    }

    function open(src, title) {
        const modalEl = document.getElementById('modalImagenAmpliada');

        if (!modalEl) {
            if (src) {
                window.open(src, '_blank');
            }
            return;
        }

        const img = document.getElementById('imagenAmpliada');
        const titleLabel = document.getElementById('tituloImagenAmpliada');

        if (img) {
            img.src = src || '';
        }

        if (titleLabel) {
            titleLabel.textContent = title || 'Imagen';
        }

        const modal = getInstance(modalEl);

        if (modal) {
            modal.show();
        }
    }

    function bind() {
        if (window.__imageViewerBound) {
            return;
        }

        window.__imageViewerBound = true;

        document.addEventListener('click', function (event) {
            const trigger = event.target.closest('[data-open-image], .js-abrir-imagen, .js-imagen-ampliar');

            if (!trigger) {
                return;
            }

            event.preventDefault();

            const src =
                trigger.getAttribute('data-src') ||
                trigger.getAttribute('data-imagen') ||
                (trigger.tagName === 'IMG' ? trigger.src : '');

            const title =
                trigger.getAttribute('data-title') ||
                trigger.getAttribute('data-nombre') ||
                'Imagen';

            open(src, title);
        });
    }

    window.ImageViewer = {
        open: open,
        bind: bind
    };

    window.abrirModalImagen = open;

    bind();
})();