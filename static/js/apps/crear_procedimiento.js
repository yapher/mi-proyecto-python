/**
 * JavaScript para el componente Crear Procedimiento
 * Maneja la gestión jerárquica de procedimientos
 */

// Variable global para el árbol de menús
let arbolMenus = [];

/**
 * Carga el árbol de menús desde la API
 * @param {Function} cb - Callback a ejecutar cuando se complete la carga
 */
function cargarArbolMenus(cb) {
    fetch('/api/proce_arbol')
        .then(res => res.json())
        .then(data => {
            arbolMenus = data;
            if (cb) cb();
        });
}

/**
 * Renderiza los selectores de niveles jerárquicos
 * @param {string} seleccionRuta - Ruta seleccionada para edición
 */
function renderSelectoresNiveles(seleccionRuta = "") {
    const cont = document.getElementById('nivelesContainer');
    cont.innerHTML = '';

    function agregarSelect(nodos, nivel, rutaSeleccionada = "") {
        const select = document.createElement('select');
        select.className = 'form-control nivel-select mb-2';
        select.setAttribute('data-nivel', nivel);
        select.innerHTML = `<option value="" ${rutaSeleccionada === "" ? "selected" : ""}>Sin seleccionar</option>`;
        
        nodos.forEach(item => {
            const selected = (rutaSeleccionada === item.ruta_jerarquia) ? 'selected' : '';
            select.innerHTML += `<option value="${item.ruta_jerarquia}" ${selected}>${item.emoji} ${item.nombre}</option>`;
        });

        select.onchange = function () {
            // Eliminar selects inferiores
            let siguiente = this.nextElementSibling;
            while (siguiente) {
                siguiente.remove();
                siguiente = this.nextElementSibling;
            }

            if (this.value) {
                const seleccionado = buscarNodoPorRuta(arbolMenus, this.value);
                if (seleccionado && seleccionado.submenues && seleccionado.submenues.length > 0) {
                    agregarSelect(seleccionado.submenues, nivel + 1);
                }
            }
        };

        cont.appendChild(select);
    }

    if (seleccionRuta) {
        // Construir selects para cada nivel basado en ruta seleccionada
        const partes = seleccionRuta.split('.');
        let nodosActuales = arbolMenus;

        for (let i = 0; i < partes.length; i++) {
            const rutaParcial = partes.slice(0, i + 1).join('.');
            agregarSelect(nodosActuales, i, rutaParcial);

            const nodoSeleccionado = nodosActuales.find(n => n.ruta_jerarquia === rutaParcial);
            if (nodoSeleccionado && nodoSeleccionado.submenues && nodoSeleccionado.submenues.length > 0) {
                nodosActuales = nodoSeleccionado.submenues;
            } else {
                break;
            }
        }
    } else {
        agregarSelect(arbolMenus, 0);
    }
}

/**
 * Obtiene la siguiente ruta en la jerarquía
 * @param {string} ruta - Ruta actual
 * @returns {string} Siguiente ruta
 */
function getNextRuta(ruta) {
    const partes = ruta.split('.');
    if (partes.length === 0) return '';
    return partes.slice(0, partes.length + 1).join('.');
}

/**
 * Busca un nodo en el árbol por su ruta jerárquica
 * @param {Array} arbol - Árbol de menús
 * @param {string} ruta - Ruta jerárquica a buscar
 * @returns {Object|null} Nodo encontrado o null
 */
function buscarNodoPorRuta(arbol, ruta) {
    const partes = ruta.split('.');
    let actual = arbol;
    let nodoEncontrado = null;
    
    for (let i = 0; i < partes.length; i++) {
        const parteActual = partes.slice(0, i + 1).join('.');
        nodoEncontrado = actual.find(item => item.ruta_jerarquia === parteActual);
        if (!nodoEncontrado) return null;
        actual = nodoEncontrado.submenues || [];
    }
    return nodoEncontrado;
}

/**
 * Obtiene la ruta del elemento padre seleccionado
 * @returns {string} Ruta del padre
 */
function obtenerRutaPadre() {
    const selects = document.querySelectorAll('.nivel-select');
    let ruta = '';
    selects.forEach(sel => {
        if (sel.value) ruta = sel.value;
    });
    return ruta;
}

/**
 * Guarda un nuevo procedimiento
 */
function guardar() {
    const nombre = document.getElementById("nombre").value;
    const emoji = document.getElementById("emoji").value.trim();
    const ruta_menu = document.getElementById("ruta_menu").value.trim();
    const ruta_padre = obtenerRutaPadre();

    if (!nombre || !emoji) return alert("Complete todos los campos");

    fetch('/api/proce', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre, emoji, ruta: ruta_menu, ruta_padre })
    }).then(res => res.json())
        .then(res => {
            alert(res.msg);
            cargarTodo();
            cancelar();
        });
}

/**
 * Edita un procedimiento existente
 */
function editar() {
    const nombre = document.getElementById("nombre").value;
    const emoji = document.getElementById("emoji").value.trim();
    const ruta_menu = document.getElementById("ruta_menu").value.trim();
    const ruta = document.getElementById("ruta_original").value;

    if (!nombre || !emoji || !ruta) return alert("Complete todos los campos");

    fetch('/api/proce', {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre, emoji, ruta_menu, ruta })
    }).then(res => res.json())
        .then(res => {
            alert(res.msg);
            cargarTodo();
            cancelar();
        });
}

/**
 * Elimina un procedimiento
 * @param {string} ruta - Ruta del procedimiento a eliminar
 */
function eliminar(ruta) {
    if (!confirm(`¿Está seguro de eliminar este ítem?`)) return;
    fetch('/api/proce', {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ruta })
    }).then(res => res.json())
        .then(res => {
            alert(res.msg);
            cargarTodo();
            cancelar();
        });
}

/**
 * Prepara la edición desde un dataset de botón
 * @param {HTMLElement} btn - Botón que contiene los datos
 */
function prepararEdicionDesdeDataset(btn) {
    const nombre = decodeURIComponent(btn.dataset.nombre);
    const emoji = decodeURIComponent(btn.dataset.emoji);
    const ruta_menu = decodeURIComponent(btn.dataset.ruta_menu);
    const ruta_jerarquia = btn.dataset.ruta;

    prepararEdicion(ruta_jerarquia, nombre, emoji, ruta_menu);
}

/**
 * Prepara el formulario para editar un procedimiento
 * @param {string} ruta_jerarquia - Ruta jerárquica del procedimiento
 * @param {string} nombre - Nombre del procedimiento
 * @param {string} emoji - Emoji del procedimiento
 * @param {string} ruta_menu - Ruta del menú
 */
function prepararEdicion(ruta_jerarquia, nombre, emoji, ruta_menu) {
    document.getElementById("nombre").value = nombre;
    document.getElementById("emoji").value = emoji;
    document.getElementById("ruta_menu").value = ruta_menu || "";
    document.getElementById("ruta_original").value = ruta_jerarquia;
    document.querySelector(".btn-agregar").style.display = "none";
    document.querySelector(".btn-editar").classList.add("active");
    document.querySelector(".btn-cancelar").classList.add("active");

    const rutaPadre = ruta_jerarquia.split('.').slice(0, -1).join('.');
    renderSelectoresNiveles(rutaPadre);
}

/**
 * Cancela la edición y limpia el formulario
 */
function cancelar() {
    document.getElementById("nombre").value = "";
    document.getElementById("emoji").value = "";
    document.getElementById("ruta_menu").value = "";
    document.getElementById("ruta_original").value = "";
    document.querySelector(".btn-agregar").style.display = "inline";
    document.querySelector(".btn-editar").classList.remove("active");
    document.querySelector(".btn-cancelar").classList.remove("active");
    renderSelectoresNiveles();
}

/**
 * Carga la tabla con todos los procedimientos
 */
function cargarTabla() {
    fetch('/api/proce_arbol')
        .then(res => res.json())
        .then(data => {
            const tabla = document.getElementById("tabla");
            tabla.innerHTML = "";
            
            function recorrer(menus, nivel = 0) {
                menus.forEach(menu => {
                    tabla.innerHTML += `
                    <tr>
                        <td>${menu.emoji}</td>
                        <td class="nivel-${nivel}">${menu.nombre}</td>
                        <td>${menu.ruta || ''}</td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary"
                                data-ruta="${menu.ruta_jerarquia}"
                                data-nombre="${encodeURIComponent(menu.nombre)}"
                                data-emoji="${encodeURIComponent(menu.emoji)}"
                                data-ruta_menu="${encodeURIComponent(menu.ruta || "")}"
                                onclick="prepararEdicionDesdeDataset(this)">Editar</button>
                            <button class="btn btn-sm btn-outline-danger"
                                onclick="eliminar('${menu.ruta_jerarquia}')">Eliminar</button>
                        </td>
                    </tr>
                `;
                    if (menu.submenues && menu.submenues.length > 0) {
                        recorrer(menu.submenues, nivel + 1);
                    }
                });
            }
            recorrer(data);
        });
}

/**
 * Carga todos los datos necesarios
 */
function cargarTodo() {
    cargarArbolMenus(() => {
        renderSelectoresNiveles();
        cargarTabla();
    });
}

// Inicializar cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", cargarTodo);
