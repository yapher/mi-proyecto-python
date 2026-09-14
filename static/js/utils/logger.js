/**
 * Logger - Sistema de logs profesional y reutilizable
 * Uso:
 *   Logger.info('Mensaje', { datos });
 *   Logger.success('Operación exitosa');
 *   Logger.error('Error', error);
 */
class Logger {
    static #currentPrefix = '[App]';
    static #colors = {
        info: '#3498db', success: '#2ecc71',
        warn: '#f39c12', error: '#e74c3c', debug: '#9b59b6'
    };
    static #icons = {
        info: 'ℹ️', success: '✅', warn: '⚠️',
        error: '❌', debug: '🔍'
    };

    static setPrefix(prefix) { Logger.#currentPrefix = prefix; }

    static #getTimestamp() {
        const now = new Date();
        return now.toLocaleTimeString('es-AR', { hour12: false }) +
               '.' + String(now.getMilliseconds()).padStart(3, '0');
    }

    static #log(level, message, data = null) {
        const header = `${Logger.#icons[level]} [${Logger.#getTimestamp()}] ${Logger.#currentPrefix} ${message}`;
        const style = `color: ${Logger.#colors[level]}; font-weight: bold;`;
        switch (level) {
            case 'error': console.error(`%c${header}`, style, data || ''); break;
            case 'warn':  console.warn(`%c${header}`, style, data || ''); break;
            case 'debug':
                if (localStorage.getItem('DEBUG_MODE') === 'true')
                    console.debug(`%c${header}`, style, data || '');
                break;
            default: console.log(`%c${header}`, style, data !== null ? data : '');
        }
    }

    static info(msg, data = null)    { Logger.#log('info', msg, data); }
    static success(msg, data = null) { Logger.#log('success', msg, data); }
    static warn(msg, data = null)    { Logger.#log('warn', msg, data); }
    static error(msg, err = null)    { Logger.#log('error', msg, err); }
    static debug(msg, data = null)   { Logger.#log('debug', msg, data); }

    static moduleInit(name) {
        Logger.setPrefix(`[${name}]`);
        Logger.info('Módulo inicializado correctamente');
    }

    static apiCall(method, url) { Logger.info(`API ${method} → ${url}`); }
    static apiResponse(method, url, status, data = null) {
        const level = status >= 200 && status < 300 ? 'success' : 'error';
        Logger[level](`API ${method} ← ${url} [${status}]`, data);
    }
}
window.Logger = Logger;