// estadistica_de_paradas.js
const datos_iniciales = window.datos_iniciales;

const coloresPaleta = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
    '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788',
    '#E74C3C', '#3498DB', '#9B59B6', '#F39C12', '#1ABC9C'
];

function obtenerColor(index) {
    return coloresPaleta[index % coloresPaleta.length];
}

function renderizarGraficos(datos) {
    if (!datos || !datos.categorias || !datos.valores) {
        console.error('Datos inválidos para renderizar');
        return;
    }

    // Gráfico de Torta
    let tortaChart = echarts.init(document.getElementById('graficoTorta'));
    let tortaData = datos.categorias.map((cat, i) => ({
        name: cat,
        value: datos.valores[i],
        itemStyle: { color: obtenerColor(i) }
    }));

    tortaChart.setOption({
        title: {
            text: 'Distribución por Categoría',
            left: 'center',
            top: 20,
            textStyle: { color: 'white', fontSize: 18, fontWeight: 'bold' }
        },
        tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
        legend: {
            orient: 'vertical', right: 10, top: 'center',
            textStyle: { color: 'white' },
            formatter: function(name) {
                return name.length > 25 ? name.substring(0, 25) + '...' : name;
            }
        },
        series: [{
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['40%', '55%'],
            data: tortaData,
            label: { show: true, formatter: '{c}', color: 'white', fontSize: 12, fontWeight: 'bold' },
            labelLine: { show: true, lineStyle: { color: 'white' } },
            itemStyle: {
                borderRadius: 10, borderColor: '#1a1a2e', borderWidth: 3,
                shadowBlur: 10, shadowColor: 'rgba(0, 0, 0, 0.5)'
            },
            emphasis: {
                itemStyle: { shadowBlur: 20, shadowOffsetX: 0, shadowColor: 'rgba(255, 255, 255, 0.5)' }
            }
        }],
        backgroundColor: '#1a1a2e'
    });

    // Gráfico de Barras
    let barraChart = echarts.init(document.getElementById('graficoBarras'));
    barraChart.setOption({
        title: {
            text: 'Cantidad por Categoría',
            left: 'center', top: 20,
            textStyle: { color: 'white', fontSize: 18, fontWeight: 'bold' }
        },
        tooltip: {},
        xAxis: {
            type: 'category',
            data: datos.categorias,
            axisLabel: {
                color: '#fff', fontSize: 10, interval: 0, rotate: 45,
                formatter: function(value) {
                    return value.length > 15 ? value.substring(0, 15) + '...' : value;
                }
            },
            axisLine: { lineStyle: { color: '#fff' } }
        },
        yAxis: {
            type: 'value',
            axisLabel: { color: '#fff' },
            axisLine: { lineStyle: { color: '#fff' } }
        },
        series: [{
            type: 'bar',
            data: datos.valores,
            itemStyle: {
                color: function(params) { return obtenerColor(params.dataIndex); },
                borderRadius: [4, 4, 0, 0]
            },
            label: {
                show: true, position: 'top', color: '#fff',
                fontSize: 12, fontWeight: 'bold'
            }
        }],
        backgroundColor: '#1a1a2e'
    });

    window.addEventListener('resize', function() {
        tortaChart.resize();
        barraChart.resize();
    });
}

// Renderizar gráficos iniciales
renderizarGraficos(datos_iniciales);

// Cargar archivo
if (document.getElementById('archivoInput')) {
    document.getElementById('archivoInput').addEventListener('change', function(e) {
        const archivo = e.target.files[0];
        if (!archivo) return;
        document.getElementById('nombreArchivo').textContent = `Archivo: ${archivo.name}`;
        const formData = new FormData();
        formData.append('archivo', archivo);

        fetch('/estadistica_de_paradas/cargar_archivo', { method: 'POST', body: formData })
            .then(resp => {
                if (!resp.ok) throw new Error('Error en la respuesta del servidor');
                return resp.json();
            })
            .then(data => {
                if (data.error) { alert('Error: ' + data.error); return; }
                renderizarGraficos({ categorias: data.categorias, valores: data.valores });
                if (data.rango_fechas && data.rango_fechas.min && data.rango_fechas.max) {
                    document.getElementById('fechaInicio').value = convertirFecha(data.rango_fechas.min);
                    document.getElementById('fechaFin').value = convertirFecha(data.rango_fechas.max);
                    document.getElementById('fechaInicio').min = convertirFecha(data.rango_fechas.min);
                    document.getElementById('fechaInicio').max = convertirFecha(data.rango_fechas.max);
                    document.getElementById('fechaFin').min = convertirFecha(data.rango_fechas.min);
                    document.getElementById('fechaFin').max = convertirFecha(data.rango_fechas.max);
                }
                alert(`✓ Archivo cargado!\nTotal: ${data.total_avisos}`);
            })
            .catch(err => {
                console.error('Error al cargar archivo:', err);
                alert('Error al cargar el archivo.');
            });
    });
}

// Filtro por columna
if (document.getElementById('columnaSelect')) {
    document.getElementById('columnaSelect').addEventListener('change', function() {
        const seleccion = this.value;
        const fechaInicio = document.getElementById('fechaInicio').value;
        const fechaFin = document.getElementById('fechaFin').value;
        let url = `/estadistica_de_paradas/datos?columna=${encodeURIComponent(seleccion)}`;
        if (fechaInicio) url += `&fecha_inicio=${convertirFechaInversa(fechaInicio)}`;
        if (fechaFin) url += `&fecha_fin=${convertirFechaInversa(fechaFin)}`;

        fetch(url)
            .then(resp => resp.json())
            .then(datos => renderizarGraficos(datos))
            .catch(err => console.error('Error al cargar datos:', err));
    });
}

// Filtrar por fechas
document.getElementById('btnFiltrarFechas').addEventListener('click', function() {
    const fechaInicio = document.getElementById('fechaInicio').value;
    const fechaFin = document.getElementById('fechaFin').value;
    if (!fechaInicio || !fechaFin) { alert('Selecciona ambas fechas'); return; }
    const columna = document.getElementById('columnaSelect').value;
    let url = `/estadistica_de_paradas/datos?columna=${columna}&fecha_inicio=${convertirFechaInversa(fechaInicio)}&fecha_fin=${convertirFechaInversa(fechaFin)}`;
    fetch(url)
        .then(resp => resp.json())
        .then(datos => renderizarGraficos(datos))
        .catch(err => console.error('Error:', err));
});

// Limpiar filtros
document.getElementById('btnLimpiarFechas').addEventListener('click', function() {
    if (window.rango_fechas && window.rango_fechas.min && window.rango_fechas.max) {
        document.getElementById('fechaInicio').value = convertirFecha(window.rango_fechas.min);
        document.getElementById('fechaFin').value = convertirFecha(window.rango_fechas.max);
    }
    const columna = document.getElementById('columnaSelect').value;
    fetch(`/estadistica_de_paradas/datos?columna=${columna}`)
        .then(resp => resp.json())
        .then(datos => renderizarGraficos(datos));
});

// Exportar a PDF
if (document.getElementById('exportarPdf')) {
    document.getElementById('exportarPdf').addEventListener('click', () => {
        const graficoDiv = document.getElementById('grafico');
        html2canvas(graficoDiv, { backgroundColor: '#370d60', scale: 2 }).then(canvas => {
            const imgData = canvas.toDataURL('image/png');
            const { jsPDF } = window.jspdf;
            const pdf = new jsPDF({
                orientation: 'landscape',
                unit: 'px',
                format: [canvas.width / 2 + 60, canvas.height / 2 + 100]
            });
            pdf.setFontSize(22);
            pdf.setTextColor(255, 255, 255);
            pdf.setFillColor(55, 13, 96);
            pdf.rect(0, 0, pdf.internal.pageSize.width, pdf.internal.pageSize.height, 'F');
            pdf.text('Estadística de Paradas', 30, 40);
            pdf.setFontSize(12);
            const columnaSeleccionada = document.getElementById('columnaSelect').value;
            pdf.text(`Agrupado por: ${columnaSeleccionada.replace('_', ' ')}`, 30, 60);
            pdf.text(`Fecha: ${new Date().toLocaleDateString('es-AR')}`, 30, 75);
            pdf.addImage(imgData, 'PNG', 30, 90, canvas.width / 2, canvas.height / 2);
            pdf.save(`estadistica_paradas_${new Date().toISOString().split('T')[0]}.pdf`);
        }).catch(err => {
            console.error('Error al generar PDF:', err);
            alert('Error al generar el PDF.');
        });
    });
}

// Drilldown en gráfico de torta
const graficoTortaElement = document.getElementById('graficoTorta');
if (graficoTortaElement) {
    const tortaChartInstance = echarts.getInstanceByDom(graficoTortaElement);
    if (tortaChartInstance) {
        tortaChartInstance.on('click', function(params) {
            const columnaFiltro = document.getElementById('columnaSelect').value;
            mostrarModalDrillDown(params.name, columnaFiltro);
        });
    }
}

function mostrarModalDrillDown(categoria, columnaFiltro) {
    let modal = document.getElementById('modalDrillDown');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'modalDrillDown';
        modal.className = 'modal-drilldown';
        modal.innerHTML = `
            <div class="modal-content-drilldown">
                <div class="modal-header-drilldown">
                    <h2 id="modalTitulo">Detalle</h2>
                    <button class="btn-cerrar-modal" onclick="cerrarModal()">&times;</button>
                </div>
                <div class="modal-body-drilldown">
                    <div id="graficoModal" style="width: 100%; height: 500px;"></div>
                </div>
            </div>`;
        document.body.appendChild(modal);
    }
    document.getElementById('modalTitulo').textContent = `Detalle: ${categoria}`;
    modal.style.display = 'flex';

    const fechaInicio = document.getElementById('fechaInicio').value;
    const fechaFin = document.getElementById('fechaFin').value;
    let url = `/estadistica_de_paradas/drilldown?categoria=${encodeURIComponent(categoria)}&columna=${encodeURIComponent(columnaFiltro)}`;
    if (fechaInicio) url += `&fecha_inicio=${convertirFechaInversa(fechaInicio)}`;
    if (fechaFin) url += `&fecha_fin=${convertirFechaInversa(fechaFin)}`;

    fetch(url)
        .then(resp => resp.json())
        .then(datos => {
            let modalChart = echarts.init(document.getElementById('graficoModal'));
            let tortaData = datos.categorias.map((cat, i) => ({
                name: cat, value: datos.valores[i],
                itemStyle: { color: obtenerColor(i) }
            }));
            modalChart.setOption({
                title: { text: `Desglose de: ${categoria}`, left: 'center', textStyle: { color: '#333', fontSize: 16 } },
                tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
                legend: { orient: 'vertical', right: 10, top: 'center' },
                series: [{
                    type: 'pie', radius: ['30%', '60%'],
                    data: tortaData,
                    label: { show: true, formatter: '{b}: {c}' }
                }],
                backgroundColor: '#f5f5f5'
            });
            modalChart.on('click', function(params) {
                const columnaSecundaria = columnaFiltro === 'Texto_codigo' ? 'Ubicac_tecnica' : 'Texto_codigo';
                mostrarTablaDetalle(categoria, params.name, columnaFiltro, columnaSecundaria);
            });
        });
}

function mostrarTablaDetalle(catPrincipal, catSecundaria, colPrincipal, colSecundaria) {
    let modalTabla = document.getElementById('modalTabla');
    if (!modalTabla) {
        modalTabla = document.createElement('div');
        modalTabla.id = 'modalTabla';
        modalTabla.className = 'modal-drilldown';
        modalTabla.innerHTML = `
            <div class="modal-content-drilldown modal-tabla">
                <div class="modal-header-drilldown">
                    <h2 id="modalTituloTabla">Registros Detallados</h2>
                    <button class="btn-cerrar-modal" onclick="cerrarModalTabla()">&times;</button>
                </div>
                <div class="modal-body-drilldown">
                    <div style="display: flex; gap: 20px; margin-bottom: 15px; flex-wrap: wrap;">
                        <div id="contadorRegistros"></div>
                        <div id="totalDemoras"></div>
                    </div>
                    <div style="overflow-x: auto;">
                        <table id="tablaDetalle" class="tabla-detalle">
                            <thead id="tablaHead"></thead>
                            <tbody id="tablaBody"></tbody>
                        </table>
                    </div>
                </div>
            </div>`;
        document.body.appendChild(modalTabla);
    }
    document.getElementById('modalTituloTabla').textContent = `${catPrincipal} → ${catSecundaria}`;
    modalTabla.style.display = 'flex';

    const fechaInicio = document.getElementById('fechaInicio').value;
    const fechaFin = document.getElementById('fechaFin').value;
    let url = `/estadistica_de_paradas/detalle?categoria_principal=${encodeURIComponent(catPrincipal)}&categoria_secundaria=${encodeURIComponent(catSecundaria)}&columna_principal=${encodeURIComponent(colPrincipal)}&columna_secundaria=${encodeURIComponent(colSecundaria)}`;
    if (fechaInicio) url += `&fecha_inicio=${convertirFechaInversa(fechaInicio)}`;
    if (fechaFin) url += `&fecha_fin=${convertirFechaInversa(fechaFin)}`;

    fetch(url)
        .then(resp => resp.json())
        .then(datos => {
            document.getElementById('contadorRegistros').textContent = `Total de registros: ${datos.total}`;
            let totalHoras = 0;
            datos.registros.forEach(reg => {
                totalHoras += parseFloat(reg.DurParada || 0);
            });
            const horas = Math.floor(totalHoras);
            const minutos = Math.round((totalHoras - horas) * 60);
            document.getElementById('totalDemoras').textContent =
                `Total demoras: ${String(horas).padStart(2, '0')}:${String(minutos).padStart(2, '0')} Hs`;

            if (datos.registros.length === 0) {
                document.getElementById('tablaBody').innerHTML = '<tr><td colspan="12" style="text-align:center;">No hay datos</td></tr>';
                return;
            }
            const columnas = ['Aviso', 'Fecha', 'Descripcion', 'Equipo', 'Ubicac_tecnica', 'DurParada', 'Aut_aviso', 'Por', 'Orden', 'Fin_desead', 'Texto_codigo'];
            document.getElementById('tablaHead').innerHTML = '<tr>' + columnas.map(col => `<th>${col.replace('_', ' ')}</th>`).join('') + '</tr>';
            document.getElementById('tablaBody').innerHTML = datos.registros.map(reg =>
                '<tr>' + columnas.map(col => `<td>${reg[col] || ''}</td>`).join('') + '</tr>'
            ).join('');
        })
        .catch(err => {
            console.error('Error al cargar detalle:', err);
            alert('Error al cargar los datos detallados.');
        });
}

function cerrarModal() {
    const modal = document.getElementById('modalDrillDown');
    if (modal) modal.style.display = 'none';
}

function cerrarModalTabla() {
    const modal = document.getElementById('modalTabla');
    if (modal) modal.style.display = 'none';
}

window.onclick = function(event) {
    const modal = document.getElementById('modalDrillDown');
    if (event.target === modal) cerrarModal();
    const modalTabla = document.getElementById('modalTabla');
    if (event.target === modalTabla) cerrarModalTabla();
};

// Configurar rangos de fechas iniciales
if (window.rango_fechas && window.rango_fechas.min && window.rango_fechas.max) {
    document.getElementById('fechaInicio').value = convertirFecha(window.rango_fechas.min);
    document.getElementById('fechaFin').value = convertirFecha(window.rango_fechas.max);
    document.getElementById('fechaInicio').min = convertirFecha(window.rango_fechas.min);
    document.getElementById('fechaInicio').max = convertirFecha(window.rango_fechas.max);
    document.getElementById('fechaFin').min = convertirFecha(window.rango_fechas.min);
    document.getElementById('fechaFin').max = convertirFecha(window.rango_fechas.max);
}

// Utilidades de fechas
function convertirFecha(fecha) {
    if (!fecha) return '';
    const partes = fecha.split('.');
    if (partes.length === 3) return `${partes[2]}-${partes[1]}-${partes[0]}`;
    return fecha;
}

function convertirFechaInversa(fecha) {
    if (!fecha) return '';
    const partes = fecha.split('-');
    if (partes.length === 3) return `${partes[2]}.${partes[1]}.${partes[0]}`;
    return fecha;
}