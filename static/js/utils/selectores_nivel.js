/**
 * selectores_nivel.js - Módulo reutilizable
 * Lógica de selectores multinivel para árboles jerárquicos.
 * Usado por: Pagos, Crear Rubros, Crear Almacenes, etc.
 */

class SelectoresNivel {
    constructor(config = {}) {
        this.config = Object.assign({
            containerId: 'nivelesContainer',
            apiUrl: '/api/rubro_arbol',  // URL de la API del árbol
            separador: '.',
            loggerPrefix: '[SelectoresNivel]',
            onLoaded: null
        }, config);
        
        this.arbol = [];
        this.container = document.getElementById(this.config.containerId);
        
        if (!this.container) {
            console.error(`${this.config.loggerPrefix} Contenedor ${this.config.containerId} no encontrado`);
            return;
        }
        
        this.init();
    }

    async init() {
        await this.cargarArbol();
        this.renderSelectores();
        if (this.config.onLoaded) this.config.onLoaded(this.arbol);
    }

    async cargarArbol() {
        try {
            Logger.apiCall('GET', this.config.apiUrl);
            const res = await fetch(this.config.apiUrl, { credentials: 'include' });
            Logger.apiResponse('GET', this.config.apiUrl, res.status);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            this.arbol = await res.json();
            Logger.info(`${this.config.loggerPrefix} Árbol cargado`, { nodos: this.arbol.length });
        } catch (err) {
            Logger.error(`${this.config.loggerPrefix} Error cargando árbol`, err);
            this.arbol = [];
        }
    }

    renderSelectores(rutaPorDefecto = '') {
        if (!this.container) return;
        this.container.innerHTML = '';
        
        if (!rutaPorDefecto) {
            this.container.appendChild(this.crearSelect(this.arbol, 0));
            return;
        }

        const partes = rutaPorDefecto.split(this.config.separador);
        let actual = this.arbol;
        let rutaAcumulada = '';

        partes.forEach((parte, nivel) => {
            rutaAcumulada += (nivel > 0 ? this.config.separador : '') + parte;
            this.container.appendChild(this.crearSelect(actual, nivel, rutaAcumulada));
            const nodo = (actual || []).find(n => n.nombre === parte);
            actual = nodo ? (nodo.submenues || []) : [];
        });
    }

    crearSelect(opciones, nivel, valorSeleccionado = '') {
        const select = document.createElement('select');
        select.className = 'form-control nivel-select mb-2';
        select.setAttribute('data-nivel', nivel);
        
        let html = '<option value="">Sin seleccionar</option>';
        (opciones || []).forEach(item => {
            const sel = item.ruta_jerarquia === valorSeleccionado ? ' selected' : '';
            html += `<option value="${item.ruta_jerarquia}" ${sel}>${item.emoji || ''} ${item.nombre}</option>`;
        });
        select.innerHTML = html;

        select.addEventListener('change', () => {
            // Eliminar selects siguientes
            let next = select.nextElementSibling;
            while (next) {
                const tmp = next.nextElementSibling;
                next.remove();
                next = tmp;
            }

            // Crear siguiente nivel si hay hijos
            if (select.value) {
                const nodo = this.buscarNodoPorRuta(select.value);
                const hijos = nodo ? (nodo.submenues || []) : [];
                if (hijos.length > 0) {
                    select.parentElement.appendChild(this.crearSelect(hijos, nivel + 1));
                }
            }
        });

        return select;
    }

    buscarNodoPorRuta(ruta) {
        if (!ruta) return null;
        const partes = ruta.split(this.config.separador);
        let actual = this.arbol;
        let encontrado = null;

        for (const parte of partes) {
            const nodo = (actual || []).find(n => n.nombre === parte);
            if (!nodo) return null;
            encontrado = nodo;
            actual = nodo.submenues || [];
        }
        return encontrado;
    }

    obtenerRutaPadre() {
        const selects = this.container.querySelectorAll('.nivel-select');
        let ruta = '';
        selects.forEach(sel => {
            if (sel.value) ruta = sel.value;
        });
        return ruta;
    }
}

window.SelectoresNivel = SelectoresNivel;