/**
 * graficos_repuestos.js
 * Renderiza gráficos de repuestos por estado usando ECharts.
 * - Sin scripts inline: lee datos desde data-attributes.
 * - Sin doble carga de ECharts: usa la versión del layout.
 * - Usa AppModal para drilldown.
 * - Usa PdfExporter para exportar.
 * - Usa Logger y Notify reutilizables.
 */
(function () {
    'use strict';

    if (window.__graficosRepuestosInitialized) return;
    window.__graficosRepuestosInitialized = true;

    const Logger = window.Logger || {
        moduleInit: function () {},
        info: function () {},
        warn: function () {},
        error: function () {},
        success: function () {},
        apiCall: function () {},
        apiResponse: function () {}
    };

    const Notify = window.Notify || {
        success: function () {},
        error: function (msg) { console.error(msg); },
        warning: function (msg) { console.warn(msg); }
    };

    // ============================================================
    // PALETA DE COLORES (fallback si ChartPalette no está cargado)
    // ============================================================
    const PALETA_FALLBACK = [
        '#2ecc71', '#e74c3c', '#f1c40f', '#3498db', '#9b59b6',
        '#e67e22', '#1abc9c', '#fd79a8', '#00b894', '#6c5ce7',
        '#fdcb6e', '#74b9ff', '#a29bfe', '#ff7675', '#55efc4', '#ffeaa7'
    ];

    function getColor(categoria, index) {
        if (window.ChartPalette && typeof window.ChartPalette.getColor === 'function') {
            return window.ChartPalette.getColor(categoria, index);
        }
        return PALETA_FALLBACK[index % PALETA_FALLBACK.length];
    }

    // ============================================================
    // ESTADO
    // ============================================================
    let tortaChart = null;
    let barraChart = null;
    let ultimoEstadoModal = '';
    let datosIniciales = null;

    // ============================================================
    // HELPERS
    // ============================================================
    function getCurrentJerarquia() {
        const select = document.getElementById('jerarquiaSelect');
        return select ? String(select.value || '').trim() : '';
    }

    function actualizarUrlFiltro(jerarquia) {
        try {
            const url = new URL(window.location.href);
            if (jerarquia) {
                url.searchParams.set('jerarquia', jerarquia);
            } else {
                url.searchParams.delete('jerarquia');
            }
            window.history.replaceState({}, '', url);
        } catch (e) {
            Logger.warn('No se pudo actualizar la URL con el filtro', e);
        }
    }

    function actualizarLinkExportar(container, jerarquia) {
        if (!container) return;
        const links = container.querySelectorAll(
            'a[href*="/graficos_repuestos/exportar_pdf_estado/"]'
        );
        links.forEach(function (link) {
            const href = link.getAttribute('href') || '';
            try {
                const url = new URL(href, window.location.origin);
                if (jerarquia) {
                    url.searchParams.set('jerarquia', jerarquia);
                } else {
                    url.searchParams.delete('jerarquia');
                }
                link.setAttribute('href', url.pathname + (url.search || ''));
            } catch (e) {
                if (jerarquia) {
                    const sep = href.indexOf('?') === -1 ? '?' : '&';
                    link.setAttribute('href', href + sep + 'jerarquia=' + encodeURIComponent(jerarquia));
                }
            }
        });
    }

    function configurarResize() {
        window.addEventListener('resize', function () {
            if (tortaChart) tortaChart.resize();
            if (barraChart) barraChart.resize();
        });
    }

    function handleChartClick(params) {
        let nombre = '';
        if (params && params.name) {
            nombre = params.name;
        } else if (params && Array.isArray(params.value) && params.value.length) {
            nombre = params.value[0];
        }
        if (nombre) {
            window.abrirModalDetalle(nombre, getCurrentJerarquia());
        }
    }

    // ============================================================
    // RENDERIZADO DE GRÁFICOS
    // ============================================================
    function renderizarGraficos(datos) {
        if (typeof echarts === 'undefined') {
            Logger.error('ECharts no está disponible en el window.');
            Notify.error('No se pudo cargar la librería de gráficos (ECharts).');
            return;
        }

        if (!datos || !Array.isArray(datos.categorias) || !Array.isArray(datos.valores) || datos.categorias.length === 0) {
            Logger.warn('No hay datos válidos para graficar.', datos);
            if (tortaChart) { tortaChart.dispose(); tortaChart = null; }
            if (barraChart) { barraChart.dispose(); barraChart = null; }
            return;
        }

        const categorias = datos.categorias.map(function (c) { return String(c || ''); });
        const valores = datos.valores.map(function (v) { return Number(v || 0); });

        // ===================== TORTA =====================
        const elTorta = document.getElementById('graficoTorta');
        if (elTorta) {
            if (tortaChart) tortaChart.dispose();
            tortaChart = echarts.init(elTorta);

            const tortaData = categorias.map(function (cat, i) {
                return {
                    name: cat,
                    value: valores[i] || 0,
                    itemStyle: {
                        color: getColor(cat, i),
                        borderColor: '#111',
                        borderWidth: 2,
                        borderRadius: 8
                    }
                };
            });

            tortaChart.setOption({
                title: {
                    text: 'Repuestos por Estado',
                    left: 'center',
                    textStyle: { color: '#88c999', fontSize: 18, fontWeight: 'bold' }
                },
                tooltip: {
                    trigger: 'item',
                    formatter: '{b}: {c} ({d}%)',
                    backgroundColor: 'rgba(62, 45, 89, 0.95)',
                    borderColor: '#88c999',
                    textStyle: { color: '#fff' }
                },
                legend: {
                    orient: window.innerWidth < 768 ? 'horizontal' : 'vertical',
                    right: window.innerWidth < 768 ? 'center' : 10,
                    bottom: window.innerWidth < 768 ? 0 : 'auto',
                    top: window.innerWidth < 768 ? 'auto' : 'center',
                    textStyle: { color: '#fff', fontSize: window.innerWidth < 480 ? 9 : 11 },
                    formatter: function (name) {
                        return name.length > 20 ? name.substring(0, 20) + '…' : name;
                    }
                },
                series: [{
                    type: 'pie',
                    roseType: 'radius',
                    radius: ['30%', '70%'],
                    center: window.innerWidth < 768 ? ['50%', '45%'] : ['40%', '55%'],
                    data: tortaData,
                    label: {
                        show: window.innerWidth >= 480,
                        color: '#fff',
                        fontSize: 12,
                        fontWeight: 'bold',
                        formatter: '{c}'
                    },
                    labelLine: {
                        show: window.innerWidth >= 480,
                        lineStyle: { color: '#88c999' }
                    },
                    itemStyle: {
                        borderRadius: 10,
                        borderColor: '#1a1a2e',
                        borderWidth: 3
                    },
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 20,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }],
                backgroundColor: 'transparent'
            });

            tortaChart.off('click');
            tortaChart.on('click', handleChartClick);
        }

        // ===================== BARRAS =====================
        const elBarras = document.getElementById('graficoBarras');
        if (elBarras) {
            if (barraChart) barraChart.dispose();
            barraChart = echarts.init(elBarras);

            const barrasData = categorias.map(function (cat, i) {
                return { name: cat, value: valores[i] || 0 };
            });

            barraChart.setOption({
                title: {
                    text: 'Cantidad por Estado',
                    left: 'center',
                    textStyle: { color: '#88c999', fontSize: 18, fontWeight: 'bold' }
                },
                tooltip: {
                    trigger: 'axis',
                    axisPointer: { type: 'shadow' },
                    backgroundColor: 'rgba(62, 45, 89, 0.95)',
                    borderColor: '#88c999',
                    textStyle: { color: '#fff' }
                },
                xAxis: {
                    type: 'category',
                    data: categorias,
                    axisLabel: {
                        color: '#fff',
                        interval: 0,
                        rotate: window.innerWidth < 768 ? 45 : 30,
                        fontSize: window.innerWidth < 480 ? 9 : 11,
                        formatter: function (value) {
                            var text = String(value || '');
                            return text.length > 12 ? text.substring(0, 12) + '…' : text;
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
                    itemStyle: {
                        color: function (params) {
                            var nombre = params.name || categorias[params.dataIndex] || '';
                            return getColor(nombre, params.dataIndex);
                        },
                        borderRadius: [6, 6, 0, 0]
                    },
                    label: {
                        show: true,
                        position: 'top',
                        color: '#fff',
                        fontSize: 12,
                        fontWeight: 'bold'
                    }
                }],
                backgroundColor: 'transparent',
                grid: {
                    left: '10%',
                    right: '5%',
                    bottom: '18%',
                    top: '15%'
                }
            });

            barraChart.off('click');
            barraChart.on('click', handleChartClick);
        }

        setTimeout(function () {
            if (tortaChart) tortaChart.resize();
            if (barraChart) barraChart.resize();
        }, 100);
    }

    // ============================================================
    // MODAL DE DETALLE (drilldown)
    // ============================================================
    window.abrirModalDetalle = function (estado, jerarquia) {
        jerarquia = jerarquia || '';
        if (!window.AppModal || !window.AppModal.showFetch) {
            Logger.error('Falta AppModal.showFetch. Revisar static/js/utils/modal.js');
            Notify.error('No se pudo cargar el modal de detalle.');
            return;
        }

        ultimoEstadoModal = estado;
        var url = '/graficos_repuestos/detalle/' + encodeURIComponent(estado);
        if (jerarquia) {
            url += '?jerarquia=' + encodeURIComponent(jerarquia);
        }

        var loadingMessage = jerarquia
            ? 'Cargando repuestos de "' + estado + '" en "' + jerarquia + '"...'
            : 'Cargando repuestos de "' + estado + '"...';

        AppModal.showFetch({
            modalId: 'modalDetalleEstado',
            contentId: 'modalDetalleContenido',
            url: url,
            loadingMessage: loadingMessage,
            errorMessage: 'Error al cargar los repuestos.',
            afterRender: function (container) {
                actualizarLinkExportar(container, jerarquia);
            }
        });
    };

    // ============================================================
    // CARGA DE DATOS FILTRADOS
    // ============================================================
    function cargarDatosFiltrados(jerarquia) {
        var url = '/graficos_repuestos/datos';
        if (jerarquia) {
            url += '?jerarquia=' + encodeURIComponent(jerarquia);
        }

        Logger.apiCall('GET', url);

        fetch(url, { credentials: 'same-origin' })
            .then(function (resp) {
                if (!resp.ok) throw new Error('HTTP ' + resp.status);
                return resp.json();
            })
            .then(function (datos) {
                Logger.apiResponse('GET', url, 200, datos);
                renderizarGraficos(datos);
            })
            .catch(function (err) {
                Logger.error('Error al cargar datos filtrados', err);
                Notify.error('Error al filtrar los datos');
            });
    }

    // ============================================================
    // EXPORTAR PDF
    // ============================================================
    function configurarExportarPDF() {
        var btnExport = document.getElementById('exportarPdf');
        if (!btnExport) return;

        btnExport.addEventListener('click', function () {
            var graficoDiv = document.getElementById('grafico');
            if (!window.PdfExporter || !window.PdfExporter.element) {
                Notify.error('PdfExporter no disponible.');
                return;
            }
            PdfExporter.element(graficoDiv, {
                filename: 'graficos_repuestos.pdf',
                title: 'Gráficos de Repuestos por Estado',
                backgroundColor: '#111',
                textColor: '#fff',
                orientation: 'landscape'
            });
        });
    }

    // ============================================================
    // INICIALIZACIÓN
    // ============================================================
    function init() {
        Logger.moduleInit('GraficosRepuestos');

        // Leer datos desde data-attributes (sin script inline)
        var dataNode = document.getElementById('graficosRepuestosData');
        if (dataNode) {
            try {
                var raw = dataNode.getAttribute('data-datos');
                if (raw) {
                    datosIniciales = JSON.parse(raw);
                }

                // Configurar endpoints globales para repuesto_form.js
                window.RepuestoEndpoints = {
                    agregar: dataNode.getAttribute('data-endpoint-agregar') || '',
                    editar: dataNode.getAttribute('data-endpoint-editar') || '',
                    eliminar: dataNode.getAttribute('data-endpoint-eliminar') || '',
                    returnTo: dataNode.getAttribute('data-return-to') || 'indexgraficos_repuestos.indexgraficos_repuestos'
                };
            } catch (e) {
                Logger.error('Error parseando datos iniciales', e);
            }
        }

        // Renderizar gráficos
        if (datosIniciales) {
            renderizarGraficos(datosIniciales);
        } else {
            cargarDatosFiltrados(getCurrentJerarquia());
        }

        // Configurar select de jerarquía
        var select = document.getElementById('jerarquiaSelect');
        if (select) {
            select.addEventListener('change', function () {
                var jerarquia = this.value;
                actualizarUrlFiltro(jerarquia);
                cargarDatosFiltrados(jerarquia);

                // Si el modal de detalle está abierto, recargar con nuevo filtro
                var modalEl = document.getElementById('modalDetalleEstado');
                if (modalEl && modalEl.classList.contains('show') && ultimoEstadoModal) {
                    window.abrirModalDetalle(ultimoEstadoModal, jerarquia);
                }
            });
        }

        // Configurar exportar PDF
        configurarExportarPDF();

        // Configurar resize
        configurarResize();

        // Limpiar estado al cerrar modal
        var modalDetalleEl = document.getElementById('modalDetalleEstado');
        if (modalDetalleEl) {
            modalDetalleEl.addEventListener('hidden.bs.modal', function () {
                ultimoEstadoModal = '';
            });
        }

        Logger.success('Módulo GraficosRepuestos inicializado');
    }

    // Esperar a que el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();