/**
 * JavaScript para el componente Instalaciones
 * Usa Logger e ImageUploader reutilizables
 * ✅ NOTIFICACIONES UNIFICADAS: usa Notify global (static/js/utils/notifications.js)
 */
let ubicacionTecnicaData = null;
let imageUploader = null;
const STATIC_INSTALACIONES = '/instalaciones/static/';
const DEFAULT_IMAGE = STATIC_INSTALACIONES + 'img/factory.png';

document.addEventListener("DOMContentLoaded", async () => {
    Logger.moduleInit('Instalaciones');

    const container = document.getElementById("tree-container");
    if (!container) {
        Logger.error('Contenedor tree-container no encontrado');
        return;
    }

    await cargarDatos();

    const root = document.createElement('ul');
    root.style.position = 'relative';
    root.classList.add('ul-flex');
    ubicacionTecnicaData.forEach(nodo => root.appendChild(crearNodo(nodo)));
    container.appendChild(root);

    dibujarLineas();
    window.addEventListener('resize', dibujarLineas);
    window.addEventListener('scroll', dibujarLineas);

    imageUploader = new ImageUploader({
        previewId: 'modalImagen',
        placeholderId: 'imagenPlaceholder',
        inputId: 'inputImagen',
        removeBtnId: 'btnQuitarImagen',
        infoId: 'imagenInfo',
        wrapperId: 'imagenPreviewWrapper',
        loggerPrefix: '[Instalaciones:Image]'
    });

    configurarFormularios();
    Logger.success('Módulo Instalaciones listo', { nodos: ubicacionTecnicaData.length });
});

// ============================================================
// API: Cargar datos
// ============================================================
async function cargarDatos() {
    Logger.apiCall('GET', '/api/ubicacion_tecnica_json');
    try {
        const res = await fetch("/api/ubicacion_tecnica_json", { credentials: 'same-origin' });
        Logger.apiResponse('GET', '/api/ubicacion_tecnica_json', res.status);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        ubicacionTecnicaData = await res.json();
    } catch (err) {
        Logger.error('Error al cargar datos', err);
        // ✅ UNIFICADO: usa Notify.error en lugar de mostrarNotif
        Notify.error('Error al cargar las ubicaciones');
        ubicacionTecnicaData = [];
    }
}

// ❌ ELIMINADAS las funciones locales mostrarNotif y mostrarConfirm
// ✅ Ahora se usa Notify global (static/js/utils/notifications.js)

// ============================================================
// UTILIDADES DE BÚSQUEDA
// ============================================================
function buscarUbicacionPorJerarquia(ruta, nodo) {
    if (nodo.ruta_jerarquia === ruta) return nodo;
    if (nodo.sububicaciones) {
        for (const h of nodo.sububicaciones) {
            const r = buscarUbicacionPorJerarquia(ruta, h);
            if (r) return r;
        }
    }
    return null;
}

// ============================================================
// UI: Abrir modal de ubicación
// ============================================================
function abrirModalUbicacion(rutaJerarquia) {
    let nodo = null;
    for (const raiz of ubicacionTecnicaData) {
        nodo = buscarUbicacionPorJerarquia(rutaJerarquia, raiz);
        if (nodo) break;
    }

    if (!nodo) {
        Logger.warn('Ubicación no encontrada', { ruta: rutaJerarquia });
        // ✅ UNIFICADO: usa Notify.warning
        Notify.warning('Ubicación no encontrada');
        return;
    }

    Logger.info('Abriendo modal', { nombre: nodo.nombre, ruta: nodo.ruta_jerarquia });

    document.getElementById('nombre').value = nodo.nombre || '';
    document.getElementById('emoji').value = nodo.emoji || '';
    document.getElementById('ruta').value = nodo.ruta || '';
    document.getElementById('ruta_jerarquia').value = nodo.ruta_jerarquia || '';
    document.getElementById('ruta_jerarquia_display').value = nodo.ruta_jerarquia || '';

    if (nodo.imagen && nodo.imagen.trim() !== '') {
        const url = nodo.imagen.startsWith('/') ? nodo.imagen : STATIC_INSTALACIONES + 'img/' + nodo.imagen;
        imageUploader.loadExisting(url);
    } else {
        imageUploader.reset();
    }

    const cont = document.getElementById('sububicacionesContainer');
    cont.innerHTML = '';
    if (nodo.sububicaciones && nodo.sububicaciones.length) {
        nodo.sububicaciones.forEach(sub => {
            const div = document.createElement('div');
            div.className = 'text-white p-1 border-bottom border-secondary';
            div.textContent = `${sub.nombre} (${sub.ruta || 'sin ruta'})`;
            cont.appendChild(div);
        });
    }

    bootstrap.Modal.getOrCreateInstance(document.getElementById('ubicacionModal')).show();
}

// ============================================================
// UI: Crear nodo del árbol
// ============================================================
function crearNodo(nodo) {
    const li = document.createElement('li');
    const nodeDiv = document.createElement('div');
    nodeDiv.className = 'node';
    nodeDiv.tabIndex = 0;

    const img = document.createElement('img');
    if (nodo.imagen && nodo.imagen.trim() !== '') {
        img.src = nodo.imagen.startsWith('/') ? nodo.imagen : STATIC_INSTALACIONES + 'img/' + nodo.imagen;
    } else {
        img.src = DEFAULT_IMAGE;
    }
    img.alt = nodo.ruta || 'Sin ruta';

    const label = document.createElement('div');
    label.className = 'label';
    label.textContent = nodo.ruta && nodo.ruta.trim() !== '' ? nodo.ruta : 'Sin ruta';

    nodeDiv.appendChild(img);
    nodeDiv.appendChild(label);
    li.appendChild(nodeDiv);

    nodeDiv.addEventListener('click', e => {
        e.stopPropagation();
        abrirModalUbicacion(nodo.ruta_jerarquia);
    });

    if (nodo.sububicaciones && nodo.sububicaciones.length > 0) {
        const toggle = document.createElement('button');
        toggle.className = 'toggle btn btn-outline-primary btn-sm';
        toggle.type = 'button';
        toggle.setAttribute('aria-expanded', 'false');
        toggle.title = 'Expandir';
        toggle.textContent = '+';
        nodeDiv.appendChild(toggle);

        const ulHijos = document.createElement('ul');
        ulHijos.className = 'children-container ul-flex collapsed';
        nodo.sububicaciones.forEach(sub => ulHijos.appendChild(crearNodo(sub)));
        li.appendChild(ulHijos);

        toggle.addEventListener('click', e => {
            e.stopPropagation();
            const col = ulHijos.classList.toggle('collapsed');
            toggle.textContent = col ? '+' : '−';
            toggle.setAttribute('aria-expanded', String(!col));
            setTimeout(dibujarLineas, 50);
        });
    }

    return li;
}

// ============================================================
// UI: Dibujar líneas SVG entre nodos
// ============================================================
function dibujarLineas() {
    const container = document.getElementById("tree-container");
    const svg = document.getElementById('svg-lines');
    if (!container || !svg) return;

    while (svg.firstChild) svg.removeChild(svg.firstChild);

    const rect = container.getBoundingClientRect();
    svg.style.width = rect.width + 'px';
    svg.style.height = rect.height + 'px';
    svg.style.top = rect.top + window.scrollY + 'px';
    svg.style.left = rect.left + window.scrollX + 'px';

    container.querySelectorAll('li > .node').forEach(nodeDiv => {
        const li = nodeDiv.parentElement;
        const ulHijos = li.querySelector('ul.children-container:not(.collapsed)');
        if (!ulHijos) return;

        ulHijos.childNodes.forEach(childLi => {
            if (childLi.nodeType !== 1) return;

            const sImg = nodeDiv.querySelector('img').getBoundingClientRect();
            const eImg = childLi.querySelector('.node img')?.getBoundingClientRect();
            if (!eImg) return;

            const x1 = sImg.left + sImg.width / 2 - rect.left;
            const y1 = sImg.bottom - rect.top;
            const x2 = eImg.left + eImg.width / 2 - rect.left;
            const y2 = eImg.top - rect.top;

            const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            g.setAttribute('stroke', '#0d6efd');
            g.setAttribute('fill', 'none');
            g.setAttribute('stroke-width', '2');

            const p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            p.setAttribute('d', `M ${x1} ${y1} L ${x1} ${(y1 + y2) / 2} L ${x2} ${(y1 + y2) / 2} L ${x2} ${y2}`);
            g.appendChild(p);
            svg.appendChild(g);
        });
    });
}

// ============================================================
// API: Fetch helper con logging
// ============================================================
async function manejarFetch(url, options) {
    const method = options.method || 'GET';
    Logger.apiCall(method, url);

    try {
        const res = await fetch(url, { ...options, credentials: 'same-origin' });
        const text = await res.text();
        let json;
        try {
            json = JSON.parse(text);
        } catch {
            return { ok: false, data: { status: 'error', msg: 'Respuesta inválida' } };
        }
        Logger.apiResponse(method, url, res.status, json);
        return { ok: res.ok, data: json };
    } catch (err) {
        Logger.error(`Error ${method} ${url}`, err);
        return { ok: false, data: { status: 'error', msg: err.message } };
    }
}

// ============================================================
// EVENTOS DE FORMULARIOS
// ============================================================
function configurarFormularios() {
    // ---------- GUARDAR EDICIÓN ----------
    document.getElementById('formUbicacion').addEventListener('submit', async e => {
        e.preventDefault();
        const ruta = document.getElementById('ruta_jerarquia').value;
        const formData = new FormData();
        formData.append('ruta_jerarquia', ruta);
        formData.append('nombre', document.getElementById('nombre').value);
        formData.append('emoji', document.getElementById('emoji').value);
        formData.append('ruta', document.getElementById('ruta').value);

        const archivoSel = imageUploader.getSelectedFile();
        const fueQuitada = imageUploader.wasRemoved();
        if (archivoSel) formData.append('imagen', archivoSel);
        else if (fueQuitada) formData.append('eliminar_imagen', 'true');

        const { ok, data } = await manejarFetch('/api/editar_ubicacion', {
            method: 'PUT',
            body: formData
        });

        if (ok && data.status === 'ok') {
            // ✅ UNIFICADO: usa Notify.success
            Notify.success(data.msg || 'Ubicación guardada correctamente');
            Logger.success('Ubicación actualizada', { ruta });
            bootstrap.Modal.getInstance(document.getElementById('ubicacionModal'))?.hide();
            setTimeout(() => location.reload(), 800);
        } else {
            // ✅ UNIFICADO: usa Notify.error
            Notify.error(data.msg || 'Error al guardar');
            Logger.error('Error al guardar', data);
        }
    });

    // ---------- BORRAR UBICACIÓN ----------
    document.getElementById('btnBorrarUbicacion').addEventListener('click', () => {
        const ruta = document.getElementById('ruta_jerarquia').value;
        const nombre = document.getElementById('nombre').value;

        // ✅ UNIFICADO: usa Notify.confirm en lugar de mostrarConfirm
        Notify.confirm(
            'Eliminar ubicación',
            `¿Está seguro que desea eliminar "${nombre}"? Esta acción no se puede deshacer.`,
            async () => {
                const { ok, data } = await manejarFetch('/api/borrar_ubicacion', {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ruta_jerarquia: ruta })
                });

                if (ok && data.status === 'ok') {
                    // ✅ UNIFICADO: usa Notify.success
                    Notify.success(data.msg || 'Ubicación eliminada');
                    setTimeout(() => location.reload(), 800);
                } else {
                    // ✅ UNIFICADO: usa Notify.error
                    Notify.error(data.msg || 'Error al eliminar');
                }
            }
        );
    });

    // ---------- AGREGAR SUBUBICACIÓN ----------
    document.getElementById('btnAgregarHijo').addEventListener('click', () => {
        const cont = document.getElementById('sububicacionesContainer');
        const formDiv = document.createElement('div');
        formDiv.className = 'mb-3 mt-3 border p-2 bg-dark text-white rounded';
        formDiv.innerHTML = `
            <h6>Agregar sububicación</h6>
            <input type="text" id="nombreHijo" class="form-control mb-2" placeholder="Nombre" required>
            <input type="text" id="emojiHijo" class="form-control mb-2" placeholder="Emoji">
            <input type="text" id="rutaHijo" class="form-control mb-2" placeholder="Ruta">
            <div class="mb-2">
                <label class="form-label small">Imagen (opcional)</label>
                <input type="file" id="imagenHijo" class="form-control" accept="image/*">
            </div>
            <button class="btn btn-success btn-sm" id="guardarHijoBtn">Guardar</button>
            <button class="btn btn-cancelar btn-sm" id="cancelarHijoBtn">Cancelar</button>
        `;
        cont.appendChild(formDiv);

        formDiv.querySelector('#cancelarHijoBtn').addEventListener('click', () => formDiv.remove());

        formDiv.querySelector('#guardarHijoBtn').addEventListener('click', async e => {
            e.preventDefault();
            const rutaPadre = document.getElementById('ruta_jerarquia').value;
            const imgFile = formDiv.querySelector('#imagenHijo').files[0];

            const formData = new FormData();
            formData.append('ruta_padre', rutaPadre);
            formData.append('nombre', formDiv.querySelector('#nombreHijo').value);
            formData.append('emoji', formDiv.querySelector('#emojiHijo').value);
            formData.append('ruta', formDiv.querySelector('#rutaHijo').value);
            if (imgFile) formData.append('imagen', imgFile);

            const { ok, data } = await manejarFetch('/api/agregar_sububicacion', {
                method: 'POST',
                body: formData
            });

            if (ok && data.status === 'ok') {
                // ✅ UNIFICADO: usa Notify.success
                Notify.success(data.msg || 'Sububicación agregada');
                setTimeout(() => location.reload(), 800);
            } else {
                // ✅ UNIFICADO: usa Notify.error
                Notify.error(data.msg || 'Error al agregar');
            }
        });
    });
}