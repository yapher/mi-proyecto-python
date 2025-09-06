/**
 * JavaScript para el componente Crear Almacenes
 * Maneja la gestión jerárquica de almacenes
 */

// Variable global para el árbol de almacenes
let arbolcrear_almaceneseses = [];

/**
 * Carga el árbol de almacenes desde la API
 * @param {Function} cb - Callback a ejecutar cuando se complete la carga
 */
function cargarArbolcrear_almaceneseses(cb) {
    fetch('/api/crear_almacenes_arbol')
        .then(res => res.json())
        .then(data => {
            arbolcrear_almaceneseses = data;
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
    let actual = arbolcrear_almaceneseses;
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
                const seleccionado = buscarNodoPorRuta(arbolcrear_almaceneseses, this.value);
                if (seleccionado && seleccionado.subcrear_almacenes && seleccionado.subcrear_almacenes.length > 0) {
                    renderSubnivel(seleccionado.subcrear_almacenes, nivel + 1, this.value);
                }
            }
        };
        seguir = false;
    }
}

/**
 * Renderiza un subnivel de almacenes
 * @param {Array} subcrear_almacenes - Array de subalmacenes
 * @param {number} nivel - Nivel jerárquico
 * @param {string} rutaPadre - Ruta del elemento padre
 */
function renderSubnivel(subcrear_almacenes, nivel, rutaPadre) {
    const cont = document.getElementById('nivelesContainer');
    const select = document.createElement('select');
    select.className = 'form-control nivel-select mb-2';
    select.setAttribute('data-nivel', nivel);
    select.innerHTML = `<option value="" selected>Sin seleccionar</option>`;
    
    subcrear_almacenes.forEach(item => {
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
            const seleccionado = buscarNodoPorRuta(arbolcrear_almaceneseses, this.value);
            if (seleccionado && seleccionado.subcrear_almacenes && seleccionado.subcrear_almacenes.length > 0) {
                renderSubnivel(seleccionado.subcrear_almacenes, nivel + 1, this.value);
            }
        }
    };
}

/**
 * Busca un nodo en el árbol por su ruta jerárquica
 * @param {Array} arbol - Árbol de almacenes
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
        actual = encontrado.subcrear_almacenes;
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
 * Guarda un nuevo almacén
 */
function guardar() {
    const nombre = document.getElementById("nombre").value.trim();
    const emoji = document.getElementById("emoji").value.trim();
    const ruta_crear_almaceneses = document.getElementById("ruta_crear_almaceneses").value.trim();
    const ruta_padre = obtenerRutaPadre();

    if (!nombre || !emoji) return alert("Complete todos los campos");

    fetch('/api/crear_almacenes', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre, emoji, ruta: ruta_crear_almaceneses, ruta_padre })
    }).then(res => res.json())
        .then(res => {
            alert(res.msg);
            cargarTodo();
            cancelar();
        });
}

/**
 * Edita un almacén existente
 */
function editar() {
    const nombre = document.getElementById("nombre").value.trim();
    const emoji = document.getElementById("emoji").value.trim();
    const ruta_crear_almaceneses = document.getElementById("ruta_crear_almaceneses").value.trim();
    const ruta = document.getElementById("ruta_original").value;

    if (!nombre || !emoji || !ruta) return alert("Complete todos los campos");

    fetch('/api/crear_almacenes', {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre, emoji, ruta_crear_almaceneses, ruta })
    }).then(res => res.json())
        .then(res => {
            alert(res.msg);
            cargarTodo();
            cancelar();
        });
}

/**
 * Elimina un almacén
 * @param {string} ruta - Ruta del almacén a eliminar
 */
function eliminar(ruta) {
    if (!confirm(`¿Está seguro de eliminar este ítem?`)) return;
    fetch('/api/crear_almacenes', {
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
 * Prepara el formulario para editar un almacén
 * @param {string} ruta_jerarquia - Ruta jerárquica del almacén
 * @param {string} nombre - Nombre del almacén
 * @param {string} emoji - Emoji del almacén
 * @param {string} ruta_crear_almaceneses - Ruta del almacén
 */
function prepararEdicion(ruta_jerarquia, nombre, emoji, ruta_crear_almaceneses) {
    document.getElementById("nombre").value = nombre;
    document.getElementById("emoji").value = emoji;
    document.getElementById("ruta_crear_almaceneses").value = ruta_crear_almaceneses || "";
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
    document.getElementById("ruta_crear_almaceneses").value = "";
    document.getElementById("ruta_original").value = "";
    document.querySelector(".btn-agregar").style.display = "inline";
    document.querySelector(".btn-editar").classList.remove("active");
    document.querySelector(".btn-cancelar").classList.remove("active");
}

/**
 * Carga la tabla con todos los almacenes
 */
function cargarTabla() {
    fetch('/api/crear_almacenes_arbol')
        .then(res => res.json())
        .then(data => {
            const tabla = document.getElementById("tabla");
            tabla.innerHTML = "";
            
            function recorrer(crear_almaceneseses, nivel = 0) {
                crear_almaceneseses.forEach(crear_almaceneses => {
                    tabla.innerHTML += `
                    <tr>
                        <td>${crear_almaceneses.emoji}</td>
                        <td class="nivel-${nivel}">${crear_almaceneses.nombre}</td>
                        <td>${crear_almaceneses.ruta || ''}</td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary" onclick="prepararEdicion('${crear_almaceneses.ruta_jerarquia}','${crear_almaceneses.nombre}','${crear_almaceneses.emoji}','${crear_almaceneses.ruta || ""}')">Editar</button>
                            <button class="btn btn-sm btn-outline-danger" onclick="eliminar('${crear_almaceneses.ruta_jerarquia}')">Eliminar</button>
                        </td>
                    </tr>
                `;
                    if (crear_almaceneses.subcrear_almacenes && crear_almaceneses.subcrear_almacenes.length > 0) {
                        recorrer(crear_almaceneses.subcrear_almacenes, nivel + 1);
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
    cargarArbolcrear_almaceneseses(() => {
        renderSelectoresNiveles();
        cargarTabla();
    });
}

// Inicializar cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", cargarTodo);
