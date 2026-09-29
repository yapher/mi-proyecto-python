/**
 * flash_messages.js - Procesa mensajes flash de Flask sin inline scripts
 * Lee el contenedor #flashMessages y muestra notificaciones con Notify
 */
(function () {
    'use strict';

    if (window.__flashMessagesInitialized) return;
    window.__flashMessagesInitialized = true;

    document.addEventListener('DOMContentLoaded', function () {
        const container = document.getElementById('flashMessages');
        if (!container) return;

        try {
            const raw = container.getAttribute('data-messages');
            if (!raw) return;

            const messages = JSON.parse(raw);
            if (!Array.isArray(messages)) return;

            messages.forEach(function (msg) {
                if (!Array.isArray(msg) || msg.length < 2) return;
                const category = msg[0] || 'info';
                const text = msg[1] || '';

                if (typeof Notify !== 'undefined') {
                    let type = 'info';
                    switch (category) {
                        case 'success': type = 'success'; break;
                        case 'danger':
                        case 'error': type = 'error'; break;
                        case 'warning': type = 'warning'; break;
                        default: type = 'info';
                    }
                    Notify.alert(text, type, 4000);
                } else {
                    console.log('[' + category + '] ' + text);
                }
            });

            // Limpiar el contenedor
            container.remove();

        } catch (e) {
            console.error('Error procesando flash messages:', e);
        }
    });
})();