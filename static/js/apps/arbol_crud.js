/**
* arbol_crud.js - VERSIÓN MEJORADA
* Módulo genérico y reutilizable para CRUD de árboles jerárquicos.
* 
* MEJORAS:
* - Usa Logger reutilizable (si está disponible)
* - Usa Noty para notificaciones (si está disponible, sino alert)
* - Usa SweetAlert2 para confirmaciones (si está disponible, sino confirm)
* - Mejora manejo de errores de API
* - Evita conflictos con múltiples instancias
*/
class ArbolCRUD {
    constructor(cfg) {
        const requeridos = ["apiArbol", "apiCrud", "claveHijos", "selectoresId", "tablaId"];
        for (const k of requeridos) {
            if (!cfg[k]) throw new Error(`ArbolCRUD: falta config.${k}`);
        }
        this.cfg = Object.assign({
            nombreItem: "item",
            campoRuta: "ruta",
            camposForm: { nombre: "nombre", emoji: "emoji", ruta: "ruta", original: "ruta_original" },
            botones: { agregar: ".btn-agregar", editar: ".btn-editar", cancelar: ".btn-cancelar" },
            mensajeExito: null,
            onInit: null,
            onRenderFila: null
        }, cfg);
        this.arbol = [];
        this.instanceId = `arbol_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        this.init();
    }

    // ========================================================
    // LOGGER (usa Logger global si existe, sino console)
    // ========================================================
    _log(level, msg, data = null) {
        if (typeof Logger !== 'undefined' && Logger[level]) {
            Logger[level](`[ArbolCRUD:${this.cfg.nombreItem}] ${msg}`, data);
        } else {
            const prefix = `[ArbolCRUD:${this.cfg.nombreItem}]`;
            if (level === 'error') console.error(prefix, msg, data || '');
            else if (level === 'warn') console.warn(prefix, msg, data || '');
            else console.log(prefix, msg, data || '');
        }
    }

    // ========================================================
    // NOTIFICACIONES (usa Noty si existe, sino alert)
    // ========================================================
    _notif(msg, tipo = 'success') {
        if (typeof Noty !== 'undefined') {
            new Noty({
                type: tipo,
                layout: 'topRight',
                timeout: 3000,
                theme: 'mint',
                text: msg
            }).show();
        } else {
            alert(msg);
        }
    }

    // ========================================================
    // CONFIRMACIONES (usa SweetAlert2 si existe, sino confirm)
    // ========================================================
    async _confirm(titulo, texto) {
        if (typeof Swal !== 'undefined') {
            const result = await Swal.fire({
                title: titulo,
                text: texto,
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#dc3545',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar'
            });
            return result.isConfirmed;
        }
        return confirm(texto);
    }

    // ========================================================
    // INICIALIZACIÓN
    // ========================================================
    async init() {
        this._log('info', 'Inicializando módulo');
        await this.cargarArbol();
        this.renderSelectoresNiveles();
        this.cargarTabla();
        this._bindBotones();
        if (this.cfg.onInit) this.cfg.onInit(this);
        this._log('success', 'Módulo inicializado correctamente');
    }

    // ========================================================
    // API: cargar árbol
    // ========================================================
    async cargarArbol() {
        try {
            this._log('info', `Cargando árbol desde ${this.cfg.apiArbol}`);
            const res = await fetch(this.cfg.apiArbol);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const contentType = res.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error('Respuesta no es JSON');
            }
            this.arbol = await res.json();
            this._log('success', `Árbol cargado`, { nodos: this.arbol.length });
        } catch (err) {
            this._log('error', 'Error cargando árbol', err);
            this.arbol = [];
            this._notif('Error al cargar los datos', 'error');
        }
        return this.arbol;
    }

    // ========================================================
    // API: crear / editar / eliminar
    // ========================================================
    async _apiCall(method, payload) {
        this._log('info', `API ${method} → ${this.cfg.apiCrud}`, payload);
        try {
            const res = await fetch(this.cfg.apiCrud, {
                method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const contentType = res.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error('Respuesta del servidor no es JSON');
            }
            const data = await res.json();
            this._log(res.ok ? 'success' : 'error', `API ${method} ← ${res.status}`, data);
            return data;
        } catch (err) {
            this._log('error', `Error en API ${method}`, err);
            throw err;
        }
    }

    async crear(payload) {
        return this._apiCall("POST", payload);
    }

    async editar(payload) {
        return this._apiCall("PUT", payload);
    }

    async eliminar(ruta) {
        return this._apiCall("DELETE", { ruta });
    }

    // ========================================================
    // UTILIDADES DE ÁRBOL
    // ========================================================
    buscarNodoPorRuta(ruta) {
        if (!ruta) return null;
        // Detectar separador según claveHijos
        let separador;
        if (ruta.includes("||")) {
            separador = "||";
        } else if (this.cfg.claveHijos === "submenues") {
            separador = ".";
        } else if (this.cfg.claveHijos === "sububicaciones") {
            separador = "-";
        } else {
            separador = ".";
        }
        const partes = ruta.split(separador);
        let actual = this.arbol;
        let encontrado = null;
        for (let i = 0; i < partes.length; i++) {
            const parte = partes[i];
            const nodo = (actual || []).find(n => n.nombre === parte);
            if (!nodo) return null;
            encontrado = nodo;
            actual = nodo[this.cfg.claveHijos] || [];
        }
        return encontrado;
    }

    obtenerRutaPadre() {
        const selects = document.querySelectorAll(`#${this.cfg.selectoresId} .nivel-select`);
        let ruta = "";
        selects.forEach(sel => {
            if (sel.value) ruta = sel.value;
        });
        return ruta;
    }

    // ========================================================
    // UI: renderizar selectores multinivel
    // ========================================================
    renderSelectoresNiveles(rutaPorDefecto = "") {
        const cont = document.getElementById(this.cfg.selectoresId);
        if (!cont) return;
        cont.innerHTML = "";
        if (!rutaPorDefecto) {
            cont.appendChild(this._crearSelect(this.arbol, 0));
            return;
        }
        let separador;
        if (rutaPorDefecto.includes("||")) {
            separador = "||";
        } else if (this.cfg.claveHijos === "submenues") {
            separador = ".";
        } else if (this.cfg.claveHijos === "sububicaciones") {
            separador = "-";
        } else {
            separador = ".";
        }
        const partes = rutaPorDefecto.split(separador);
        let actual = this.arbol;
        let rutaAcumulada = "";
        partes.forEach((parte, nivel) => {
            rutaAcumulada += (nivel > 0 ? separador : "") + parte;
            cont.appendChild(this._crearSelect(actual, nivel, rutaAcumulada));
            const nodo = (actual || []).find(n => n.nombre === parte);
            actual = nodo ? (nodo[this.cfg.claveHijos] || []) : [];
        });
    }

    _crearSelect(opciones, nivel, valorSeleccionado = "") {
        const select = document.createElement("select");
        select.className = "form-control nivel-select mb-2";
        select.setAttribute("data-nivel", nivel);
        select.innerHTML = `<option value="">Sin seleccionar</option>`;
        (opciones || []).forEach(item => {
            const selected = item.ruta_jerarquia === valorSeleccionado ? "selected" : "";
            select.innerHTML += `<option value="${item.ruta_jerarquia}" ${selected}>${item.emoji || ""} ${item.nombre}</option>`;
        });
        select.onchange = () => {
            let next = select.nextElementSibling;
            while (next) {
                next.remove();
                next = select.nextElementSibling;
            }
            if (select.value) {
                const seleccionado = this.buscarNodoPorRuta(select.value);
                const hijos = seleccionado ? (seleccionado[this.cfg.claveHijos] || []) : [];
                if (hijos.length > 0) {
                    select.parentElement.appendChild(this._crearSelect(hijos, nivel + 1));
                }
            }
        };
        return select;
    }

    // ========================================================
    // UI: renderizar tabla jerárquica
    // ========================================================
    cargarTabla() {
        const tabla = document.getElementById(this.cfg.tablaId);
        if (!tabla) return;
        tabla.innerHTML = "";
        this._renderNodos(this.arbol, tabla, 0);
    }

    _renderNodos(nodos, tabla, nivel) {
        (nodos || []).forEach(nodo => {
            const fila = this._construirFila(nodo, nivel);
            tabla.insertAdjacentHTML("beforeend", fila);
            const hijos = nodo[this.cfg.claveHijos] || [];
            if (hijos.length > 0) {
                this._renderNodos(hijos, tabla, nivel + 1);
            }
        });
    }

    _construirFila(nodo, nivel) {
        if (this.cfg.onRenderFila) {
            return this.cfg.onRenderFila(nodo, nivel, this);
        }
        const rutaAttr = this._escapeAttr(nodo.ruta_jerarquia);
        const nombreAttr = this._escapeAttr(nodo.nombre);
        const emojiAttr = this._escapeAttr(nodo.emoji || "");
        const rutaValorAttr = this._escapeAttr(nodo.ruta || "");
        return `
        <tr>
            <td>${nodo.emoji || ""}</td>
            <td class="nivel-${nivel}">${nodo.nombre}</td>
            <td>${nodo.ruta || ""}</td>
            <td>
                <button class="btn btn-sm btn-editar"
                    onclick="window.__arbolCRUD_editar_${this.instanceId}__.call(null,
                    '${rutaAttr}','${nombreAttr}','${emojiAttr}','${rutaValorAttr}')">
                    Editar
                </button>
                <button class="btn btn-sm btn-eliminar"
                    onclick="window.__arbolCRUD_eliminar_${this.instanceId}__.call(null, '${rutaAttr}')">
                    Eliminar
                </button>
            </td>
        </tr>
        `;
    }

    // ========================================================
    // UI: acciones de formulario
    // ========================================================
    _bindBotones() {
        const cfg = this.cfg.botones;
        // Usar instanceId para evitar conflictos
        window[`__arbolCRUD_editar_${this.instanceId}__`] = (ruta, nombre, emoji, rutaValor) => {
            this.prepararEdicion(ruta, nombre, emoji, rutaValor);
        };
        window[`__arbolCRUD_eliminar_${this.instanceId}__`] = (ruta) => {
            this.eliminarItem(ruta);
        };
        const btnEditar = document.querySelector(cfg.editar);
        if (btnEditar) btnEditar.onclick = () => this.guardarEdicion();
        const btnCancelar = document.querySelector(cfg.cancelar);
        if (btnCancelar) btnCancelar.onclick = () => this.cancelar();
    }

    async guardar() {
        const f = this.cfg.camposForm;
        const nombre = document.getElementById(f.nombre)?.value.trim();
        const emoji = document.getElementById(f.emoji)?.value.trim();
        const ruta = document.getElementById(f.ruta)?.value.trim();
        const ruta_padre = this.obtenerRutaPadre();

        if (!nombre || !emoji) {
            this._notif("Complete todos los campos obligatorios", 'warning');
            return;
        }

        const payload = { nombre, emoji, ruta, ruta_padre };
        payload[this.cfg.campoRuta] = ruta;

        try {
            const res = await this.crear(payload);
            if (res.type === 'success') {
                this._notif(res.msg || `${this.cfg.nombreItem} agregado correctamente`, 'success');
                await this.init();
                this.cancelar();
            } else {
                this._notif(res.msg || 'Error al agregar', res.type || 'error');
            }
        } catch (err) {
            this._log('error', 'Error al crear', err);
            this._notif('Error de conexión al guardar', 'error');
        }
    }

    async guardarEdicion() {
        const f = this.cfg.camposForm;
        const nombre = document.getElementById(f.nombre)?.value.trim();
        const emoji = document.getElementById(f.emoji)?.value.trim();
        const ruta = document.getElementById(f.ruta)?.value.trim();
        const ruta_original = document.getElementById(f.original)?.value;

        if (!nombre || !emoji || !ruta_original) {
            this._notif("Complete todos los campos", 'warning');
            return;
        }

        const payload = { nombre, emoji, ruta, ruta: ruta_original };
        payload[this.cfg.campoRuta] = ruta;

        try {
            const res = await this.editar(payload);
            if (res.type === 'success') {
                this._notif(res.msg || `${this.cfg.nombreItem} actualizado correctamente`, 'success');
                await this.init();
                this.cancelar();
            } else {
                this._notif(res.msg || 'Error al actualizar', res.type || 'error');
            }
        } catch (err) {
            this._log('error', 'Error al editar', err);
            this._notif('Error de conexión al editar', 'error');
        }
    }

    async eliminarItem(ruta) {
        const confirmado = await this._confirm(
            `¿Eliminar este ${this.cfg.nombreItem}?`,
            'Esta acción no se puede deshacer'
        );
        if (!confirmado) return;

        try {
            const res = await this.eliminar(ruta);
            if (res.type === 'success') {
                this._notif(res.msg || `${this.cfg.nombreItem} eliminado correctamente`, 'success');
                await this.init();
                this.cancelar();
            } else {
                this._notif(res.msg || 'Error al eliminar', res.type || 'error');
            }
        } catch (err) {
            this._log('error', 'Error al eliminar', err);
            this._notif('Error de conexión al eliminar', 'error');
        }
    }

    prepararEdicion(ruta_jerarquia, nombre, emoji, ruta_valor) {
        const f = this.cfg.camposForm;
        const b = this.cfg.botones;
        document.getElementById(f.nombre).value = nombre;
        document.getElementById(f.emoji).value = emoji;
        document.getElementById(f.ruta).value = ruta_valor || "";
        document.getElementById(f.original).value = ruta_jerarquia;

        const btnAgregar = document.querySelector(b.agregar);
        const btnEditar = document.querySelector(b.editar);
        const btnCancelar = document.querySelector(b.cancelar);
        if (btnAgregar) btnAgregar.style.display = "none";
        if (btnEditar) btnEditar.classList.add("active");
        if (btnCancelar) btnCancelar.classList.add("active");

        let separador;
        if (ruta_jerarquia.includes("||")) {
            separador = "||";
        } else if (this.cfg.claveHijos === "submenues") {
            separador = ".";
        } else if (this.cfg.claveHijos === "sububicaciones") {
            separador = "-";
        } else {
            separador = ".";
        }
        const partes = ruta_jerarquia.split(separador);
        partes.pop();
        const rutaPadre = partes.join(separador);
        this.renderSelectoresNiveles(rutaPadre);
    }

    cancelar() {
        const f = this.cfg.camposForm;
        const b = this.cfg.botones;
        document.getElementById(f.nombre).value = "";
        document.getElementById(f.emoji).value = "";
        document.getElementById(f.ruta).value = "";
        document.getElementById(f.original).value = "";

        const btnAgregar = document.querySelector(b.agregar);
        const btnEditar = document.querySelector(b.editar);
        const btnCancelar = document.querySelector(b.cancelar);
        if (btnAgregar) btnAgregar.style.display = "inline";
        if (btnEditar) btnEditar.classList.remove("active");
        if (btnCancelar) btnCancelar.classList.remove("active");

        this.renderSelectoresNiveles();
    }

    _escapeAttr(s) {
        return String(s || "").replace(/'/g, "\\'").replace(/"/g, "&quot;");
    }
}

window.ArbolCRUD = ArbolCRUD;