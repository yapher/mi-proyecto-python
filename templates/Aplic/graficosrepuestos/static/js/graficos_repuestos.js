// templates/Aplic/graficosrepuestos/static/js/graficos_repuestos.js
/**
 * Gráficos de Repuestos por Estado
 * ✅ Barras 2D + Torta con clic → modal de detalle
 * ✅ Exportar gráficos completos a PDF
 * ✅ Reutiliza Logger y Notify globales
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
let modalDetalle = null;

// ============================================================
// INICIALIZACIÓN
// ============================================================

document.addEventListener('DOMContentLoaded', function () {
    Logger.moduleInit('GraficosRepuestos');

    // Inicializar modal Bootstrap
    const modalEl = document.getElementById('modalDetalleEstado');
    if (modalEl) {
        modalDetalle = new bootstrap.Modal(modalEl);
    }

    renderizarGraficos(datos_iniciales);
    Logger.success('Módulo GraficosRepuestos inicializado');
});

// ============================================================
// RENDERIZAR GRÁFICOS
// ============================================================

function renderizarGraficos(datos) {
    if (!datos || !datos.categorias || !datos.valores || datos.categorias.length === 0) {
        Logger.warn('No hay datos para graficar');
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

    // ✅ Clic en segmento de torta → abrir modal
    tortaChart.on('click', function (params) {
        if (params.name) {
            abrirModalDetalle(params.name);
        }
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

    // ✅ Clic en barra → abrir modal
    barraChart.on('click', function (params) {
        if (params.name) {
            abrirModalDetalle(params.name);
        }
    });

    // Redimensionar al cambiar tamaño de ventana
    window.addEventListener('resize', function () {
        if (tortaChart) tortaChart.resize();
        if (barraChart) barraChart.resize();
    });
}

// ============================================================
// ✅ NUEVO: ABRIR MODAL CON DETALLE DE REPUESTOS
// ============================================================

async function abrirModalDetalle(estado) {
    if (!modalDetalle) {
        Logger.error('Modal de detalle no encontrado');
        return;
    }

    Logger.info('Abriendo detalle de estado', { estado });

    // Mostrar spinner mientras carga
    const contenido = document.getElementById('modalDetalleContenido');
    contenido.innerHTML = `
        <div class="modal-body text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-3 text-white">Cargando repuestos de "${estado}"...</p>
        </div>
    `;
    modalDetalle.show();

    try {
        const url = `/graficos_repuestos/detalle/${encodeURIComponent(estado)}`;
        Logger.apiCall('GET', url);

        const res = await fetch(url, { credentials: 'same-origin' });
        Logger.apiResponse('GET', url, res.status);

        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const html = await res.text();
        contenido.innerHTML = html;

        Logger.success('Detalle cargado', { estado });
    } catch (err) {
        Logger.error('Error cargando detalle', err);
        contenido.innerHTML = `
            <div class="modal-body text-center py-5">
                <i class="bi bi-exclamation-triangle" style="font-size: 3rem; color: #dc3545;"></i>
                <p class="mt-3 text-danger">Error al cargar los repuestos</p>
                <button class="btn btn-cancelar" data-bs-dismiss="modal">Cerrar</button>
            </div>
        `;
        Notify.error('No se pudieron cargar los repuestos');
    }
}

// ============================================================
// ✅ NUEVO: Filtrar tabla dentro del modal
// ============================================================

function filtrarTablaModal(input) {
    const filtro = input.value.toLowerCase().trim();
    const tabla = document.getElementById('tablaDetalleEstado');
    if (!tabla) return;

    const filas = tabla.querySelectorAll('tbody tr');
    filas.forEach(fila => {
        const texto = fila.textContent.toLowerCase();
        fila.style.display = texto.includes(filtro) ? '' : 'none';
    });
}

// ============================================================
// ✅ NUEVO: Ampliar imagen en mini-modal
// ============================================================

function abrirModalImagen(src, nombre) {
    const modalEl = document.getElementById('modalImagenAmpliada');
    if (!modalEl) return;

    document.getElementById('imagenAmpliada').src = src;
    document.getElementById('tituloImagenAmpliada').textContent = nombre || '';

    const modal = new bootstrap.Modal(modalEl);
    modal.show();
}

// Hacer funciones accesibles globalmente (para onclick en HTML)
window.filtrarTablaModal = filtrarTablaModal;
window.abrirModalImagen = abrirModalImagen;

// ============================================================
// FILTRO POR JERARQUÍA (existente)
// ============================================================

document.addEventListener('DOMContentLoaded', function () {
    const select = document.getElementById('jerarquiaSelect');
    if (select) {
        select.addEventListener('change', function () {
            const seleccion = this.value;
            let url = '/graficos_repuestos/datos';
            if (seleccion) url += '?jerarquia=' + encodeURIComponent(seleccion);
            fetch(url)
                .then(resp => resp.json())
                .then(datos => renderizarGraficos(datos))
                .catch(err => {
                    Logger.error('Error al cargar datos filtrados', err);
                    Notify.error('Error al filtrar los datos');
                });
        });
    }

    // ============================================================
    // EXPORTAR GRÁFICOS COMPLETOS A PDF (existente)
    // ============================================================

    const btnExportar = document.getElementById('exportarPdf');
    if (btnExportar) {
        btnExportar.addEventListener('click', function () {
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
                Notify.success('PDF de gráficos exportado');
            }).catch(err => {
                Logger.error('Error al generar PDF de gráficos', err);
                Notify.error('Error al generar el PDF');
            });
        });
    }
});