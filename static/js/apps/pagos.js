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
 * @param {number} id - ID del pago
 */
function eliminar(id) {
    if (!confirm("¿Seguro que querés eliminar este pago?")) return;

    fetch(`/pagos/eliminar/${id}`, {
        method: 'DELETE'
    })
        .then(res => {
            if (!res.ok) throw new Error('HTTP error');
            return res.json();
        })
        .then(() => {
            filtrarPorMes();
            new Noty({
                type: 'success',
                layout: 'topRight',
                timeout: 2500,
                theme: 'mint',
                text: 'Pago eliminado'
            }).show();
        })
        .catch(err => {
            console.error("Error al eliminar pago:", err);
            alert("No se pudo eliminar el pago.");
        });
}

/**
 * Abre el modal de clonado, sugiriendo el mes siguiente al filtrado
 */
function abrirModalClonar() {
    const anio = document.getElementById('filtroAnio').value;
    const mes = document.getElementById('filtroMes').value;

    if (!anio || !mes) return alert("Primero filtrá un mes para clonar");

    document.getElementById('mesOrigenTexto').textContent = `${mes}/${anio}`;

    let mesDestino = parseInt(mes) + 1;
    let anioDestino = parseInt(anio);
    if (mesDestino > 12) { mesDestino = 1; anioDestino++; }

    document.getElementById('clonarAnioDestino').value = anioDestino;
    document.getElementById('clonarMesDestino').value = mesDestino;

    new bootstrap.Modal(document.getElementById('clonarModal')).show();
}

/**
 * Envía la solicitud de clonado al backend
 */
function clonarMes() {
    const anioOrigen = document.getElementById('filtroAnio').value;
    const mesOrigen = document.getElementById('filtroMes').value;
    const anioDestino = document.getElementById('clonarAnioDestino').value;
    const mesDestino = document.getElementById('clonarMesDestino').value;

    if (!anioDestino || !mesDestino) return alert('Completar año y mes destino');

    fetch('/pagos/clonar_mes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            anio_origen: anioOrigen,
            mes_origen: mesOrigen,
            anio_destino: anioDestino,
            mes_destino: mesDestino
        })
    })
    .then(res => res.json().then(data => ({ ok: res.ok, data })))
    .then(({ ok, data }) => {
        if (!ok) throw new Error(data.error || 'Error al clonar');

        bootstrap.Modal.getInstance(document.getElementById('clonarModal')).hide();
        new Noty({
            type: 'success',
            layout: 'topRight',
            timeout: 3000,
            theme: 'mint',
            text: data.mensaje
        }).show();

        if (parseInt(anioDestino) === parseInt(document.getElementById('filtroAnio').value) &&
            parseInt(mesDestino) === parseInt(document.getElementById('filtroMes').value)) {
            filtrarPorMes();
        }
    })
    .catch(err => {
        console.error(err);
        alert(err.message);
    });
}