// graficos_repuestos.js

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

function renderizarGraficos(datos) {
    // Torta 3D
    let tortaChart = echarts.init(document.getElementById('graficoTorta'));
    let tortaData = datos.categorias.map((cat, i) => ({
        name: cat,
        value: datos.valores[i],
        itemStyle: { color: colorEstado[cat] || '#9E9E9E' }
    }));

    let tortaOption = {
        title: {
            text: 'Repuestos por Estado (Torta 3D)',
            left: 'center',
            textStyle: { color: 'white' }
        },
        tooltip: { trigger: 'item' },
        series: [{
            type: 'pie',
            roseType: 'radius',
            radius: ['30%', '70%'],
            data: tortaData,
            label: {
                color: 'white',
                fontSize: 14,
            },
            itemStyle: {
                borderRadius: 8,
                borderColor: '#111',
                borderWidth: 2
            }
        }],
        backgroundColor: '#111'
    };
    tortaChart.setOption(tortaOption);

    // Barras 3D
    let barraChart = echarts.init(document.getElementById('graficoBarras'));
    let barraOption = {
        title: {
            text: 'Repuestos por Estado (Barras 3D)',
            left: 'center',
            textStyle: { color: 'white' }
        },
        tooltip: {},
        xAxis3D: {
            type: 'category',
            data: datos.categorias
        },
        yAxis3D: {
            type: 'category',
            data: ['']
        },
        zAxis3D: {
            type: 'value'
        },
        grid3D: {
            boxWidth: 200,
            boxDepth: 40,
            light: {
                main: { intensity: 1.2 },
                ambient: { intensity: 0.3 }
            },
            viewControl: { alpha: 25, beta: 40 }
        },
        series: [{
            type: 'bar3D',
            data: datos.categorias.map((cat, i) => [cat, '', datos.valores[i]]),
            shading: 'lambert',
            label: {
                show: true,
                formatter: function (params) {
                    return params.value[2];
                },
                textStyle: { color: '#fff' }
            },
            itemStyle: {
                color: function (params) {
                    let cat = datos.categorias[params.dataIndex];
                    return colorEstado[cat] || '#9E9E9E';
                }
            }
        }],
        backgroundColor: '#111'
    };
    barraChart.setOption(barraOption);
}

// Render inicial
renderizarGraficos(datos_iniciales);

// Filtro por jerarquía
if (document.getElementById('jerarquiaSelect')) {
    document.getElementById('jerarquiaSelect').addEventListener('change', function () {
        const seleccion = this.value;
        fetch(`/graficos_repuestos/datos?jerarquia=${encodeURIComponent(seleccion)}`)
            .then(resp => resp.json())
            .then(datos => renderizarGraficos(datos));
    });
}

// Exportar a PDF
if (document.getElementById('exportarPdf')) {
    document.getElementById('exportarPdf').addEventListener('click', () => {
        const graficoDiv = document.getElementById('grafico');
        html2canvas(graficoDiv, { backgroundColor: '#111' }).then(canvas => {
            const imgData = canvas.toDataURL('image/png');
            const { jsPDF } = window.jspdf;
            const pdf = new jsPDF({
                orientation: 'landscape',
                unit: 'px',
                format: [canvas.width + 60, canvas.height + 100]
            });

            // Agregar título y fecha
            pdf.setFontSize(20);
            pdf.text('Gráficos de Repuestos por Estado', 30, 40);
            pdf.setFontSize(12);
            pdf.text(`Fecha: ${new Date().toLocaleDateString()}`, 30, 60);

            pdf.addImage(imgData, 'PNG', 30, 80, canvas.width, canvas.height);
            pdf.save('graficos_repuestos.pdf');
        });
    });
}
