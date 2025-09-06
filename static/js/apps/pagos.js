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
