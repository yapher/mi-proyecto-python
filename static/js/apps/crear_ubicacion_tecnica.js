/**
 * JavaScript para el componente Crear Ubicación Técnica
 * Maneja la gestión jerárquica de ubicaciones técnicas
 */

// Variable global para el árbol de ubicaciones
let arbolUbicaciones = [];

/**
 * Carga el árbol de ubicaciones desde la API
 * @param {Function} cb - Callback a ejecutar cuando se complete la carga
 */
function cargarArbolUbicaciones(cb) {
    fetch('/api/ubicacion_arbol')
        .then(res => res.json())
        .then(data => {
            arbolUbicaciones = data;
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
    let actual = arbolUbicaciones;
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
                const seleccionado = buscarNodoPorRuta(arbolUbicaciones, this.value);
                if (seleccionado && seleccionado.sububicaciones && seleccionado.sububicaciones.length > 0) {
                    renderSubnivel(seleccionado.sububicaciones, nivel + 1, this.value);
                }
            }
        };
        seguir = false;
    }
}

/**
 * Renderiza un subnivel de ubicaciones
 * @param {Array} sububicaciones - Array de sububicaciones
 * @param {number} nivel - Nivel jerárquico
 * @param {string} rutaPadre - Ruta del elemento padre
 */
function renderSubnivel(sububicaciones, nivel, rutaPadre) {
    const cont = document.getElementById('nivelesContainer');
    const select = document.createElement('select');
    select.className = 'form-control nivel-select mb-2';
    select.setAttribute('data-nivel', nivel);
    select.innerHTML = `<option value="" selected>Sin seleccionar</option>`;
    
    sububicaciones.forEach(item => {
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
            const seleccionado = buscarNodoPorRuta(arbolUbicaciones, this.value);
            if (seleccionado && seleccionado.sububicaciones && seleccionado.sububicaciones.length > 0) {
                renderSubnivel(seleccionado.sububicaciones, nivel + 1, this.value);
            }
        }
    };
}

/**
 * Busca un nodo en el árbol por su ruta jerárquica
 * @param {Array} arbol - Árbol de ubicaciones
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
        actual = encontrado.sububicaciones;
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
 * Guarda una nueva ubicación técnica
 */
function guardar() {
    const nombre = document.getElementById("nombre").value.trim();
    const emoji = document.getElementById("emoji").value.trim();
    const ruta_ubicacion = document.getElementById("ruta_ubicacion").value.trim();
    const ruta_padre = obtenerRutaPadre();

    if (!nombre || !emoji) return alert("Complete todos los campos");

    fetch('/api/ubicacion', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre, emoji, ruta: ruta_ubicacion, ruta_padre })
    }).then(res => res.json())
        .then(res => {
            alert(res.msg);
            cargarTodo();
            cancelar();
        });
}

/**
 * Edita una ubicación técnica existente
 */
function editar() {
    const nombre = document.getElementById("nombre").value.trim();
    const emoji = document.getElementById("emoji").value.trim();
    const ruta_ubicacion = document.getElementById("ruta_ubicacion").value.trim();
    const ruta = document.getElementById("ruta_original").value;

    if (!nombre || !emoji || !ruta) return alert("Complete todos los campos");

    fetch('/api/ubicacion', {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre, emoji, ruta_ubicacion, ruta })
    }).then(res => res.json())
        .then(res => {
            alert(res.msg);
            cargarTodo();
            cancelar();
        });
}

/**
 * Elimina una ubicación técnica
 * @param {string} ruta - Ruta de la ubicación a eliminar
 */
function eliminar(ruta) {
    if (!confirm(`¿Está seguro de eliminar este ítem?`)) return;
    fetch('/api/ubicacion', {
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
 * Prepara el formulario para editar una ubicación
 * @param {string} ruta_jerarquia - Ruta jerárquica de la ubicación
 * @param {string} nombre - Nombre de la ubicación
 * @param {string} emoji - Emoji de la ubicación
 * @param {string} ruta_ubicacion - Ruta de la ubicación
 */
function prepararEdicion(ruta_jerarquia, nombre, emoji, ruta_ubicacion) {
    document.getElementById("nombre").value = nombre;
    document.getElementById("emoji").value = emoji;
    document.getElementById("ruta_ubicacion").value = ruta_ubicacion || "";
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
    document.getElementById("ruta_ubicacion").value = "";
    document.getElementById("ruta_original").value = "";
    document.querySelector(".btn-agregar").style.display = "inline";
    document.querySelector(".btn-editar").classList.remove("active");
    document.querySelector(".btn-cancelar").classList.remove("active");
}

/**
 * Carga la tabla con todas las ubicaciones
 */
function cargarTabla() {
    fetch('/api/ubicacion_arbol')
        .then(res => res.json())
        .then(data => {
            const tabla = document.getElementById("tabla");
            tabla.innerHTML = "";
            
            function recorrer(ubicaciones, nivel = 0) {
                ubicaciones.forEach(ubicacion => {
                    tabla.innerHTML += `
                    <tr>
                        <td>${ubicacion.emoji}</td>
                        <td class="nivel-${nivel}">${ubicacion.nombre}</td>
                        <td>${ubicacion.ruta || ''}</td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary" onclick="prepararEdicion('${ubicacion.ruta_jerarquia}','${ubicacion.nombre}','${ubicacion.emoji}','${ubicacion.ruta || ""}')">Editar</button>
                            <button class="btn btn-sm btn-outline-danger" onclick="eliminar('${ubicacion.ruta_jerarquia}')">Eliminar</button>
                        </td>
                    </tr>
                `;
                    if (ubicacion.sububicaciones && ubicacion.sububicaciones.length > 0) {
                        recorrer(ubicacion.sububicaciones, nivel + 1);
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
    cargarArbolUbicaciones(() => {
        renderSelectoresNiveles();
        cargarTabla();
    });
}

// Inicializar cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", cargarTodo);
