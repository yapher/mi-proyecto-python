/**
* JavaScript para el componente Pagos
* Maneja la funcionalidad de gestión de pagos y filtros
*/
// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    // Al iniciar la página, establecer año y mes actual
    const hoy = new Date();
    const anio = hoy.getFullYear();
    const mes = hoy.getMonth() + 1; // enero = 0
    document.getElementById('filtroAnio').value = anio;
    document.getElementById('filtroMes').value = mes;
    filtrarPorMes();
});

/**
* Carga todos los pagos
*/
function cargarPagos() {
    fetch('/pagos/listar')
    .then(r => r.json())
    .then(data => mostrarPagos(data));
}

/**
* Filtra los pagos por mes y año
*/
function filtrarPorMes() {
    const anio = document.getElementById('filtroAnio').value;
    const mes = document.getElementById('filtroMes').value;
    if (!anio || !mes) return alert("Completar año y mes");
    
    fetch(`/pagos/mensuales/${anio}/${mes}`)
    .then(r => r.json())
    .then(data => {
        mostrarPagos(data.pagos);
        mostrarRubros(data.rubros, data.pagos);
    });
}

/**
* Muestra los pagos en la tabla
* @param {Array} data - Array de pagos
*/
function mostrarPagos(data) {
    const tbody = document.querySelector("#tablaPagos tbody");
    tbody.innerHTML = "";
    data.forEach(p => {
        const icono = p.pagado ? '✔️' : '❌';
        const clase = p.pagado ? 'btn-success' : 'btn-warning';
        // Mostrar tipo como "Cuota X de Y" o "Único"
        let tipoTexto = "Único";
        if (p.tipo === "cuota" && p.cuota_numero && p.cuota_total) {
            tipoTexto = `Cuota ${p.cuota_numero} de ${p.cuota_total}`;
        }
        // Mostrar número de cuotas solo si existen
        let cuotaTexto = p.tipo === "cuota" && p.cuota_total ? `${p.cuota_total}` : "-";
        tbody.innerHTML += `
        <tr>
            <td>${p.rubro}</td>
            <td>${p.descripcion || '-'}</td>
            <td>$${p.importe.toFixed(2)}</td>
            <td>${tipoTexto}</td>
            <td>${cuotaTexto}</td>
            <td>${p.vencimiento}</td>
            <td>
                <button class="btn btn-sm ${clase}" onclick='togglePagado(${p.id})'>${icono}</button>
                <button class="btn btn-sm btn-outline-primary" onclick='editar(${JSON.stringify(p)})'>✏️ Editar</button>
                <button class="btn btn-sm btn-outline-danger" onclick='eliminar(${parseInt(p.id)})'>🗑️ Eliminar</button>
            </td>
        </tr>`;
    });
}

/**
* Cambia el estado de pago de un elemento
* @param {number} id - ID del pago
*/
function toggleEstadoPago(id) {
    fetch(`/pagos/toggle_estado/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(res => res.json())
    .then(data => {
        filtrarPorMes();  // recarga la tabla con el estado actualizado
    })
    .catch(err => {
        console.error("Error al cambiar estado:", err);
        alert("No se pudo actualizar el estado del pago.");
    });
}

/**
* Alterna el estado de pagado de un elemento
* @param {number} id - ID del pago
*/
function togglePagado(id) {
    fetch(`/pagos/toggle_estado/${id}`, {
        method: 'PATCH'
    })
    .then(res => res.json())
    .then(data => {
        filtrarPorMes();
    });
}

/**
* Abre el modal de edición precargado con los datos del pago
* @param {Object} p - Objeto del pago a editar
*/
function editar(p) {
    mostrarFormulario(p);
    abrirModal();
}

/**
* Elimina un pago
* Usa SweetAlert2 para confirmación (mismo patrón que Crear Almacenes)
* @param {number} id - ID del pago
*/
async function eliminar(id) {
    return new Promise((resolve) => {
        Notify.confirm(
            '¿Eliminar este pago?',
            'Esta acción no se puede deshacer',
            () => {
                fetch(`/pagos/eliminar/${id}`, { method: 'DELETE' })
                    .then(res => {
                        if (!res.ok) throw new Error('HTTP error');
                        return res.json();
                    })
                    .then(() => {
                        filtrarPorMes();
                        Notify.success('Pago eliminado');
                    })
                    .catch(err => {
                        console.error("Error al eliminar pago:", err);
                        Notify.error('No se pudo eliminar el pago');
                    });
            }
        );
    });
}

// ============================================================
// CLONAR MES
// ============================================================

/**
* Abre el modal de clonado, sugiriendo el mes siguiente al filtrado
*/
function abrirModalClonar() {
    const anio = document.getElementById('filtroAnio').value;
    const mes = document.getElementById('filtroMes').value;
    if (!anio || !mes) {
        Notify.warning('Primero filtrá el mes que querés clonar');
        return;
    }

    document.getElementById('mesOrigenTexto').textContent = `${String(mes).padStart(2, '0')}/${anio}`;

    let mesDestino = parseInt(mes, 10) + 1;
    let anioDestino = parseInt(anio, 10);
    if (mesDestino > 12) { mesDestino = 1; anioDestino++; }

    document.getElementById('clonarAnioDestino').value = anioDestino;
    document.getElementById('clonarMesDestino').value = mesDestino;

    bootstrap.Modal.getOrCreateInstance(document.getElementById('clonarModal')).show();
}

/**
* Valida los datos, avisa si el destino ya tiene pagos y envía el clonado
*/
async function clonarMes() {
    const anioOrigen = parseInt(document.getElementById('filtroAnio').value, 10);
    const mesOrigen = parseInt(document.getElementById('filtroMes').value, 10);
    const anioDestino = parseInt(document.getElementById('clonarAnioDestino').value, 10);
    const mesDestino = parseInt(document.getElementById('clonarMesDestino').value, 10);

    if (!anioDestino || !mesDestino || mesDestino < 1 || mesDestino > 12) {
        Notify.warning('Completá un año y un mes destino válidos (mes de 1 a 12)');
        return;
    }

    if (anioDestino === anioOrigen && mesDestino === mesOrigen) {
        Notify.warning('El mes destino tiene que ser distinto al mes origen');
        return;
    }

    const btn = document.getElementById('btnConfirmarClonar');
    if (btn) btn.disabled = true;

    try {
        // ¿El destino ya tiene pagos? Clonar dos veces duplicaría todo.
        let existentes = 0;
        try {
            const r = await fetch(`/pagos/mensuales/${anioDestino}/${mesDestino}`, { credentials: 'same-origin' });
            const d = await r.json();
            existentes = (d.pagos || []).length;
        } catch (e) {
            existentes = 0;
        }

        if (existentes > 0) {
            Notify.confirm(
                'El mes destino ya tiene pagos',
                `${String(mesDestino).padStart(2, '0')}/${anioDestino} ya tiene ${existentes} pago(s). ` +
                'Si clonás, se agregarán los del mes origen y pueden quedar duplicados. ¿Continuar?',
                () => ejecutarClonado(anioOrigen, mesOrigen, anioDestino, mesDestino),
                () => { if (btn) btn.disabled = false; }
            );
            return;
        }

        await ejecutarClonado(anioOrigen, mesOrigen, anioDestino, mesDestino);
    } finally {
        // Si se abrió la confirmación, el botón se rehabilita al cancelar o al terminar
        if (btn && !document.querySelector('.swal2-container')) btn.disabled = false;
    }
}

/**
* Envía la solicitud de clonado al backend
*/
async function ejecutarClonado(anioOrigen, mesOrigen, anioDestino, mesDestino) {
    const btn = document.getElementById('btnConfirmarClonar');

    try {
        const res = await fetch('/pagos/clonar_mes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify({
                anio_origen: anioOrigen,
                mes_origen: mesOrigen,
                anio_destino: anioDestino,
                mes_destino: mesDestino
            })
        });

        if (res.redirected) {
            throw new Error('Tu sesión expiró. Volvé a iniciar sesión.');
        }

        let data = {};
        try { data = await res.json(); } catch (e) { /* sin JSON */ }

        if (!res.ok) {
            throw new Error(data.error || data.msg || `Error del servidor (HTTP ${res.status})`);
        }

        const modalEl = document.getElementById('clonarModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();

        Notify.success(data.mensaje || 'Mes clonado correctamente');

        // Mostrar el mes destino para ver el resultado
        document.getElementById('filtroAnio').value = anioDestino;
        document.getElementById('filtroMes').value = mesDestino;
        filtrarPorMes();
    } catch (err) {
        console.error('Error al clonar mes:', err);
        Notify.error(err.message || 'No se pudo clonar el mes');
    } finally {
        if (btn) btn.disabled = false;
    }
}