/**
 * flash_messages.js
 * Procesa mensajes flash de Flask sin usar <script> inline.
 */
(function () {
    'use strict';

    if (window.__flashMessagesInitialized) return;
    window.__flashMessagesInitialized = true;

    document.addEventListener('DOMContentLoaded', function () {
        const container = document.getElementById('flash-messages-data');
        if (!container) return;

        try {
            const raw = container.getAttribute('data-messages');
            if (!raw) return;

            const messages = JSON.parse(raw);
            if (!Array.isArray(messages)) return;

            messages.forEach(function (message) {
                if (!Array.isArray(message) || message.length < 2) return;

                const category = message[0] || 'info';
                const text = message[1] || '';

                if (typeof Notify !== 'undefined') {
                    let type = 'info';

                    switch (category) {
                        case 'success':
                            type = 'success';
                            break;
                        case 'danger':
                        case 'error':
                            type = 'error';
                            break;
                        case 'warning':
                            type = 'warning';
                            break;
                        default:
                            type = 'info';
                    }

                    Notify.alert(text, type, 3500);
                } else {
                    console.log(`[${category}] ${text}`);
                }
            });

            container.remove();
        } catch (error) {
            console.error('Error procesando flash messages:', error);
        }
    });
})();