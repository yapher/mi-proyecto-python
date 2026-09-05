// static/js/utils/event_modal.js
/**
 * EventModal - Componente reutilizable para modales de eventos
 * ✅ NOTIFICACIONES UNIFICADAS: usa Notify global
 */
class EventModal {
    constructor(config = {}) {
        this.config = Object.assign({
            modalId: null, formId: null,
            onGuardar: null, onEliminar: null, onGuardado: null
        }, config);
        this.el = document.getElementById(this.config.modalId);
        if (!this.el) return;
        this.modal = new bootstrap.Modal(this.el);
        this.eventoActual = null;
        this._bind();
    }

    abrirNuevo(fecha = '') {
        this.eventoActual = null;
        this._limpiar();
        if (fecha) {
            const f = this.el.querySelector('#eventoFecha');
            if (f) f.value = fecha;
        }
        this.el.querySelector('.modal-title').textContent = 'Nuevo Evento';
        this._toggleEliminar(false);
        this.modal.show();
    }

    abrirEditar(evento) {
        this.eventoActual = evento;
        this._setVal('eventoId', evento.id || '');
        this._setVal('eventoTitulo', evento.titulo || '');
        this._setVal('eventoFecha', evento.fecha || '');
        this._setVal('eventoDescripcion', evento.descripcion || '');
        this._setVal('eventoEmail', evento.email || '');
        this._setVal('eventoPrioridad', evento.prioridad || 'media');
        const chk = this.el.querySelector('#eventoRealizado');
        if (chk) chk.checked = !!evento.realizado;
        this.el.querySelector('.modal-title').textContent = 'Editar Evento';
        this._toggleEliminar(true);
        this.modal.show();
    }

    cerrar() { this.modal.hide(); }

    _bind() {
        this.el.querySelector('[data-action="guardar"]').addEventListener('click', () => this._guardar());
        this.el.querySelector('[data-action="eliminar"]').addEventListener('click', () => this._eliminar());
    }

    _limpiar() {
        this.el.querySelectorAll('input, textarea, select').forEach(i => {
            if (i.type === 'checkbox') i.checked = false;
            else if (i.tagName === 'SELECT') i.selectedIndex = 0;
            else i.value = '';
        });
    }

    _setVal(id, val) {
        const el = this.el.querySelector(`#${id}`);
        if (el) el.value = val || '';
    }

    _getVal(id) {
        const el = this.el.querySelector(`#${id}`);
        return el ? el.value.trim() : '';
    }

    _toggleEliminar(show) {
        const btn = this.el.querySelector('[data-action="eliminar"]');
        if (btn) btn.style.display = show ? 'inline-block' : 'none';
    }

    async _guardar() {
        const data = {
            id: this.eventoActual?.id || null,
            titulo: this._getVal('eventoTitulo'),
            fecha: this._getVal('eventoFecha'),
            descripcion: this._getVal('eventoDescripcion'),
            email: this._getVal('eventoEmail'),
            prioridad: this._getVal('eventoPrioridad') || 'media',
            realizado: this.el.querySelector('#eventoRealizado').checked
        };
        if (!data.titulo || !data.fecha) {
            // ✅ UNIFICADO: usa Notify en lugar de Noty directo
            this._notif('Título y fecha son requeridos', 'warning');
            return;
        }
        try {
            if (this.config.onGuardar) await this.config.onGuardar(data);
            this._notif('Evento guardado', 'success');
            this.cerrar();
            if (this.config.onGuardado) this.config.onGuardado();
        } catch (e) {
            this._notif('Error al guardar', 'error');
        }
    }

    async _eliminar() {
        if (!this.eventoActual?.id) return;
        if (!confirm('¿Eliminar este evento?')) return;
        try {
            if (this.config.onEliminar) await this.config.onEliminar(this.eventoActual.id);
            this._notif('Evento eliminado', 'success');
            this.cerrar();
        } catch (e) {
            this._notif('Error al eliminar', 'error');
        }
    }

    // ✅ UNIFICADO: usa Notify global en lugar de Noty directo
    _notif(msg, tipo) {
        Notify.alert(msg, tipo);
    }
}

window.EventModal = EventModal;