// static/js/utils/modal.js
(function () {
    'use strict';

    if (window.__appModalInitialized) {
        return;
    }

    window.__appModalInitialized = true;

    const Logger = window.Logger || {
        error: function () {},
        success: function () {},
        apiCall: function () {},
        apiResponse: function () {}
    };

    const Notify = window.Notify || {
        error: function (msg) {
            window.alert(msg || 'Error');
        }
    };

    function escapeHtml(value) {
        return String(value || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function getInstance(element, showError) {
        if (!element) {
            return null;
        }

        if (!window.bootstrap || !window.bootstrap.Modal) {
            Logger.error('Bootstrap no está disponible para abrir modales.');

            if (showError) {
                Notify.error('Bootstrap no está disponible.');
            }

            return null;
        }

        let instance = window.bootstrap.Modal.getInstance(element);

        if (!instance) {
            instance = new window.bootstrap.Modal(element);
        }

        return instance;
    }

    async function showFetch(options) {
        options = options || {};

        const modalId = options.modalId;
        const contentId = options.contentId;
        const url = options.url;
        const loadingMessage = options.loadingMessage || 'Cargando...';
        const errorMessage = options.errorMessage || 'Error al cargar el contenido.';
        const afterRender = options.afterRender;

        const contenido = document.getElementById(contentId);
        const modalEl = document.getElementById(modalId);

        if (!contenido) {
            Logger.error('AppModal.showFetch: no se encontró #' + contentId);
            Notify.error('No se encontró el contenido del modal.');
            return false;
        }

        if (!modalEl) {
            Logger.error('AppModal.showFetch: no se encontró #' + modalId);
            Notify.error('No se encontró el modal.');
            return false;
        }

        const safeLoading = escapeHtml(loadingMessage);

        contenido.innerHTML =
            '<div class="modal-body text-center py-5">' +
                '<div class="spinner-border text-primary" role="status"></div>' +
                '<p class="mt-3 text-white">' + safeLoading + '</p>' +
            '</div>';

        const modal = getInstance(modalEl, true);

        if (!modal) {
            return false;
        }

        try {
            modal.show();
        } catch (err) {
            Logger.error('AppModal.showFetch: modal.show() falló', err);
            Notify.error('No se pudo abrir el modal.');
            return false;
        }

        try {
            Logger.apiCall('GET', url);

            const res = await fetch(url, {
                credentials: 'same-origin'
            });

            Logger.apiResponse('GET', url, res.status);

            if (!res.ok) {
                throw new Error('HTTP ' + res.status);
            }

            const html = await res.text();
            contenido.innerHTML = html;

            if (typeof afterRender === 'function') {
                afterRender(contenido);
            }

            Logger.success('AppModal.showFetch: contenido cargado', { url: url });
            return true;
        } catch (err) {
            Logger.error('AppModal.showFetch: error cargando contenido', err);

            const safeError = escapeHtml(err && err.message ? err.message : err);

            contenido.innerHTML =
                '<div class="modal-body text-center py-5">' +
                    '<i class="bi bi-exclamation-triangle" style="font-size: 3rem; color: #dc3545;"></i>' +
                    '<p class="mt-3 text-danger">' + escapeHtml(errorMessage) + '</p>' +
                    '<p class="text-white-50 small">' + safeError + '</p>' +
                    '<button class="btn btn-cancelar" data-bs-dismiss="modal">Cerrar</button>' +
                '</div>';

            Notify.error(errorMessage);
            return false;
        }
    }

    window.AppModal = {
        getInstance: getInstance,
        showFetch: showFetch,
        escapeHtml: escapeHtml
    };
})();