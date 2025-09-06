/**
 * JavaScript para el componente Gestión de Menú
 * Maneja la gestión jerárquica de menús
 */

// Variable global para el árbol de menús
let arbolMenus = [];

/**
 * Carga el árbol de menús desde la API
 * @param {Function} cb - Callback a ejecutar cuando se complete la carga
 */
function cargarArbolMenus(cb) {
    fetch('/api/menu_arbol')
        .then(res => res.json())
        .then(data => {
            arbolMenus = data;
            if (cb) cb();
        });
}

/**
 * Renderiza los selectores de niveles jerárquicos
 */
function renderSelectoresNiveles() {
    const cont = document.getElementById('nivelesContainer');
    cont.innerHTML = '';
    let nivel = 0;
    let actual = arbolMenus;
    let seguir = true;
    
    while (seguir) {
        const select = document.createElement('select');
        select.className = 'form-control nivel-select mb-2';
        select.setAttribute('data-nivel', nivel);
        select.innerHTML = `<option value="" selected>Sin seleccionar</option>`;
        
        actual.forEach(item => {
            select.innerHTML += `<option value="${item.ruta_jerarquia}">${item.emoji} ${item.nombre}</option>`;
        });
        
        cont.appendChild(select);

        select.onchange = function () {
            let next = this.nextElementSibling;
            while (next) {
                next.remove();
                next = this.nextElementSibling;
            }
            if (this.value) {
                const seleccionado = buscarNodoPorRuta(arbolMenus, this.value);
                if (seleccionado && seleccionado.submenues && seleccionado.submenues.length > 0) {
                    renderSubnivel(seleccionado.submenues, nivel + 1, this.value);
                }
            }
        };
        seguir = false;
    }
}

/**
 * Renderiza un subnivel de menús
 * @param {Array} submenues - Array de submenús
 * @param {number} nivel - Nivel jerárquico
 * @param {string} rutaPadre - Ruta del elemento padre
 */
function renderSubnivel(submenues, nivel, rutaPadre) {
    const cont = document.getElementById('nivelesContainer');
    const select = document.createElement('select');
    select.className = 'form-control nivel-select mb-2';
    select.setAttribute('data-nivel', nivel);
    select.innerHTML = `<option value="" selected>Sin seleccionar</option>`;
    
    submenues.forEach(item => {
        select.innerHTML += `<option value="${item.ruta_jerarquia}">${item.emoji} ${item.nombre}</option>`;
    });
    
    cont.appendChild(select);

    select.onchange = function () {
        let next = this.nextElementSibling;
        while (next) {
            next.remove();
            next = this.nextElementSibling;
        }
        if (this.value) {
            const seleccionado = buscarNodoPorRuta(arbolMenus, this.value);
            if (seleccionado && seleccionado.submenues && seleccionado.submenues.length > 0) {
                renderSubnivel(seleccionado.submenues, nivel + 1, this.value);
            }
        }
    };
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
    for (let parte of partes) {
        if (!parte) continue;
        let encontrado = actual.find(item => item.nombre === parte);
        if (!encontrado) return null;
        actual = encontrado.submenues;
        if (partes[partes.length - 1] === parte) return encontrado;
    }
    return null;
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
 * Guarda un nuevo menú
 */
function guardar() {
    const nombre = document.getElementById("nombre").value.trim();
    const emoji = document.getElementById("emoji").value.trim();
    const ruta_menu = document.getElementById("ruta_menu").value.trim();
    const ruta_padre = obtenerRutaPadre();

    if (!nombre || !emoji) return alert("Complete todos los campos");

    fetch('/api/menu', {
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
 * Edita un menú existente
 */
function editar() {
    const nombre = document.getElementById("nombre").value.trim();
    const emoji = document.getElementById("emoji").value.trim();
    const ruta_menu = document.getElementById("ruta_menu").value.trim();
    const ruta = document.getElementById("ruta_original").value;

    if (!nombre || !emoji || !ruta) return alert("Complete todos los campos");

    fetch('/api/menu', {
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
 * Elimina un menú
 * @param {string} ruta - Ruta del menú a eliminar
 */
function eliminar(ruta) {
    if (!confirm(`¿Está seguro de eliminar este ítem?`)) return;
    fetch('/api/menu', {
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
 * Prepara el formulario para editar un menú
 * @param {string} ruta_jerarquia - Ruta jerárquica del menú
 * @param {string} nombre - Nombre del menú
 * @param {string} emoji - Emoji del menú
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
}

/**
 * Carga la tabla con todos los menús
 */
function cargarTabla() {
    fetch('/api/menu_arbol')
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
                            <button class="btn btn-sm btn-outline-primary" onclick="prepararEdicion('${menu.ruta_jerarquia}','${menu.nombre}','${menu.emoji}','${menu.ruta || ""}')">Editar</button>
                            <button class="btn btn-sm btn-outline-danger" onclick="eliminar('${menu.ruta_jerarquia}')">Eliminar</button>
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
