/**
 * fetch_helper.js - Utilidad centralizada para fetch con CSRF + Logger + Notify
 * 
 * Reemplaza los fetch() duplicados en cada app.
 * Uso:
 *   FetchHelper.get('/api/tareas')
 *   FetchHelper.post('/api/tareas', { titulo: 'Nueva' })
 *   FetchHelper.put('/api/tareas/1', { titulo: 'Editada' })
 *   FetchHelper.delete('/api/tareas/1')
 */
(function () {
    'use strict';

    if (window.__fetchHelperInitialized) return;
    window.__fetchHelperInitialized = true;

    const _logger = window.Logger || {
        apiCall: function () {},
        apiResponse: function () {},
        error: function () {}
    };

    const _notify = window.Notify || {
        error: function (msg) { console.error(msg); }
    };

    async function _getToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        if (meta && meta.content) return meta.content;
        try {
            const res = await fetch('/api/csrf-token', { credentials: 'same-origin' });
            const data = await res.json();
            return data.csrf_token || '';
        } catch (e) {
            _logger.error('FetchHelper: no se pudo obtener token CSRF', e);
            return '';
        }
    }

    async function _request(method, url, data, options) {
        options = options || {};
        const showErrors = options.showErrors !== false;
        const successMsg = options.successMsg || null;

        _logger.apiCall(method, url);

        try {
            const headers = { ...options.headers };
            let body = undefined;

            if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
                const token = await _getToken();
                headers['X-CSRFToken'] = token;
            }

            if (data !== undefined && data !== null) {
                if (data instanceof FormData) {
                    body = data;
                    // No setear Content-Type para FormData
                } else {
                    headers['Content-Type'] = 'application/json';
                    body = JSON.stringify(data);
                }
            }

            const res = await fetch(url, {
                method: method,
                headers: headers,
                body: body,
                credentials: 'same-origin'
            });

            let json = null;
            const contentType = res.headers.get('content-type') || '';
            if (contentType.includes('application/json')) {
                json = await res.json();
            } else {
                json = await res.text();
            }

            _logger.apiResponse(method, url, res.status, json);

            if (!res.ok) {
                const msg = (json && json.msg) || (json && json.error) || ('HTTP ' + res.status);
                if (showErrors) _notify.error(msg);
                throw new Error(msg);
            }

            if (successMsg) _notify.success(successMsg);
            return json;

        } catch (err) {
            _logger.error('FetchHelper ' + method + ' ' + url, err);
            if (showErrors && !err._notified) {
                _notify.error(err.message || 'Error de conexión');
            }
            throw err;
        }
    }

    window.FetchHelper = {
        get: function (url, options) {
            return _request('GET', url, undefined, options);
        },
        post: function (url, data, options) {
            return _request('POST', url, data, options);
        },
        put: function (url, data, options) {
            return _request('PUT', url, data, options);
        },
        patch: function (url, data, options) {
            return _request('PATCH', url, data, options);
        },
        delete: function (url, options) {
            return _request('DELETE', url, undefined, options);
        },
        postForm: function (url, formData, options) {
            return _request('POST', url, formData, options);
        },
        putForm: function (url, formData, options) {
            return _request('PUT', url, formData, options);
        }
    };

    _logger.info('FetchHelper inicializado');
})();