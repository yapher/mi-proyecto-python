// cudRubro.js

function guardar() {
    const nombre = document.getElementById("nombre").value.trim();
    const emoji = document.getElementById("emoji").value.trim();
    const ruta_menu = document.getElementById("ruta_menu").value.trim();
    const ruta_padre = obtenerRutaPadre();

    if (!nombre || !emoji) return new Noty({
        type: 'warning',
        layout: 'topRight',
        timeout: 3000,
        theme: 'mint',
        text: 'Complete los campos'
    }).show();

    fetch('/api/rubro', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre, emoji, ruta: ruta_menu, ruta_padre })
    }).then(res => res.json())
        .then(res => {
            new Noty({
                type: res.type || 'success',
                layout: 'topRight',
                timeout: 3000,
                theme: 'mint',
                text: res.msg
            }).show();
            cargarTodo();
            cancelar();
            cerrarModal();
        });
}

function editar() {
    const nombre = document.getElementById("nombre").value.trim();
    const emoji = document.getElementById("emoji").value.trim();
    const ruta_menu = document.getElementById("ruta_menu").value.trim();
    const ruta = document.getElementById("ruta_original").value;

    if (!nombre || !emoji || !ruta) return new Noty({
        type: 'warning',
        layout: 'topRight',
        timeout: 3000,
        theme: 'mint',
        text: 'Complete los campos'
    }).show();

    fetch('/api/rubro', {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre, emoji, ruta_menu, ruta })
    }).then(res => res.json())
        .then(res => {
            new Noty({
                type: res.type || 'success',
                text: res.msg,
                layout: 'topRight',
                timeout: 3000
            }).show();
            cargarTodo();
            cancelar();
            cerrarModal();
        });
}

function eliminar(ruta) {
    Swal.fire({
        title: '¿Está seguro de eliminar este ítem?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar',
        customClass: {
            confirmButton: 'btn  btn-outline-danger',
            cancelButton: 'btn  btn-outline-primary'
        },
        buttonsStyling: false,
    }).then((result) => {
        if (result.isConfirmed) {
            fetch('/api/rubro', {
                method: "DELETE",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ ruta })
            }).then(res => res.json())
                .then(res => {
                    new Noty({
                        type: res.type || 'success',
                        text: res.msg,
                        layout: 'topRight',
                        timeout: 3000
                    }).show();
                    cargarTodo();
                    cancelar();
                    cerrarModal();
                });
        }
    });
}

function cancelar() {
    document.getElementById("nombre").value = "";
    document.getElementById("emoji").value = "";
    document.getElementById("ruta_menu").value = "";
    document.getElementById("ruta_original").value = "";
    document.querySelector(".btn-agregar").style.display = "inline";
    document.querySelector(".btn-editar").style.display = "none";
    document.querySelector(".btn-cancelar").style.display = "none";
    renderSelectoresNiveles();
}
function obtenerRutaPadre() {
    const selects = document.querySelectorAll('.nivel-select');
    let ruta = '';
    selects.forEach(sel => {
        if (sel.value) ruta = sel.value;
    });
    return ruta;
}

function cerrarModal() {
    const modalEl = document.getElementById('agregarModal');
    const modal = bootstrap.Modal.getInstance(modalEl);
    if (modal) modal.hide();
}
