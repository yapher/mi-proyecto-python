/**
 * notifications.js - Sistema unificado de notificaciones y mensajes
 * Compatible con Noty y SweetAlert2
 * Uso:
 *   Notify.success('Operación exitosa');
 *   Notify.error('Error al guardar');
 *   Notify.confirm('¿Estás seguro?', () => { ... });
 *   Notify.alert('Información importante', 'warning');
 */

class Notify {
    // ============================================================
    // CONFIGURACIÓN POR DEFECTO
    // ============================================================
    static defaults = {
        // Noty
        noty: {
            layout: 'topRight',
            timeout: 3000,
            theme: 'mint',
            progressBar: true
        },
        // SweetAlert2
        sweet: {
            confirmButtonColor: '#88c999',
            cancelButtonColor: '#dc3545',
            background: '#4b376a',
            color: '#fff',
            customClass: {
                popup: 'swal-custom-popup',
                title: 'swal-custom-title',
                confirmButton: 'swal-custom-confirm-button'
            }
        }
    };

    // ============================================================
    // NOTIFICACIONES RÁPIDAS (Noty)
    // ============================================================
    
    /**
     * Muestra una notificación de éxito
     * @param {string} msg - Mensaje a mostrar
     * @param {number} timeout - Duración en ms (default: 3000)
     */
    static success(msg, timeout = 3000) {
        if (typeof Noty !== 'undefined') {
            new Noty({
                type: 'success',
                text: msg,
                timeout: timeout,
                ...this.defaults.noty
            }).show();
        } else {
            console.log('✅', msg);
        }
    }

    /**
     * Muestra una notificación de error
     * @param {string} msg - Mensaje a mostrar
     * @param {number} timeout - Duración en ms (default: 4000)
     */
    static error(msg, timeout = 4000) {
        if (typeof Noty !== 'undefined') {
            new Noty({
                type: 'error',
                text: msg,
                timeout: timeout,
                ...this.defaults.noty
            }).show();
        } else {
            console.error('❌', msg);
        }
    }

    /**
     * Muestra una notificación de advertencia
     * @param {string} msg - Mensaje a mostrar
     * @param {number} timeout - Duración en ms (default: 3500)
     */
    static warning(msg, timeout = 3500) {
        if (typeof Noty !== 'undefined') {
            new Noty({
                type: 'warning',
                text: msg,
                timeout: timeout,
                ...this.defaults.noty
            }).show();
        } else {
            console.warn('⚠️', msg);
        }
    }

    /**
     * Muestra una notificación de información
     * @param {string} msg - Mensaje a mostrar
     * @param {number} timeout - Duración en ms (default: 3000)
     */
    static info(msg, timeout = 3000) {
        if (typeof Noty !== 'undefined') {
            new Noty({
                type: 'info',
                text: msg,
                timeout: timeout,
                ...this.defaults.noty
            }).show();
        } else {
            console.info('ℹ️', msg);
        }
    }

    /**
     * Muestra una notificación genérica
     * @param {string} msg - Mensaje a mostrar
     * @param {string} type - Tipo: 'success', 'error', 'warning', 'info'
     * @param {number} timeout - Duración en ms
     */
    static alert(msg, type = 'info', timeout = 3000) {
        switch (type) {
            case 'success': this.success(msg, timeout); break;
            case 'error': this.error(msg, timeout); break;
            case 'warning': this.warning(msg, timeout); break;
            default: this.info(msg, timeout);
        }
    }

    // ============================================================
    // DIÁLOGOS MODALES (SweetAlert2)
    // ============================================================

    /**
     * Muestra un diálogo de confirmación
     * @param {string} title - Título del diálogo
     * @param {string} text - Texto descriptivo
     * @param {function} onConfirm - Callback si se confirma
     * @param {function} onCancel - Callback si se cancela (opcional)
     */
    static confirm(title, text, onConfirm, onCancel = null) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: title,
                text: text,
                icon: 'warning',
                showCancelButton: true,
                ...this.defaults.sweet,
                confirmButtonText: 'Sí, confirmar',
                cancelButtonText: 'Cancelar'
            }).then(result => {
                if (result.isConfirmed && onConfirm) {
                    onConfirm();
                } else if (!result.isConfirmed && onCancel) {
                    onCancel();
                }
            });
        } else {
            if (confirm(text)) {
                if (onConfirm) onConfirm();
            } else {
                if (onCancel) onCancel();
            }
        }
    }

    /**
     * Muestra un diálogo de eliminación con confirmación
     * @param {string} itemName - Nombre del item a eliminar
     * @param {function} onConfirm - Callback si se confirma
     */
    static delete(itemName, onConfirm) {
        this.confirm(
            `¿Eliminar ${itemName}?`,
            'Esta acción no se puede deshacer',
            onConfirm
        );
    }

    /**
     * Muestra un mensaje de éxito modal
     * @param {string} title - Título
     * @param {string} text - Texto (opcional)
     * @param {number} timer - Duración en ms (default: 2000)
     */
    static successModal(title, text = '', timer = 2000) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'success',
                title: title,
                text: text,
                timer: timer,
                showConfirmButton: false,
                ...this.defaults.sweet
            });
        } else {
            alert(title);
        }
    }

    /**
     * Muestra un mensaje de error modal
     * @param {string} title - Título
     * @param {string} text - Texto (opcional)
     */
    static errorModal(title, text = '') {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'error',
                title: title,
                text: text,
                ...this.defaults.sweet,
                confirmButtonText: 'Entendido'
            });
        } else {
            alert(title);
        }
    }

    /**
     * Muestra un mensaje de información modal
     * @param {string} title - Título
     * @param {string} text - Texto (opcional)
     */
    static infoModal(title, text = '') {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: 'info',
                title: title,
                text: text,
                ...this.defaults.sweet,
                confirmButtonText: 'Entendido'
            });
        } else {
            alert(title);
        }
    }

    /**
     * Muestra un diálogo de entrada de texto
     * @param {string} title - Título
     * @param {string} inputType - Tipo de input: 'text', 'email', 'number', etc.
     * @param {function} onConfirm - Callback con el valor ingresado
     */
    static prompt(title, inputType, onConfirm) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: title,
                input: inputType,
                inputPlaceholder: 'Ingrese el valor',
                showCancelButton: true,
                ...this.defaults.sweet,
                confirmButtonText: 'Aceptar',
                cancelButtonText: 'Cancelar'
            }).then(result => {
                if (result.isConfirmed && result.value && onConfirm) {
                    onConfirm(result.value);
                }
            });
        } else {
            const value = prompt(title);
            if (value && onConfirm) {
                onConfirm(value);
            }
        }
    }

    /**
     * Muestra un diálogo con opciones personalizadas
     * @param {object} options - Objeto con configuración completa de SweetAlert2
     * @returns {Promise} - Promise con el resultado
     */
    static custom(options) {
        if (typeof Swal !== 'undefined') {
            return Swal.fire({
                ...this.defaults.sweet,
                ...options
            });
        } else {
            return Promise.resolve({ isConfirmed: false });
        }
    }
}

// ============================================================
// ALIAS PARA COMPATIBILIDAD
// ============================================================
window.Notify = Notify;

// Alias para uso más corto
window.showSuccess = (msg, timeout) => Notify.success(msg, timeout);
window.showError = (msg, timeout) => Notify.error(msg, timeout);
window.showWarning = (msg, timeout) => Notify.warning(msg, timeout);
window.showInfo = (msg, timeout) => Notify.info(msg, timeout);
window.showConfirm = (title, text, onConfirm, onCancel) => 
    Notify.confirm(title, text, onConfirm, onCancel);