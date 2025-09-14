let pagoEnEdicion = null;

// Función para renderizar selectores de rubros multinivel
function renderSelectoresNiveles(seleccion = '') {
    const contenedor = document.getElementById('contenedor-rubros');
    if (!contenedor) return;

    contenedor.innerHTML = ''; // Limpiar selects anteriores

    // Traer los rubros desde el backend
    fetch('/rubros/listar')
        .then(res => res.json())
        .then(rubros => {
            // Crear primer select
            const primerSelect = document.createElement('select');
            primerSelect.className = 'form-control ps-5 nivel-select';
            primerSelect.innerHTML = '<option value="">Seleccione Rubro</option>';
            rubros.forEach(r => {
                primerSelect.innerHTML += `<option value="${r.nombre}">${r.nombre}</option>`;
            });
            contenedor.appendChild(primerSelect);

            // Si hay selección previa, preseleccionarla
            if (seleccion) {
                const niveles = seleccion.split('.');
                primerSelect.value = niveles[0] || '';
            }

            // Detectar cambio y mostrar subcategorías si existen
            primerSelect.addEventListener('change', () => {
                // Eliminar selects siguientes
                while (primerSelect.nextSibling) {
                    contenedor.removeChild(primerSelect.nextSibling);
                }

                const rubroSeleccionado = rubros.find(r => r.nombre === primerSelect.value);
                if (rubroSeleccionado && rubroSeleccionado.subcategorias && rubroSeleccionado.subcategorias.length) {
                    const subSelect = document.createElement('select');
                    subSelect.className = 'form-control ps-5 nivel-select mt-2';
                    subSelect.innerHTML = '<option value="">Seleccione Subcategoría</option>';
                    rubroSeleccionado.subcategorias.forEach(s => {
                        subSelect.innerHTML += `<option value="${s}">${s}</option>`;
                    });
                    contenedor.appendChild(subSelect);

                    // Preseleccionar subcategoría si hay
                    if (seleccion) {
                        const niveles = seleccion.split('.');
                        subSelect.value = niveles[1] || '';
                    }

                    // Si hay más niveles, se puede iterar recursivamente
                }
            });

            // Disparar evento change para precargar subcategorías si se editó
            if (seleccion) primerSelect.dispatchEvent(new Event('change'));
        })
        .catch(err => console.error('Error al cargar rubros:', err));
}

// ------------------------ Funciones existentes ------------------------

function guardarPago() {
    let texto = obtenerRutaPadre();
    if (!texto && pagoEnEdicion) texto = pagoEnEdicion.rubro || '';

    let categoria, subcategoria;
    if (texto && texto.includes(".")) {
        [categoria, subcategoria] = texto.split(".");
    } else {
        categoria = texto || '';
        subcategoria = null;
    }

    const tipo = document.getElementById('tipo').value;
    const cuotas = parseInt(document.getElementById('cuotas').value) || 1;
    const importeTotal = parseFloat(document.getElementById('importe').value);
    let vencimiento = document.getElementById('vencimiento').value;

    if (!categoria || isNaN(importeTotal) || importeTotal <= 0) {
        return new Noty({
            type: 'warning',
            layout: 'topRight',
            timeout: 3000,
            theme: 'mint',
            text: 'Debe seleccionar un rubro y un importe válido'
        }).show();
    }

    if (!vencimiento) vencimiento = new Date().toISOString().split('T')[0];
    const descripcion = subcategoria || document.getElementById('descripcion').value || "";

    if (pagoEnEdicion) {
        const pagoEditar = {
            id: pagoEnEdicion.id,
            rubro: categoria,
            descripcion: descripcion,
            importe: importeTotal,
            tipo: tipo,
            vencimiento: vencimiento,
            pagado: pagoEnEdicion.pagado
        };

        fetch(`/pagos/editar/${pagoEnEdicion.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(pagoEditar)
        })
        .then(response => {
            if (!response.ok) throw new Error('HTTP error');
            return response.json().catch(() => ({}));
        })
        .then(() => {
            filtrarPorMes();
            mostrarFormulario(null);
            cerrarModal();
            pagoEnEdicion = null;

            new Noty({
                type: 'success',
                layout: 'topRight',
                timeout: 2500,
                theme: 'mint',
                text: 'Editado con éxito'
            }).show();
        })
        .catch(err => console.error("Error real al guardar pago:", err));

    } else {
        let pagos = [];
        if (tipo === "cuotas") {
            const importeCuota = parseFloat((importeTotal / cuotas).toFixed(2));
            let fecha = new Date(vencimiento);

            for (let i = 0; i < cuotas; i++) {
                pagos.push({
                    id: Date.now() + i,
                    rubro: categoria,
                    descripcion: descripcion,
                    importe: importeCuota,
                    tipo: "cuota",
                    cuota_numero: i + 1,
                    cuota_total: cuotas,
                    vencimiento: fecha.toISOString().split('T')[0],
                    pagado: false
                });
                fecha.setMonth(fecha.getMonth() + 1);
            }
        } else {
            pagos.push({
                id: Date.now(),
                rubro: categoria,
                descripcion: descripcion,
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
        .then(response => {
            if (!response.ok) throw new Error('HTTP error');
            return response.json().catch(() => ({}));
        })
        .then(() => {
            filtrarPorMes();
            mostrarFormulario(null);
            cerrarModal();

            new Noty({
                type: 'success',
                layout: 'topRight',
                timeout: 2500,
                theme: 'mint',
                text: 'Pago creado con éxito'
            }).show();
        })
        .catch(err => console.error("Error real al crear pago:", err));
    }
}

// Mostrar formulario
function mostrarFormulario(p = null) {
    if (p) {
        pagoEnEdicion = p;
        document.getElementById('pagoId').value = p.id || '';
        document.getElementById('importe').value = p.importe || '';
        document.getElementById('tipo').value = p.tipo || 'único';
        document.getElementById('cuotas').value = p.cuotas || '';
        document.getElementById('vencimiento').value = p.vencimiento || '';
        document.getElementById('descripcion').value = p.descripcion || '';
        document.querySelector(".btn-cancelar").style.display = "inline";

        let rutaCompleta = p.rubro;
        if (p.descripcion) rutaCompleta += "." + p.descripcion;
        renderSelectoresNiveles(rutaCompleta);

    } else {
        pagoEnEdicion = null;
        document.getElementById('pagoId').value = '';
        document.querySelectorAll('#formulario input, #formulario select').forEach(i => i.value = '');
        const hoy = new Date();
        const yyyy = hoy.getFullYear();
        const mm = String(hoy.getMonth() + 1).padStart(2, '0');
        const dd = String(hoy.getDate()).padStart(2, '0');
        document.getElementById('vencimiento').value = `${yyyy}-${mm}-${dd}`;
        renderSelectoresNiveles();
        document.querySelector(".btn-cancelar").style.display = "none";
    }
}

// Funciones existentes
function cancelar() { mostrarFormulario(null); }
function abrirModal() { const modal = new bootstrap.Modal(document.getElementById('agregarModal')); modal.show(); }
function cerrarModal() { const modal = bootstrap.Modal.getInstance(document.getElementById('agregarModal'))?.hide(); }
function obtenerRutaPadre() {
    const selects = document.querySelectorAll('.nivel-select');
    let ruta = '';
    selects.forEach(sel => { if (sel.value) ruta = sel.value; });
    return ruta;
}
