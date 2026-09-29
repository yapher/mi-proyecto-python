// templates/Aplic/graficosrepuestos/static/js/graficos_repuestos.js
/**
 * Gráficos de Repuestos por Estado
 *
 * Corrección:
 * - El filtro de ubicación técnica (#jerarquiaSelect) ahora también se aplica al modal.
 * - Al hacer click en el gráfico, se envía ?jerarquia=... al endpoint de detalle.
 * - Si el modal está abierto y se cambia el filtro, se recarga con el nuevo filtro.
 * - El botón "Exportar a PDF" del modal también respeta el filtro activo.
 *
 * Mantiene IDs existentes:
 * - #jerarquiaSelect
 * - #grafico
 * - #graficoTorta
 * - #graficoBarras
 * - #exportarPdf
 * - #modalDetalleEstado
 * - #modalDetalleContenido
 */

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

    /* ========================================================
       PALETA Y COLORES
       ======================================================== */

    const PALETA = [
        '#2ecc71', // verde
        '#e74c3c', // rojo
        '#f1c40f', // amarillo
        '#3498db', // azul
        '#9b59b6', // violeta
        '#e67e22', // naranja
        '#1abc9c', // turquesa
        '#fd79a8', // rosa
        '#00b894', // verde azulado
        '#6c5ce7', // índigo
        '#fdcb6e', // ámbar
        '#74b9ff', // celeste
        '#a29bfe', // lavanda
        '#ff7675', // coral
        '#55efc4', // menta
        '#ffeaa7'  // crema
    ];

    const COLOR_MAP = {
        'disponible': '#2ecc71',
        'operativo': '#2ecc71',
        'en espera': '#f1c40f',
        'espera': '#f1c40f',
        'no disponible': '#e74c3c',
        'no operativo': '#e74c3c',
        'danado': '#e74c3c',
        'roto': '#e74c3c',
        'sin codigo': '#e67e22',
        'descontinuado': '#9b59b6',
        'actualizar codigo': '#3498db',
        'mantenimiento': '#e67e22',
        'reparando': '#e67e22',
        'reserva': '#9b59b6',
        'otros': '#9e9e9e',
        'otro': '#9e9e9e',
        'sin estado': '#9e9e9e'
    };

    const EMOJI_MAP = {
        '🟢': '#2ecc71',
        '🟡': '#f1c40f',
        '🔴': '#e74c3c',
        '🔵': '#3498db',
        '🟣': '#9b59b6',
        '🟠': '#e67e22',
        '⚪': '#ecf0f1',
        '⚫': '#7f8c8d',
        '🟤': '#8d6e63'
    };

    const KEYWORDS = [
        ['no disponible', '#e74c3c'],
        ['no operativo', '#e74c3c'],
        ['danado', '#e74c3c'],
        ['roto', '#e74c3c'],
        ['en espera', '#f1c40f'],
        ['espera', '#f1c40f'],
        ['mantenimiento', '#e67e22'],
        ['reparando', '#e67e22'],
        ['descontinuado', '#9b59b6'],
        ['reserva', '#9b59b6'],
        ['actualizar codigo', '#3498db'],
        ['sin codigo', '#e67e22'],
        ['disponible', '#2ecc71'],
        ['operativo', '#2ecc71'],
        ['otros', '#9e9e9e'],
        ['otro', '#9e9e9e']
    ];

    function normalizarTexto(valor) {
        return String(valor || '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .trim();
    }

    function hashColor(texto) {
        const str = normalizarTexto(texto) || 'sin-color';
        let hash = 0;

        for (let i = 0; i < str.length; i++) {
            hash = str.charCodeAt(i) + ((hash << 5) - hash);
            hash = hash & hash;
        }

        const hue = Math.abs(hash) % 360;
        return 'hsl(' + hue + ', 70%, 55%)';
    }

    function obtenerColorCategoria(categoria, index) {
        const raw = String(categoria || '');
        const norm = normalizarTexto(raw);

        if (COLOR_MAP[norm]) {
            return COLOR_MAP[norm];
        }

        for (const emoji of Object.keys(EMOJI_MAP)) {
            if (raw.indexOf(emoji) !== -1) {
                return EMOJI_MAP[emoji];
            }
        }

        for (let i = 0; i < KEYWORDS.length; i++) {
            const keyword = KEYWORDS[i][0];
            const color = KEYWORDS[i][1];

            if (norm.indexOf(keyword) !== -1) {
                return color;
            }
        }

        if (typeof index === 'number' && index >= 0) {
            return PALETA[index % PALETA.length];
        }

        return hashColor(raw);
    }

    function escapeHtml(value) {
        return String(value || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    /* ========================================================
       FILTRO ACTUAL
       ======================================================== */

    function getCurrentJerarquia() {
        const select = document.getElementById('jerarquiaSelect');
        return select ? String(select.value || '').trim() : '';
    }

    /* ========================================================
       MODALES
       ======================================================== */

    function getModalInstance(element) {
        if (!element) {
            return null;
        }

        if (!window.bootstrap || !window.bootstrap.Modal) {
            Logger.error('Bootstrap no está disponible para abrir modales.');
            return null;
        }

        let instance = window.bootstrap.Modal.getInstance(element);

        if (!instance) {
            instance = new window.bootstrap.Modal(element);
        }

        return instance;
    }

    function ensureModalDetalle(showError) {
        const modalEl = document.getElementById('modalDetalleEstado');

        if (!modalEl) {
            Logger.error('No se encontró #modalDetalleEstado en el DOM.');

            if (showError) {
                Notify.error('No se encontró el modal de detalle.');
            }

            return null;
        }

        return getModalInstance(modalEl);
    }

    /* ========================================================
       EXPORT LINK DENTRO DEL MODAL
       ======================================================== */

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
                // Fallback manual si URL() falla por algún href raro
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

    /* ========================================================
       GRÁFICOS
       ======================================================== */

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

        const categorias = datos.categorias.map(function (cat) {
            return String(cat || '');
        });

        const valores = datos.valores.map(function (val) {
            return Number(val || 0);
        });

        /* ===== TORTA ===== */
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
                        color: obtenerColorCategoria(cat, i),
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

        /* ===== BARRAS ===== */
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
                            return obtenerColorCategoria(nombre, params.dataIndex);
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

    /* ========================================================
       MODAL DETALLE
       ======================================================== */

    window.abrirModalDetalle = async function (estado, jerarquia = '') {
        const contenido = document.getElementById('modalDetalleContenido');

        if (!contenido) {
            Logger.error('No se encontró #modalDetalleContenido.');
            Notify.error('No se encontró el contenido del modal de detalle.');
            return;
        }

        ultimoEstadoModal = estado;

        const estadoSeguro = escapeHtml(estado);
        const jerarquiaSegura = escapeHtml(jerarquia || '');

        const mensaje = jerarquiaSegura
            ? `Cargando repuestos de "${estadoSeguro}" en "${jerarquiaSegura}"...`
            : `Cargando repuestos de "${estadoSeguro}"...`;

        contenido.innerHTML =
            '<div class="modal-body text-center py-5">' +
                '<div class="spinner-border text-primary" role="status"></div>' +
                '<p class="mt-3 text-white">' + mensaje + '</p>' +
            '</div>';

        const modal = ensureModalDetalle(true);

        if (!modal) {
            return;
        }

        try {
            modal.show();
        } catch (err) {
            Logger.error('modal.show() falló', err);
            Notify.error('No se pudo abrir el modal de detalle.');
            return;
        }

        let url = '/graficos_repuestos/detalle/' + encodeURIComponent(estado);

        if (jerarquia) {
            url += '?jerarquia=' + encodeURIComponent(jerarquia);
        }

        try {
            Logger.apiCall('GET', url);

            const res = await fetch(url, {
                credentials: 'same-origin'
            });

            Logger.apiResponse('GET', url, res.status);

            if (!res.ok) {
                throw new Error('HTTP ' + res.status);
            }

            const html = await res.text();
            contenido.innerHTML = html;

            actualizarLinkExportar(contenido, jerarquia);

            Logger.success('Detalle cargado', {
                estado: estado,
                jerarquia: jerarquia
            });
        } catch (err) {
            Logger.error('Error cargando detalle', err);

            contenido.innerHTML =
                '<div class="modal-body text-center py-5">' +
                    '<i class="bi bi-exclamation-triangle" style="font-size: 3rem; color: #dc3545;"></i>' +
                    '<p class="mt-3 text-danger">Error al cargar los repuestos</p>' +
                    '<p class="text-white-50 small">' + escapeHtml(err && err.message ? err.message : err) + '</p>' +
                    '<button class="btn btn-cancelar" data-bs-dismiss="modal">Cerrar</button>' +
                '</div>';

            Notify.error('No se pudieron cargar los repuestos.');
        }
    };

    /* ========================================================
       FILTRADO DE TABLA EN MODAL
       ======================================================== */

    window.filtrarTablaModal = function (input) {
        if (!input) return;

        const term = (input.value || '').toLowerCase().trim();

        const root =
            input.closest('.modal-body') ||
            document.getElementById('modalDetalleContenido') ||
            document;

        const table = root.querySelector('table');

        if (!table) {
            return;
        }

        const rows = table.querySelectorAll('tbody tr');

        rows.forEach(function (row) {
            const text = (row.textContent || '').toLowerCase();
            row.style.display = (!term || text.indexOf(term) !== -1) ? '' : 'none';
        });
    };

    /* ========================================================
       AMPLIAR IMAGEN
       ======================================================== */

    window.abrirModalImagen = function (src, nombre) {
        const modalEl = document.getElementById('modalImagenAmpliada');

        if (!modalEl) {
            if (src) {
                window.open(src, '_blank');
            }
            return;
        }

        const img = document.getElementById('imagenAmpliada');
        const title = document.getElementById('tituloImagenAmpliada');

        if (img) {
            img.src = src || '';
        }

        if (title) {
            title.textContent = nombre || 'Imagen';
        }

        const modal = getModalInstance(modalEl);

        if (modal) {
            modal.show();
        }
    };

    /* ========================================================
       FILTRO POR JERARQUÍA
       ======================================================== */

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

    /* ========================================================
       EXPORTAR PDF
       ======================================================== */

    function exportarGraficosPdf() {
        const graficoDiv = document.getElementById('grafico');

        if (!graficoDiv) {
            Notify.error('No se encontró el contenedor del gráfico.');
            return;
        }

        if (!window.html2canvas || !window.jspdf) {
            Notify.error('No se pudieron cargar las librerías de exportación.');
            return;
        }

        const fondo = getComputedStyle(document.body).backgroundColor || '#3e2d59';

        window.html2canvas(graficoDiv, {
            backgroundColor: fondo,
            scale: 2
        })
            .then(function (canvas) {
                const imgData = canvas.toDataURL('image/png');
                const jsPDF = window.jspdf.jsPDF;

                const pdf = new jsPDF({
                    orientation: 'landscape',
                    unit: 'px',
                    format: [
                        canvas.width / 2 + 60,
                        canvas.height / 2 + 100
                    ]
                });

                pdf.setFontSize(20);
                pdf.setTextColor(255, 255, 255);
                pdf.setFillColor(62, 45, 89);
                pdf.rect(
                    0,
                    0,
                    pdf.internal.pageSize.width,
                    pdf.internal.pageSize.height,
                    'F'
                );

                pdf.text('Gráficos de Repuestos por Estado', 30, 40);

                pdf.setFontSize(12);
                pdf.text(
                    'Fecha: ' + new Date().toLocaleDateString('es-AR'),
                    30,
                    60
                );

                pdf.addImage(
                    imgData,
                    'PNG',
                    30,
                    80,
                    canvas.width / 2,
                    canvas.height / 2
                );

                pdf.save('graficos_repuestos.pdf');
            })
            .catch(function (err) {
                Logger.error('Error exportando PDF', err);
                Notify.error('No se pudo exportar el PDF.');
            });
    }

    /* ========================================================
       INIT
       ======================================================== */

    function init() {
        Logger.moduleInit('GraficosRepuestos');

        ensureModalDetalle(false);

        if (window.datos_iniciales) {
            renderizarGraficos(window.datos_iniciales);
        } else {
            cargarDatosFiltrados(getCurrentJerarquia());
        }

        const select = document.getElementById('jerarquiaSelect');

        if (select) {
            select.addEventListener('change', function () {
                const jerarquia = this.value;

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
            btnExport.addEventListener('click', exportarGraficosPdf);
        }

        const modalDetalleEl = document.getElementById('modalDetalleEstado');

        if (modalDetalleEl) {
            modalDetalleEl.addEventListener('hidden.bs.modal', function () {
                ultimoEstadoModal = '';
            });
        }

        document.addEventListener('input', function (event) {
            const target = event.target;

            if (!target) return;

            if (
                target.id === 'buscarEnModal' ||
                target.classList.contains('js-filtrar-tabla')
            ) {
                window.filtrarTablaModal(target);
            }
        });

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