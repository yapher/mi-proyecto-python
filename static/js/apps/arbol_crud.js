/**
 * arbol_crud.js
 * =============
 * Módulo genérico y reutilizable para CRUD de árboles jerárquicos.
 * Reemplaza la lógica duplicada en:
 *   - crear_almacenes.js
 *   - crear_ubicacion_tecnica.js
 *   - crear_procedimiento.js
 *   - gestion_menu.js
 *
 * Uso:
 *   document.addEventListener("DOMContentLoaded", () => {
 *       new ArbolCRUD({
 *           apiArbol:     '/api/crear_almacenes_arbol',
 *           apiCrud:      '/api/crear_almacenes',
 *           claveHijos:   'subcrear_almacenes',
 *           campoRuta:    'ruta_crear_almacenes',
 *           nombreItem:   'almacén',
 *           selectoresId: 'nivelesContainer',
 *           tablaId:      'tabla',
 *           camposForm:   {
 *               nombre:    'nombre',
 *               emoji:     'emoji',
 *               ruta:      'ruta_crear_almaceneses',
 *               original:  'ruta_original'
 *           },
 *           botones: {
 *               agregar:  '.btn-agregar',
 *               editar:   '.btn-editar',
 *               cancelar: '.btn-cancelar'
 *           }
 *       });
 *   });
 */

class ArbolCRUD {
    /**
     * @param {Object} cfg - Configuración del árbol
     */
    constructor(cfg) {
        // Validación mínima
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
            onInit: null,       // callback tras inicializar
            onRenderFila: null  // callback para personalizar HTML de cada fila
        }, cfg);

        this.arbol = [];
        this.init();
    }

    // ========================================================
    // INIALIZACIÓN
    // ========================================================
    async init() {
        await this.cargarArbol();
        this.renderSelectoresNiveles();
        this.cargarTabla();
        this._bindBotones();
        if (this.cfg.onInit) this.cfg.onInit(this);
    }

    // ========================================================
    // API: cargar árbol
    // ========================================================
    async cargarArbol() {
        try {
            const res = await fetch(this.cfg.apiArbol);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            this.arbol = await res.json();
        } catch (err) {
            console.error(`[ArbolCRUD] Error cargando árbol:`, err);
            this.arbol = [];
        }
        return this.arbol;
    }

    // ========================================================
    // API: crear / editar / eliminar
    // ========================================================
    async _apiCall(method, payload) {
        const res = await fetch(this.cfg.apiCrud, {
            method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        return res.json();
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
        const partes = ruta.includes("||") ? ruta.split("||") : ruta.split(/[.\-]/);
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

        // Expandir jerarquía hasta la ruta por defecto
        const partes = rutaPorDefecto.includes("||")
            ? rutaPorDefecto.split("||")
            : rutaPorDefecto.split(/[.\-]/);
        let actual = this.arbol;
        let rutaAcumulada = "";

        partes.forEach((parte, nivel) => {
            const sep = this.cfg.claveHijos === "submenues" ? "." :
                        this.cfg.claveHijos === "sububicaciones" ? "-" : ".";
            rutaAcumulada += (nivel > 0 ? sep : "") + parte;
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
            // Limpiar niveles hijos
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
        // Permitir personalizar la fila desde fuera
        if (this.cfg.onRenderFila) {
            return this.cfg.onRenderFila(nodo, nivel, this);
        }

        // Implementación por defecto
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
                        onclick="window.__arbolCRUD_editar__.call(null,
                            '${rutaAttr}','${nombreAttr}','${emojiAttr}','${rutaValorAttr}')">
                        Editar
                    </button>
                    <button class="btn btn-sm btn-eliminar"
                        onclick="window.__arbolCRUD_eliminar__.call(null, '${rutaAttr}')">
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

        // Exponer métodos globales para los onclick de la tabla
        window.__arbolCRUD_editar__ = (ruta, nombre, emoji, rutaValor) => {
            this.prepararEdicion(ruta, nombre, emoji, rutaValor);
        };
        window.__arbolCRUD_eliminar__ = (ruta) => {
            this.eliminarItem(ruta);
        };

        // Botón editar (guardar cambios)
        const btnEditar = document.querySelector(cfg.editar);
        if (btnEditar) btnEditar.onclick = () => this.guardarEdicion();

        // Botón cancelar
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
            alert("Complete todos los campos obligatorios");
            return;
        }

        const payload = { nombre, emoji, ruta, ruta_padre };
        payload[this.cfg.campoRuta] = ruta;

        const res = await this.crear(payload);
        alert(res.msg || "Creado");
        await this.init();
        this.cancelar();
    }

    async guardarEdicion() {
        const f = this.cfg.camposForm;
        const nombre = document.getElementById(f.nombre)?.value.trim();
        const emoji = document.getElementById(f.emoji)?.value.trim();
        const ruta = document.getElementById(f.ruta)?.value.trim();
        const ruta_original = document.getElementById(f.original)?.value;

        if (!nombre || !emoji || !ruta_original) {
            alert("Complete todos los campos");
            return;
        }

        const payload = { nombre, emoji, ruta, ruta: ruta_original };
        payload[this.cfg.campoRuta] = ruta;

        const res = await this.editar(payload);
        alert(res.msg || "Actualizado");
        await this.init();
        this.cancelar();
    }

    async eliminarItem(ruta) {
        if (!confirm(`¿Eliminar este ${this.cfg.nombreItem}?`)) return;
        const res = await this.eliminar(ruta);
        alert(res.msg || "Eliminado");
        await this.init();
        this.cancelar();
    }

    prepararEdicion(ruta_jerarquia, nombre, emoji, ruta_valor) {
        const f = this.cfg.camposForm;
        const b = this.cfg.botones;

        document.getElementById(f.nombre).value = nombre;
        document.getElementById(f.emoji).value = emoji;
        document.getElementById(f.ruta).value = ruta_valor || "";
        document.getElementById(f.original).value = ruta_jerarquia;

        // Toggle botones
        const btnAgregar = document.querySelector(b.agregar);
        const btnEditar = document.querySelector(b.editar);
        const btnCancelar = document.querySelector(b.cancelar);

        if (btnAgregar) btnAgregar.style.display = "none";
        if (btnEditar) btnEditar.classList.add("active");
        if (btnCancelar) btnCancelar.classList.add("active");

        // Renderizar selectores con la ruta padre
        const partes = ruta_jerarquia.includes("||")
            ? ruta_jerarquia.split("||")
            : ruta_jerarquia.split(/[.\-]/);
        partes.pop();
        const rutaPadre = partes.join(
            this.cfg.claveHijos === "submenues" ? "." :
            this.cfg.claveHijos === "sububicaciones" ? "-" : "."
        );
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

    // ========================================================
    // HELPERS
    // ========================================================
    _escapeAttr(s) {
        return String(s || "").replace(/'/g, "\\'").replace(/"/g, "&quot;");
    }
}

// Exponer globalmente
window.ArbolCRUD = ArbolCRUD;