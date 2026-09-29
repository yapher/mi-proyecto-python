// templates/Aplic/graficosrepuestos/static/js/graficos_repuestos.js
(function () {
    'use strict';

    if (window.__graficosRepuestosInitialized) {
        return;
    }

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
        error: function (msg) {
            window.alert(msg || 'Error');
        },
        warning: function () {}
    };

    let tortaChart = null;
    let barraChart = null;
    let ultimoEstadoModal = '';

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
        if (!container) {
            return;
        }

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

                const nuevoHref = url.pathname + (url.search || '');
                link.setAttribute('href', nuevoHref);
            } catch (e) {
                if (jerarquia) {
                    if (href.indexOf('?') === -1) {
                        link.setAttribute('href', href + '?jerarquia=' + encodeURIComponent(jerarquia));
                    } else if (href.indexOf('jerarquia=') === -1) {
                        link.setAttribute('href', href + '&jerarquia=' + encodeURIComponent(jerarquia));
                    }
                } else {
                    let limpio = href.replace(/([?&])jerarquia=[^&]*&?/g, '$1');
                    limpio = limpio.replace(/\?&$/, '?').replace(/&$/, '');

                    if (limpio.endsWith('?')) {
                        limpio = limpio.slice(0, -1);
                    }

                    link.setAttribute('href', limpio);
                }
            }
        });
    }

    function handleChartClick(params) {
        let nombre = '';

        if (params && params.name) {
            nombre = params.name;
        } else if (params && Array.isArray(params.value) && params.value.length) {
            nombre = params.value[0];
        }

        const jerarquia = getCurrentJerarquia();

        Logger.info('Click en gráfico', {
            nombre: nombre,
            jerarquia: jerarquia
        });

        if (nombre) {
            window.abrirModalDetalle(nombre, jerarquia);
        }
    }

    function renderizarGraficos(datos) {
        if (!window.echarts) {
            Logger.error('ECharts no está disponible.');
            Notify.error('No se pudo cargar la librería de gráficos.');
            return;
        }

        if (
            !datos ||
            !Array.isArray(datos.categorias) ||
            !Array.isArray(datos.valores) ||
            datos.categorias.length === 0
        ) {
            Logger.warn('No hay datos para graficar.');
            return;
        }

        const getColor = window.ChartPalette && window.ChartPalette.getColor
            ? window.ChartPalette.getColor
            : function () { return '#9E9E9E'; };

        const categorias = datos.categorias.map(function (cat) {
            return String(cat || '');
        });

        const valores = datos.valores.map(function (val) {
            return Number(val || 0);
        });

        const elTorta = document.getElementById('graficoTorta');

        if (elTorta) {
            if (tortaChart) {
                tortaChart.dispose();
            }

            tortaChart = window.echarts.init(elTorta);

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
                    textStyle: {
                        color: 'white'
                    }
                },
                tooltip: {
                    trigger: 'item',
                    formatter: '{b}: {c} ({d}%)'
                },
                legend: {
                    bottom: 0,
                    textStyle: {
                        color: '#fff'
                    }
                },
                series: [{
                    type: 'pie',
                    roseType: 'radius',
                    radius: ['30%', '70%'],
                    data: tortaData,
                    label: {
                        color: 'white',
                        fontSize: 14
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

        const elBarras = document.getElementById('graficoBarras');

        if (elBarras) {
            if (barraChart) {
                barraChart.dispose();
            }

            barraChart = window.echarts.init(elBarras);

            const barrasData = categorias.map(function (cat, i) {
                return {
                    name: cat,
                    value: valores[i] || 0
                };
            });

            barraChart.setOption({
                title: {
                    text: 'Cantidad por Estado',
                    left: 'center',
                    textStyle: {
                        color: 'white'
                    }
                },
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'shadow'
                    }
                },
                xAxis: {
                    type: 'category',
                    data: categorias,
                    axisLabel: {
                        color: '#fff',
                        interval: 0,
                        rotate: 30,
                        formatter: function (value) {
                            const text = String(value || '');
                            return text.length > 12 ? text.substring(0, 12) + '…' : text;
                        }
                    },
                    axisLine: {
                        lineStyle: {
                            color: '#555'
                        }
                    }
                },
                yAxis: {
                    type: 'value',
                    axisLabel: {
                        color: '#fff'
                    },
                    axisLine: {
                        lineStyle: {
                            color: '#555'
                        }
                    },
                    splitLine: {
                        lineStyle: {
                            color: '#333'
                        }
                    }
                },
                series: [{
                    type: 'bar',
                    data: barrasData,
                    barMaxWidth: 50,
                    itemStyle: {
                        color: function (params) {
                            const nombre = params.name || categorias[params.dataIndex] || '';
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
        }, 80);
    }

    window.abrirModalDetalle = async function (estado, jerarquia = '') {
        if (!window.AppModal || !window.AppModal.showFetch) {
            Logger.error('Falta window.AppModal.showFetch. Revisar static/js/utils/modal.js');
            Notify.error('No se pudo cargar el modal de detalle.');
            return;
        }

        ultimoEstadoModal = estado;

        let url = '/graficos_repuestos/detalle/' + encodeURIComponent(estado);

        if (jerarquia) {
            url += '?jerarquia=' + encodeURIComponent(jerarquia);
        }

        const loadingMessage = jerarquia
            ? `Cargando repuestos de "${estado}" en "${jerarquia}"...`
            : `Cargando repuestos de "${estado}"...`;

        await window.AppModal.showFetch({
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

    function cargarDatosFiltrados(jerarquia) {
        let url = '/graficos_repuestos/datos';

        if (jerarquia) {
            url += '?jerarquia=' + encodeURIComponent(jerarquia);
        }

        fetch(url, {
            credentials: 'same-origin'
        })
            .then(function (resp) {
                if (!resp.ok) {
                    throw new Error('HTTP ' + resp.status);
                }
                return resp.json();
            })
            .then(function (datos) {
                renderizarGraficos(datos);
            })
            .catch(function (err) {
                Logger.error('Error al cargar datos filtrados', err);
                Notify.error('Error al filtrar los datos');
            });
    }

    function init() {
        Logger.moduleInit('GraficosRepuestos');

        if (window.datos_iniciales) {
            renderizarGraficos(window.datos_iniciales);
        } else {
            cargarDatosFiltrados(getCurrentJerarquia());
        }

        const select = document.getElementById('jerarquiaSelect');

        if (select) {
            select.addEventListener('change', function () {
                const jerarquia = this.value;

                actualizarUrlFiltro(jerarquia);
                cargarDatosFiltrados(jerarquia);

                const modalEl = document.getElementById('modalDetalleEstado');

                if (
                    modalEl &&
                    modalEl.classList.contains('show') &&
                    ultimoEstadoModal
                ) {
                    window.abrirModalDetalle(ultimoEstadoModal, jerarquia);
                }
            });
        }

        const btnExport = document.getElementById('exportarPdf');

        if (btnExport) {
            btnExport.addEventListener('click', function () {
                const graficoDiv = document.getElementById('grafico');

                if (!window.PdfExporter || !window.PdfExporter.element) {
                    Notify.error('Falta window.PdfExporter.element.');
                    return;
                }

                window.PdfExporter.element(graficoDiv, {
                    filename: 'graficos_repuestos.pdf',
                    title: 'Gráficos de Repuestos por Estado',
                    backgroundColor: '#111',
                    textColor: '#fff',
                    orientation: 'landscape'
                });
            });
        }

        const modalDetalleEl = document.getElementById('modalDetalleEstado');

        if (modalDetalleEl) {
            modalDetalleEl.addEventListener('hidden.bs.modal', function () {
                ultimoEstadoModal = '';
            });
        }

        window.addEventListener('resize', function () {
            if (tortaChart) tortaChart.resize();
            if (barraChart) barraChart.resize();
        });

        Logger.success('Módulo GraficosRepuestos inicializado');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();