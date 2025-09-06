function guardarPago() {
    const id = document.getElementById('pagoId').value;
    const texto = obtenerRutaPadre();

    let categoria, subcategoria;

    if (texto.includes(".")) {
        [categoria, subcategoria] = texto.split(".");
    } else {
        categoria = texto;
        subcategoria = null;
    }

    const tipo = document.getElementById('tipo').value;
    const cuotas = parseInt(document.getElementById('cuotas').value) || 1;
    const importeTotal = parseFloat(document.getElementById('importe').value);
    const vencimiento = document.getElementById('vencimiento').value;

    if (!categoria || !importeTotal || !vencimiento) {
        return new Noty({
            type: 'warning',
            layout: 'topRight',
            timeout: 3000,
            theme: 'mint',
            text: 'Complete los campos obligatorios'
        }).show();
    }

    let pagos = [];

    if (tipo === "cuotas") {
        const importeCuota = parseFloat((importeTotal / cuotas).toFixed(2));
        let fecha = new Date(vencimiento);

        for (let i = 0; i < cuotas; i++) {
            const pago = {
                id: Date.now() + i,
                rubro: categoria,
                descripcion: subcategoria,
                importe: importeCuota,
                tipo: "cuota",
                cuota_numero: i + 1,
                cuota_total: cuotas,
                vencimiento: fecha.toISOString().split('T')[0],
                pagado: false
            };
            pagos.push(pago);

            // Avanzar 1 mes
            fecha.setMonth(fecha.getMonth() + 1);
        }
    } else {
        pagos.push({
            id: Date.now(),
            rubro: categoria,
            descripcion: subcategoria,
            importe: importeTotal,
            tipo: "único",
            vencimiento: vencimiento,
            pagado: false
        });
    }

    fetch('/pagos/agregar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(pagos)
    })
        .then(() => {
            filtrarPorMes();
            mostrarFormulario(null);
            cerrarModal();
        })
        .catch(err => {
            console.error('Error al guardar:', err);
        });
}

function editar(pago) {
    abrirModal();
    mostrarFormulario(pago);
}

function mostrarFormulario(p = null) {
    if (p) {
        document.getElementById('pagoId').value = p.id || '';
        document.getElementById('importe').value = p.importe || '';
        document.getElementById('tipo').value = p.tipo || 'único';
        document.getElementById('cuotas').value = p.cuotas || '';
        document.getElementById('vencimiento').value = p.vencimiento || '';
        document.querySelector(".btn-cancelar").style.display = "inline";

        // Combinar rubro y descripción para armar la ruta
        let rutaCompleta = p.rubro;
        if (p.descripcion) rutaCompleta += "." + p.descripcion;

        // Mostrar los selectores de nivel con la ruta seleccionada
        renderSelectoresNiveles(rutaCompleta);

    } else {
        document.getElementById('pagoId').value = '';
        document.querySelectorAll('#formulario input, #formulario select').forEach(i => i.value = '');
        
        // Fecha actual
        const hoy = new Date();
        const yyyy = hoy.getFullYear();
        const mm = String(hoy.getMonth() + 1).padStart(2, '0');
        const dd = String(hoy.getDate()).padStart(2, '0');
        const fechaActual = `${yyyy}-${mm}-${dd}`;
        document.getElementById('vencimiento').value = fechaActual;

        // Volver a mostrar el primer nivel del selector
        renderSelectoresNiveles();

        document.querySelector(".btn-cancelar").style.display = "none";
    }
}

function cancelar() {
    mostrarFormulario(null);
}

function eliminar(id) {
    Swal.fire({
        title: '¿Estás seguro?',
        text: "Esta acción no se puede deshacer",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sí, eliminar'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/pagos/eliminar/${id}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' }
            })
                .then(response => {
                    if (!response.ok) throw new Error("Error en la eliminación");
                    return response.json();
                })
                .then(data => {
                    Swal.fire('Eliminado', data.mensaje, 'success');
                    filtrarPorMes();
                })
                .catch(() => {
                    Swal.fire('Error', 'No se pudo eliminar el pago.', 'error');
                });
        }
    });
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

function abrirModal() {
    const modalEl = document.getElementById('agregarModal');
    let modal = bootstrap.Modal.getInstance(modalEl);
    if (!modal) {
        modal = new bootstrap.Modal(modalEl);
    }
    modal.show();
}
