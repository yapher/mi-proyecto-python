/**
 * csrf.js - Utilidades CSRF reutilizables
 * Proporciona funciones helper para manejar tokens CSRF en requests AJAX.
 * Uso:
 *   CSRF.post('/api/usuarios', { username, password, roles })
 *   CSRF.put('/api/usuarios/123', { username: 'nuevo' })
 *   CSRF.delete('/api/usuarios/123')
 */
const CSRF = {
    /**
     * Obtiene el token CSRF del meta tag o lo genera vía API.
     */
    async getToken() {
        const metaToken = document.querySelector('meta[name="csrf-token"]')?.content;
        if (metaToken) return metaToken;

        try {
            const response = await fetch('/api/csrf-token', {
                credentials: 'same-origin'
            });
            const data = await response.json();
            return data.csrf_token;
        } catch (error) {
            console.error('Error obteniendo token CSRF:', error);
            return '';
        }
    },

    /**
     * Realiza un fetch con protección CSRF automática.
     */
    async fetch(url, options = {}) {
        const token = await this.getToken();

        const headers = {
            ...options.headers,
            'X-CSRFToken': token
        };

        if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
            headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(options.body);
        }

        return fetch(url, {
            ...options,
            headers,
            credentials: 'same-origin'
        });
    },

    async post(url, data) {
        return this.fetch(url, {
            method: 'POST',
            body: data
        });
    },

    async put(url, data) {
        return this.fetch(url, {
            method: 'PUT',
            body: data
        });
    },

    async delete(url) {
        return this.fetch(url, {
            method: 'DELETE'
        });
    },

    async patch(url, data) {
        return this.fetch(url, {
            method: 'PATCH',
            body: data
        });
    }
};

window.CSRF = CSRF;