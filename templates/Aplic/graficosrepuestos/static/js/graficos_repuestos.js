// templates/Aplic/graficosrepuestos/static/js/graficos_repuestos.js
/**
 * Gráficos de Repuestos por Estado
 * Barras 2D (confiable) + Torta
 */

const datos_iniciales = window.datos_iniciales;

const colorEstado = {
    "Disponible": "#4CAF50",
    "En espera": "#FFEB3B",
    "No disponible": "#F44336",
    "Sin código": "#FF9800",
    "Descontinuado": "#9C27B0",
    "Actualizar código": "#2196F3",
    "Otros": "#9E9E9E"
};

let tortaChart = null;
let barraChart = null;

function renderizarGraficos(datos) {
    if (!datos || !datos.categorias || !datos.valores || datos.categorias.length === 0) {
        console.warn('No hay datos para graficar');
        return;
    }

    // ===== TORTA =====
    const elTorta = document.getElementById('graficoTorta');
    if (!elTorta) return;

    if (tortaChart) tortaChart.dispose();
    tortaChart = echarts.init(elTorta);

    const tortaData = datos.categorias.map((cat, i) => ({
        name: cat,
        value: datos.valores[i],
        itemStyle: { color: colorEstado[cat] || '#9E9E9E' }
    }));

    tortaChart.setOption({
        title: {
            text: 'Repuestos por Estado',
            left: 'center',
            textStyle: { color: 'white' }
        },
        tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
        series: [{
            type: 'pie',
            roseType: 'radius',
            radius: ['30%', '70%'],
            data: tortaData,
            label: { color: 'white', fontSize: 14 },
            itemStyle: {
                borderRadius: 8,
                borderColor: '#111',
                borderWidth: 2
            }
        }],
        backgroundColor: '#111'
    });

    // ===== BARRAS 2D =====
    const elBarras = document.getElementById('graficoBarras');
    if (!elBarras) return;

    if (barraChart) barraChart.dispose();
    barraChart = echarts.init(elBarras);

    const barrasData = datos.valores.map((val, i) => ({
        value: val,
        itemStyle: { color: colorEstado[datos.categorias[i]] || '#9E9E9E' }
    }));

    barraChart.setOption({
        title: {
            text: 'Cantidad por Estado',
            left: 'center',
            textStyle: { color: 'white' }
        },
        tooltip: {
            trigger: 'axis',
            formatter: function (params) {
                return params[0].name + ': ' + params[0].value;
            }
        },
        xAxis: {
            type: 'category',
            data: datos.categorias,
            axisLabel: {
                color: '#fff',
                fontSize: 10,
                interval: 0,
                rotate: 35,
                formatter: function (value) {
                    return value.length > 12 ? value.substring(0, 12) + '…' : value;
                }
            },
            axisLine: { lineStyle: { color: '#555' } }
        },
        yAxis: {
            type: 'value',
            axisLabel: { color: '#fff' },
            axisLine: { lineStyle: { color: '#555' } },
            splitLine: { lineStyle: { color: '#333' } }
        },
        series: [{
            type: 'bar',
            data: barrasData,
            barMaxWidth: 50,
            label: {
                show: true,
                position: 'top',
                color: '#fff',
                fontSize: 12,
                fontWeight: 'bold'
            }
        }],
        backgroundColor: '#111',
        grid: {
            left: '10%',
            right: '5%',
            bottom: '18%',
            top: '15%'
        }
    });

    // Redimensionar al cambiar tamaño de ventana
    window.addEventListener('resize', function () {
        if (tortaChart) tortaChart.resize();
        if (barraChart) barraChart.resize();
    });
}

// ===== FILTRO POR JERARQUÍA =====
document.getElementById('jerarquiaSelect').addEventListener('change', function () {
    const seleccion = this.value;
    let url = '/graficos_repuestos/datos';
    if (seleccion) url += '?jerarquia=' + encodeURIComponent(seleccion);

    fetch(url)
        .then(resp => resp.json())
        .then(datos => renderizarGraficos(datos))
        .catch(err => console.error('Error al cargar datos:', err));
});

// ===== EXPORTAR PDF =====
document.getElementById('exportarPdf').addEventListener('click', function () {
    const graficoDiv = document.getElementById('grafico');
    html2canvas(graficoDiv, { backgroundColor: '#111', scale: 2 }).then(canvas => {
        const imgData = canvas.toDataURL('image/png');
        const { jsPDF } = window.jspdf;
        const pdf = new jsPDF({
            orientation: 'landscape',
            unit: 'px',
            format: [canvas.width / 2 + 60, canvas.height / 2 + 100]
        });

        pdf.setFontSize(20);
        pdf.setTextColor(255, 255, 255);
        pdf.setFillColor(17, 17, 17);
        pdf.rect(0, 0, pdf.internal.pageSize.width, pdf.internal.pageSize.height, 'F');
        pdf.text('Gráficos de Repuestos por Estado', 30, 40);
        pdf.setFontSize(12);
        pdf.text('Fecha: ' + new Date().toLocaleDateString('es-AR'), 30, 60);
        pdf.addImage(imgData, 'PNG', 30, 80, canvas.width / 2, canvas.height / 2);
        pdf.save('graficos_repuestos.pdf');
    }).catch(err => {
        console.error('Error al generar PDF:', err);
    });
});

// ===== RENDER INICIAL =====
renderizarGraficos(datos_iniciales);