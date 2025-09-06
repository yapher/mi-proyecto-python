/**
 * JavaScript para el componente Listar OT
 * Maneja la funcionalidad de búsqueda, filtros y gráficos de órdenes de trabajo
 */

// Variable global para el gráfico
let grafico = null;

// Inicialización cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", () => {
    const encabezados = document.querySelectorAll("thead th");
    const selector = document.getElementById("columnaSelector");
    encabezados.forEach((th, i) => {
        const opt = document.createElement("option");
        opt.value = i;
        opt.textContent = th.innerText.trim();
        selector.appendChild(opt);
    });
    const opcionEstado = Array.from(selector.options).find(opt => opt.textContent.toLowerCase() === "estado");
    if (opcionEstado) {
        selector.value = opcionEstado.value;
        generarGrafico();
    }
});

/**
 * Cambia el archivo seleccionado y recarga la página
 */
function cambiarArchivo() {
    const archivo = document.getElementById("archivoSelector").value;
    window.location.href = `/listar_ot?archivo=${archivo}`;
}

/**
 * Busca en las filas de la tabla según el texto ingresado
 */
function buscar() {
    const input = document.getElementById("busqueda").value.toLowerCase();
    const filas = document.querySelectorAll("tbody tr");
    let contador = 0;
    filas.forEach(fila => {
        const texto = fila.innerText.toLowerCase();
        const coincide = texto.includes(input);
        fila.style.display = coincide ? "" : "none";
        if (coincide) contador++;
    });
    document.getElementById("contador-filas").textContent = `Cantidad total de filas: ${contador}`;
}

/**
 * Genera un gráfico de torta basado en la columna seleccionada
 */
function generarGrafico() {
    const tabla = document.querySelector("table");
    if (!tabla) return;
    const indexSeleccionado = document.getElementById("columnaSelector").value;
    if (indexSeleccionado === "") return;

    const filas = tabla.querySelectorAll("tbody tr");
    const conteo = {};
    filas.forEach(fila => {
        let valor = fila.querySelectorAll("td")[indexSeleccionado].innerText.trim();
        const encabezado = document.querySelectorAll("thead th")[indexSeleccionado].innerText.trim().toLowerCase();
        if (encabezado === "numero_orden") {
            valor = valor.substring(0, 4);
        }
        conteo[valor] = (conteo[valor] || 0) + 1;
    });

    const labels = Object.keys(conteo);
    const data = Object.values(conteo);
    const ctx = document.getElementById("graficoTorta").getContext("2d");

    if (grafico) grafico.destroy();
    grafico = new Chart(ctx, {
        type: 'pie',
        data: {
            labels,
            datasets: [{
                data,
                backgroundColor: ['#4caf50', '#f44336', '#2196f3', '#ff9800', '#9c27b0', '#00bcd4', '#795548', '#607d8b', '#ffc107']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right', labels: { color: '#fff' } },
                datalabels: {
                    color: '#fff',
                    formatter: (value, ctx) =>
                        (value / ctx.dataset.data.reduce((a, b) => a + b) * 100).toFixed(1) + '%',
                    font: { weight: 'bold', size: 14 }
                }
            },
            onClick: (evt, elements) => {
                if (elements.length > 0) {
                    const index = elements[0].index;
                    const grupo = labels[index];
                    abrirModal(grupo);
                }
            }
        },
        plugins: [ChartDataLabels]
    });
}

/**
 * Abre un modal con información filtrada del grupo seleccionado
 * @param {string} grupo - Grupo seleccionado en el gráfico
 */
function abrirModal(grupo) {
    const indexSeleccionado = document.getElementById("columnaSelector").value;
    const encabezado = document.querySelectorAll("thead th")[indexSeleccionado].innerText.trim();
    const archivo = document.getElementById("archivoSelector").value;

    fetch(`/filtro_torta/${encodeURIComponent(encabezado)}/${encodeURIComponent(grupo)}?archivo=${archivo}`)
        .then(res => res.text())
        .then(html => {
            document.getElementById("modalContainer").innerHTML = html;
            const modal = new bootstrap.Modal(document.getElementById("filtroTortaModal"));
            modal.show();
        });
}
