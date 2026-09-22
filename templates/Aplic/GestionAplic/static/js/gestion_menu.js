/**
 * JavaScript para Gestión de Menú
 * ✅ Soporte de roles con checkboxes (más intuitivo)
 */
let arbolMenus = [];

function cargarArbolMenus(cb) {
    fetch('/api/menu_arbol')
        .then(res => res.json())
        .then(data => {
            arbolMenus = data;
            if (cb) cb();
        });
}

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

function obtenerRutaPadre() {
    const selects = document.querySelectorAll('.nivel-select');
    let ruta = '';
    selects.forEach(sel => {
        if (sel.value) ruta = sel.value;
    });
    return ruta;
}

// ✅ NUEVO: Obtener roles seleccionados desde checkboxes
function obtenerRolesSeleccionados() {
    const roles = [];
    if (document.getElementById('roleAdmin').checked) roles.push('admin');
    if (document.getElementById('roleEditor').checked) roles.push('editor');
    if (document.getElementById('roleViewer').checked) roles.push('viewer');
    return roles;
}

// ✅ NUEVO: Setear roles en checkboxes
function setearRoles(roles) {
    document.getElementById('roleAdmin').checked = (roles || []).includes('admin');
    document.getElementById('roleEditor').checked = (roles || []).includes('editor');
    document.getElementById('roleViewer').checked = (roles || []).includes('viewer');
}

function guardar() {
    const nombre = document.getElementById("nombre").value.trim();
    const emoji = document.getElementById("emoji").value.trim();
    const ruta_menu = document.getElementById("ruta_menu").value.trim();
    const ruta_padre = obtenerRutaPadre();
    const roles = obtenerRolesSeleccionados();  // ✅ Ahora lee checkboxes

    if (!nombre || !emoji) {
        Notify.warning("Complete todos los campos obligatorios");
        return;
    }

    fetch('/api/menu', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre, emoji, ruta: ruta_menu, ruta_padre, roles })
    }).then(res => res.json())
    .then(res => {
        if (res.type === 'success' || res.msg.includes('correctamente')) {
            Notify.success(res.msg);
            cargarTodo();
            cancelar();
        } else {
            Notify.error(res.msg || "Error al guardar");
        }
    })
    .catch(() => Notify.error("Error de conexión al guardar"));
}

function editar() {
    const nombre = document.getElementById("nombre").value.trim();
    const emoji = document.getElementById("emoji").value.trim();
    const ruta_menu = document.getElementById("ruta_menu").value.trim();
    const ruta = document.getElementById("ruta_original").value;
    const roles = obtenerRolesSeleccionados();  // ✅ Ahora lee checkboxes

    if (!nombre || !emoji || !ruta) {
        Notify.warning("Complete todos los campos obligatorios");
        return;
    }

    fetch('/api/menu', {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre, emoji, ruta_menu, ruta, roles })
    }).then(res => res.json())
    .then(res => {
        if (res.type === 'success' || res.msg.includes('actualizado')) {
            Notify.success(res.msg);
            cargarTodo();
            cancelar();
        } else {
            Notify.error(res.msg || "Error al actualizar");
        }
    })
    .catch(() => Notify.error("Error de conexión al actualizar"));
}

function eliminar(ruta) {
    Notify.confirm(
        "¿Eliminar este ítem?",
        "Esta acción no se puede deshacer y eliminará también todos sus submenús.",
        () => {
            fetch('/api/menu', {
                method: "DELETE",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ ruta })
            }).then(res => res.json())
            .then(res => {
                if (res.type === 'success' || res.msg.includes('eliminado')) {
                    Notify.success(res.msg);
                    cargarTodo();
                    cancelar();
                } else {
                    Notify.error(res.msg || "Error al eliminar");
                }
            })
            .catch(() => Notify.error("Error de conexión al eliminar"));
        }
    );
}

function prepararEdicion(ruta_jerarquia, nombre, emoji, ruta_menu, roles) {
    document.getElementById("nombre").value = nombre;
    document.getElementById("emoji").value = emoji;
    document.getElementById("ruta_menu").value = ruta_menu || "";
    document.getElementById("ruta_original").value = ruta_jerarquia;
    setearRoles(roles || []);  // ✅ Ahora setea checkboxes
    document.querySelector(".btn-agregar").style.display = "none";
    document.querySelector(".btn-editar-menu").classList.add("active");
    document.querySelector(".btn-cancelar-menu").classList.add("active");
}

function cancelar() {
    document.getElementById("nombre").value = "";
    document.getElementById("emoji").value = "";
    document.getElementById("ruta_menu").value = "";
    document.getElementById("ruta_original").value = "";
    setearRoles([]);  // ✅ Ahora limpia checkboxes
    document.querySelector(".btn-agregar").style.display = "inline";
    document.querySelector(".btn-editar-menu").classList.remove("active");
    document.querySelector(".btn-cancelar-menu").classList.remove("active");
}

function formatearRoles(roles) {
    // ✅ Si no hay roles o lista vacía, mostrar "Todos"
    if (!roles || !Array.isArray(roles) || roles.length === 0) {
        return '<span class="badge bg-success">🌐 Todos</span>';
    }
    const labels = {
        'admin': '👑 Admin',
        'editor': '✏️ Editor',
        'viewer': '👁️ Viewer'
    };
    return roles.map(r =>
        `<span class="badge bg-info me-1">${labels[r] || r}</span>`
    ).join('');
}

function cargarTabla() {
    fetch('/api/menu_arbol')
        .then(res => res.json())
        .then(data => {
            const tabla = document.getElementById("tabla");
            tabla.innerHTML = "";
            function recorrer(menus, nivel = 0) {
                menus.forEach(menu => {
                    const roles = menu.roles || [];
                    const rolesJson = JSON.stringify(roles).replace(/"/g, '&quot;');
                    tabla.innerHTML += `
                        <tr>
                            <td>${menu.emoji}</td>
                            <td class="nivel-${nivel}">${menu.nombre}</td>
                            <td>${menu.ruta || ''}</td>
                            <td>${formatearRoles(roles)}</td>
                            <td>
                                <button class="btn btn-sm btn-outline-primary"
                                    onclick="prepararEdicion('${menu.ruta_jerarquia}','${menu.nombre}','${menu.emoji}','${menu.ruta || ""}', ${rolesJson})">
                                    Editar
                                </button>
                                <button class="btn btn-sm btn-outline-danger"
                                    onclick="eliminar('${menu.ruta_jerarquia}')">
                                    Eliminar
                                </button>
                            </td>
                        </tr>`;
                    if (menu.submenues && menu.submenues.length > 0) {
                        recorrer(menu.submenues, nivel + 1);
                    }
                });
            }
            recorrer(data);
        });
}

function cargarTodo() {
    cargarArbolMenus(() => {
        renderSelectoresNiveles();
        cargarTabla();
    });
}

document.addEventListener("DOMContentLoaded", cargarTodo);