/**
 * JavaScript para el componente Instalaciones
 * Maneja la funcionalidad de visualización de árbol jerárquico de ubicaciones técnicas
 */

// Variables globales
let ubicacionTecnicaData = null;

// Inicialización cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById("tree-container");
    const svg = document.getElementById('svg-lines');

    // Cargar datos iniciales
    await cargarDatos();
    
    // Crear el árbol
    const root = document.createElement('ul');
    root.style.position = 'relative';
    root.classList.add('ul-flex');
    
    ubicacionTecnicaData.forEach(nodo => root.appendChild(crearNodo(nodo)));
    container.appendChild(root);

    // Dibujar líneas y configurar event listeners
    dibujarLineas();
    window.addEventListener('resize', dibujarLineas);
    window.addEventListener('scroll', dibujarLineas);

    // Configurar formularios
    configurarFormularios();
});

/**
 * Carga los datos de ubicaciones técnicas desde la API
 */
async function cargarDatos() {
    const res = await fetch("/api/ubicacion_tecnica_json", {credentials:'same-origin'});
    ubicacionTecnicaData = await res.json();
}

/**
 * Busca una ubicación por su ruta jerárquica
 * @param {string} ruta_jerarquia - Ruta jerárquica a buscar
 * @param {Object} nodo - Nodo donde buscar
 * @returns {Object|null} Nodo encontrado o null
 */
function buscarUbicacionPorJerarquia(ruta_jerarquia, nodo) {
    if (nodo.ruta_jerarquia === ruta_jerarquia) return nodo;
    if (nodo.sububicaciones) {
        for (const hijo of nodo.sububicaciones) {
            const res = buscarUbicacionPorJerarquia(ruta_jerarquia, hijo);
            if (res) return res;
        }
    }
    return null;
}

/**
 * Abre el modal con la información de una ubicación
 * @param {string} rutaJerarquia - Ruta jerárquica de la ubicación
 */
function abrirModalUbicacion(rutaJerarquia) {
    let nodo = null;
    for (const raiz of ubicacionTecnicaData) {
        nodo = buscarUbicacionPorJerarquia(rutaJerarquia, raiz);
        if (nodo) break;
    }
    if (!nodo) {
        alert("Ubicación no encontrada");
        return;
    }
    const modalEl = document.getElementById('ubicacionModal');
    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);

    // Llenar el formulario con los datos del nodo
    document.getElementById('nombre').value = nodo.nombre || '';
    document.getElementById('emoji').value = nodo.emoji || '';
    document.getElementById('ruta').value = nodo.ruta || '';
    document.getElementById('ruta_jerarquia').value = nodo.ruta_jerarquia || '';
    document.getElementById('ruta_jerarquia_display').value = nodo.ruta_jerarquia || '';
    document.getElementById('modalImagen').src = nodo.imagen || "/static/factory.png";

    // Mostrar sububicaciones
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
    modal.show();
}

/**
 * Crea un nodo del árbol
 * @param {Object} nodo - Datos del nodo
 * @returns {HTMLElement} Elemento li creado
 */
function crearNodo(nodo) {
    const li = document.createElement('li');
    const nodeDiv = document.createElement('div');
    nodeDiv.className = 'node';
    nodeDiv.tabIndex = 0;

    const img = document.createElement('img');
    img.src = nodo.imagen && nodo.imagen.trim()!=='' ? nodo.imagen : '/static/factory.png';
    img.alt = nodo.ruta || 'Sin ruta';

    const label = document.createElement('div');
    label.className = 'label';
    label.textContent = nodo.ruta && nodo.ruta.trim()!=='' ? nodo.ruta : 'Sin ruta';

    nodeDiv.appendChild(img);
    nodeDiv.appendChild(label);
    li.appendChild(nodeDiv);

    // Event listener para abrir modal
    nodeDiv.addEventListener('click', e=>{
        e.stopPropagation();
        abrirModalUbicacion(nodo.ruta_jerarquia);
    });

    // Si tiene sububicaciones, crear toggle y contenedor
    if (nodo.sububicaciones && nodo.sububicaciones.length > 0) {
        const toggle = document.createElement('button');
        toggle.className = 'toggle btn btn-outline-primary btn-sm';
        toggle.type = 'button';
        toggle.setAttribute('aria-expanded','false');
        toggle.title = 'Expandir';
        toggle.textContent = '+';
        nodeDiv.appendChild(toggle);

        const ulHijos = document.createElement('ul');
        ulHijos.className = 'children-container ul-flex collapsed';
        nodo.sububicaciones.forEach(sub => ulHijos.appendChild(crearNodo(sub)));
        li.appendChild(ulHijos);

        // Event listener para toggle
        toggle.addEventListener('click', e=>{
            e.stopPropagation();
            const colapsado = ulHijos.classList.toggle('collapsed');
            toggle.textContent = colapsado ? '+' : '−';
            toggle.setAttribute('aria-expanded', String(!colapsado));
            setTimeout(dibujarLineas, 50);
        });

        // Event listener para teclado
        nodeDiv.addEventListener('keydown', e=>{
            if(e.key==='Enter'||e.key===' '){
                e.preventDefault();
                toggle.click();
            }
        });
    }

    return li;
}

/**
 * Dibuja las líneas de conexión entre nodos
 */
function dibujarLineas() {
    const container = document.getElementById("tree-container");
    const svg = document.getElementById('svg-lines');
    
    while(svg.firstChild) svg.removeChild(svg.firstChild);
    const containerRect = container.getBoundingClientRect();
    svg.style.width = containerRect.width + 'px';
    svg.style.height = containerRect.height + 'px';
    svg.style.top = containerRect.top + window.scrollY + 'px';
    svg.style.left = containerRect.left + window.scrollX + 'px';

    const parentNodes = container.querySelectorAll('li > .node');
    parentNodes.forEach(nodeDiv => {
        const li = nodeDiv.parentElement;
        const ulHijos = li.querySelector('ul.children-container:not(.collapsed)');
        if(!ulHijos) return;
        ulHijos.childNodes.forEach(childLi => {
            if(childLi.nodeType !== 1) return;
            const startImg = nodeDiv.querySelector('img').getBoundingClientRect();
            const endNode = childLi.querySelector('.node img');
            if(!endNode) return;
            const endImg = endNode.getBoundingClientRect();

            const x1 = startImg.left + startImg.width/2 - containerRect.left;
            const y1 = startImg.bottom - containerRect.top;
            const x2 = endImg.left + endImg.width/2 - containerRect.left;
            const y2 = endImg.top - containerRect.top;

            const group = document.createElementNS('http://www.w3.org/2000/svg','g');
            group.setAttribute('stroke','#0d6efd');
            group.setAttribute('fill','none');
            group.setAttribute('stroke-width','2');

            const path = document.createElementNS('http://www.w3.org/2000/svg','path');
            const d = `M ${x1} ${y1} L ${x1} ${(y1+y2)/2} L ${x2} ${(y1+y2)/2} L ${x2} ${y2}`;
            path.setAttribute('d', d);
            group.appendChild(path);
            svg.appendChild(group);
        });
    });
}

/**
 * Maneja las peticiones fetch con manejo de errores
 * @param {string} url - URL de la petición
 * @param {Object} options - Opciones de la petición
 * @returns {Object} Resultado de la petición
 */
async function manejarFetch(url, options){
    try {
        const res = await fetch(url,{...options, credentials:'same-origin'});
        const text = await res.text();
        try {
            const json = JSON.parse(text);
            return {ok: res.ok, data: json};
        } catch {
            return {ok:false, data:{status:'error', msg:'Respuesta no es JSON: '+text}};
        }
    } catch(err){
        return {ok:false, data:{status:'error', msg: err.message}};
    }
}

/**
 * Configura los event listeners de los formularios
 */
function configurarFormularios() {
    // Formulario principal de ubicación
    document.getElementById('formUbicacion').addEventListener('submit', async e=>{
        e.preventDefault();
        const ruta = document.getElementById('ruta_jerarquia').value;
        const datos = {
            ruta_jerarquia: ruta,
            nombre: document.getElementById('nombre').value,
            emoji: document.getElementById('emoji').value,
            ruta: document.getElementById('ruta').value,
            imagen: document.getElementById('imagen').value
        };
        const {ok, data} = await manejarFetch('/api/editar_ubicacion',{
            method:'PUT',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify(datos)
        });
        if(ok && data.status==='ok') alert('Datos guardados correctamente'), location.reload();
        else alert('Error al guardar cambios: '+(data.msg||JSON.stringify(data)));
    });

    // Botón borrar ubicación
    document.getElementById('btnBorrarUbicacion').addEventListener('click', async ()=>{
        const ruta = document.getElementById('ruta_jerarquia').value;
        if(!confirm('¿Seguro que quieres borrar esta ubicación?')) return;
        const {ok, data} = await manejarFetch('/api/borrar_ubicacion',{
            method:'DELETE',
            headers:{'Content-Type':'application/json'},
            body: JSON.stringify({ruta_jerarquia: ruta})
        });
        if(ok && data.status==='ok') alert('Ubicación borrada'), location.reload();
        else alert('Error al borrar ubicación: '+(data.msg||JSON.stringify(data)));
    });

    // Botón agregar hijo
    document.getElementById('btnAgregarHijo').addEventListener('click', () => {
        const cont = document.getElementById('sububicacionesContainer');
        const formDiv = document.createElement('div');
        formDiv.className = 'mb-3 mt-3 border p-2 bg-dark text-white rounded';

        formDiv.innerHTML = `
            <h6>Agregar sububicación</h6>
            <input type="text" id="nombreHijo" class="form-control mb-2" placeholder="Nombre" required>
            <input type="text" id="emojiHijo" class="form-control mb-2" placeholder="Emoji">
            <input type="text" id="rutaHijo" class="form-control mb-2" placeholder="Ruta">
            <button class="btn btn-success btn-sm" id="guardarHijoBtn">Guardar sububicación</button>
        `;
        cont.appendChild(formDiv);

        formDiv.querySelector('#guardarHijoBtn').addEventListener('click', async e => {
            e.preventDefault();
            const nuevoHijo = {
                nombre: formDiv.querySelector('#nombreHijo').value,
                emoji: formDiv.querySelector('#emojiHijo').value,
                ruta: formDiv.querySelector('#rutaHijo').value,
                ruta_jerarquia: '',
                sububicaciones: []
            };
            const rutaPadre = document.getElementById('ruta_jerarquia').value;
            const {ok, data} = await manejarFetch('/api/agregar_sububicacion',{
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body: JSON.stringify({ruta_padre: rutaPadre, nuevo_hijo: nuevoHijo})
            });
            if(ok && data.status==='ok') alert('Sububicación agregada'), location.reload();
            else alert('Error al agregar sububicación: '+(data.msg||JSON.stringify(data)));
        });
    });
}
