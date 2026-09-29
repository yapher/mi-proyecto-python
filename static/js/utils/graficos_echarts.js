/**
 * graficos_echarts.js - Renderizado reutilizable de gráficos ECharts
 * 
 * Unifica la lógica de tortas, barras y 3D que se repite en:
 * - estadisticadeparadas
 * - graficosrepuestos
 * - estadisticas
 * - listarot
 * - pagos
 * 
 * Uso:
 *   GraficosEcharts.renderTorta(el, datos, opciones)
 *   GraficosEcharts.renderBarras(el, datos, opciones)
 *   GraficosEcharts.renderBarras3D(el, datos, opciones)
 */
(function () {
    'use strict';

    if (window.__graficosEchartsInitialized) return;
    window.__graficosEchartsInitialized = true;

    const PALETA = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
        '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788',
        '#E74C3C', '#3498DB', '#9B59B6', '#F39C12', '#1ABC9C'
    ];

    function getColor(index) {
        return PALETA[index % PALETA.length];
    }

    function ajustarBrillo(color, porcentaje) {
        const num = parseInt(color.replace('#', ''), 16);
        const amt = Math.round(2.55 * porcentaje);
        const R = Math.max(0, Math.min(255, (num >> 16) + amt));
        const G = Math.max(0, Math.min(255, (num >> 8 & 0x00FF) + amt));
        const B = Math.max(0, Math.min(255, (num & 0x0000FF) + amt));
        return '#' + (0x1000000 + R * 0x10000 + G * 0x100 + B).toString(16).slice(1);
    }

    function _validarDatos(datos) {
        if (!datos || !Array.isArray(datos.categorias) || !Array.isArray(datos.valores)) {
            return false;
        }
        return datos.categorias.length > 0;
    }

    function _truncar(texto, max) {
        max = max || 15;
        texto = String(texto || '');
        return texto.length > max ? texto.substring(0, max) + '…' : texto;
    }

    /**
     * Renderiza un gráfico de torta / dona
     */
    function renderTorta(elemento, datos, opciones) {
        opciones = opciones || {};
        if (!window.echarts || !_validarDatos(datos)) return null;

        const el = typeof elemento === 'string' ? document.getElementById(elemento) : elemento;
        if (!el) return null;

        let chart = echarts.getInstanceByDom(el);
        if (chart) chart.dispose();
        chart = echarts.init(el);

        const tortaData = datos.categorias.map(function (cat, i) {
            const color = opciones.useChartPalette && window.ChartPalette
                ? window.ChartPalette.getColor(cat, i)
                : getColor(i);
            return {
                name: cat,
                value: datos.valores[i] || 0,
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: color },
                        { offset: 1, color: ajustarBrillo(color, -30) }
                    ]),
                    shadowBlur: 10,
                    shadowColor: 'rgba(0, 0, 0, 0.3)'
                }
            };
        });

        const isMobile = window.innerWidth < 768;

        chart.setOption({
            title: {
                text: opciones.titulo || '',
                left: 'center',
                top: 10,
                textStyle: {
                    color: opciones.titleColor || '#fff',
                    fontSize: isMobile ? 14 : 18,
                    fontWeight: 'bold'
                }
            },
            tooltip: {
                trigger: 'item',
                formatter: opciones.tooltipFormatter || '{b}: {c} ({d}%)',
                backgroundColor: 'rgba(62, 45, 89, 0.95)',
                borderColor: '#88c999',
                borderWidth: 2,
                textStyle: { color: '#fff' }
            },
            legend: {
                orient: isMobile ? 'horizontal' : 'vertical',
                right: isMobile ? 'center' : 10,
                bottom: isMobile ? 0 : 'auto',
                top: isMobile ? 'auto' : 'center',
                textStyle: { color: '#fff', fontSize: isMobile ? 9 : 11 },
                formatter: function (name) { return _truncar(name, 20); }
            },
            series: [{
                type: 'pie',
                roseType: opciones.roseType || 'radius',
                radius: opciones.radius || ['30%', '70%'],
                center: isMobile ? ['50%', '45%'] : (opciones.center || ['40%', '55%']),
                data: tortaData,
                label: {
                    show: !isMobile,
                    color: '#fff',
                    fontSize: 12,
                    formatter: opciones.labelFormatter || '{c}'
                },
                labelLine: {
                    show: !isMobile,
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

        if (opciones.onClick) {
            chart.on('click', opciones.onClick);
        }

        return chart;
    }

    /**
     * Renderiza un gráfico de barras
     */
    function renderBarras(elemento, datos, opciones) {
        opciones = opciones || {};
        if (!window.echarts || !_validarDatos(datos)) return null;

        const el = typeof elemento === 'string' ? document.getElementById(elemento) : elemento;
        if (!el) return null;

        let chart = echarts.getInstanceByDom(el);
        if (chart) chart.dispose();
        chart = echarts.init(el);

        const barrasData = datos.categorias.map(function (cat, i) {
            return {
                name: cat,
                value: datos.valores[i] || 0
            };
        });

        chart.setOption({
            title: {
                text: opciones.titulo || '',
                left: 'center',
                top: 10,
                textStyle: {
                    color: opciones.titleColor || '#fff',
                    fontSize: window.innerWidth < 480 ? 14 : 18,
                    fontWeight: 'bold'
                }
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'shadow' }
            },
            xAxis: {
                type: 'category',
                data: datos.categorias,
                axisLabel: {
                    color: '#fff',
                    interval: 0,
                    rotate: opciones.rotateLabels !== false ? 30 : 0,
                    formatter: function (value) { return _truncar(value, 12); }
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
                        const nombre = params.name || datos.categorias[params.dataIndex] || '';
                        if (opciones.useChartPalette && window.ChartPalette) {
                            return window.ChartPalette.getColor(nombre, params.dataIndex);
                        }
                        return getColor(params.dataIndex);
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

        if (opciones.onClick) {
            chart.on('click', opciones.onClick);
        }

        return chart;
    }

    /**
     * Renderiza barras 3D (con fallback automático a 2D)
     */
    function renderBarras3D(elemento, datos, opciones) {
        opciones = opciones || {};
        const el = typeof elemento === 'string' ? document.getElementById(elemento) : elemento;
        if (!el) return null;

        const tiene3D = typeof echarts !== 'undefined' && typeof echarts.gl !== 'undefined';

        if (!tiene3D || !_validarDatos(datos)) {
            return renderBarras(elemento, datos, opciones);
        }

        try {
            let chart = echarts.getInstanceByDom(el);
            if (chart) chart.dispose();
            chart = echarts.init(el);

            chart.setOption({
                title: {
                    text: opciones.titulo || '',
                    left: 'center',
                    top: 10,
                    textStyle: {
                        color: opciones.titleColor || '#88c999',
                        fontSize: window.innerWidth < 480 ? 14 : 18,
                        fontWeight: 'bold'
                    }
                },
                tooltip: {
                    formatter: function (params) {
                        return '<b>' + params.value[0] + '</b><br/>' + params.value[2] + ' órdenes';
                    },
                    backgroundColor: 'rgba(62, 45, 89, 0.95)',
                    borderColor: '#88c999',
                    borderWidth: 2,
                    textStyle: { color: '#fff' }
                },
                xAxis3D: {
                    type: 'category',
                    data: datos.categorias,
                    axisLabel: {
                        color: '#fff',
                        fontSize: 10,
                        interval: 0,
                        rotate: 45,
                        formatter: function (v) { return _truncar(v, 12); }
                    }
                },
                yAxis3D: { type: 'category', data: [opciones.yLabel || 'Cantidad'] },
                zAxis3D: { type: 'value' },
                grid3D: {
                    boxWidth: 200,
                    boxDepth: 80,
                    viewControl: { alpha: 25, beta: 40, rotateSensitivity: 2 },
                    light: {
                        main: { intensity: 1.5, shadow: true },
                        ambient: { intensity: 0.4 }
                    },
                    environment: '#1a1a2e'
                },
                series: [{
                    type: 'bar3D',
                    data: datos.categorias.map(function (cat, i) {
                        return [cat, opciones.yLabel || 'Cantidad', datos.valores[i]];
                    }),
                    shading: 'realistic',
                    label: {
                        show: true,
                        formatter: function (p) { return p.value[2]; },
                        textStyle: {
                            color: '#fff',
                            fontSize: 12,
                            fontWeight: 'bold',
                            backgroundColor: 'rgba(0,0,0,0.7)',
                            padding: 4,
                            borderRadius: 4
                        }
                    },
                    itemStyle: {
                        color: function (params) {
                            const c = getColor(params.dataIndex);
                            return new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                { offset: 0, color: c },
                                { offset: 1, color: ajustarBrillo(c, -40) }
                            ]);
                        },
                        opacity: 0.95
                    }
                }],
                backgroundColor: 'transparent'
            });

            if (opciones.onClick) {
                chart.on('click', opciones.onClick);
            }

            return chart;

        } catch (e) {
            console.warn('3D falló, usando 2D:', e);
            return renderBarras(elemento, datos, opciones);
        }
    }

    /**
     * Renderiza gráfico de línea
     */
    function renderLinea(elemento, datos, opciones) {
        opciones = opciones || {};
        if (!window.echarts || !_validarDatos(datos)) return null;

        const el = typeof elemento === 'string' ? document.getElementById(elemento) : elemento;
        if (!el) return null;

        let chart = echarts.getInstanceByDom(el);
        if (chart) chart.dispose();
        chart = echarts.init(el);

        chart.setOption({
            title: {
                text: opciones.titulo || '',
                left: 'center',
                textStyle: { color: opciones.titleColor || '#fff' }
            },
            tooltip: {
                trigger: 'axis',
                formatter: opciones.tooltipFormatter || undefined
            },
            xAxis: {
                type: 'category',
                data: datos.categorias,
                axisLabel: { color: '#fff', rotate: 30 }
            },
            yAxis: {
                type: 'value',
                axisLabel: { color: '#fff' }
            },
            series: [{
                type: 'line',
                data: datos.valores,
                smooth: true,
                lineStyle: { width: 3, color: '#88c999' },
                areaStyle: { opacity: 0.3, color: '#88c999' },
                itemStyle: { color: '#88c999' },
                markPoint: {
                    data: [
                        { type: 'max', name: 'Máximo' },
                        { type: 'min', name: 'Mínimo' }
                    ]
                }
            }],
            backgroundColor: 'transparent'
        });

        return chart;
    }

    /**
     * Resize handler para todos los charts
     */
    function resizeAll() {
        const charts = document.querySelectorAll('[_echarts_instance_]');
        charts.forEach(function (el) {
            const instance = echarts.getInstanceByDom(el);
            if (instance) instance.resize();
        });
    }

    window.addEventListener('resize', function () {
        clearTimeout(window._graficosResizeTimer);
        window._graficosResizeTimer = setTimeout(resizeAll, 250);
    });

    window.GraficosEcharts = {
        renderTorta: renderTorta,
        renderBarras: renderBarras,
        renderBarras3D: renderBarras3D,
        renderLinea: renderLinea,
        getColor: getColor,
        paleta: PALETA,
        resizeAll: resizeAll
    };
})();