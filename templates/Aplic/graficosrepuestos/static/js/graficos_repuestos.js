/**
 * graficos_repuestos.js
 * Usa GraficosEcharts reutilizable + AppModal + FetchHelper
 */
(function () {
    'use strict';

    if (window.__graficosRepuestosInitialized) return;
    window.__graficosRepuestosInitialized = true;

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
            Logger.warn('No se pudo actualizar la URL', e);
        }
    }

    function actualizarLinkExportar(container, jerarquia) {
        if (!container) return;
        const links = container.querySelectorAll('a[href*="/graficos_repuestos/exportar_pdf_estado/"]');
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

    function renderizarGraficos(datos) {
        if (!datos || !datos.categorias || !datos.valores || datos.categorias.length === 0) {
            Logger.warn('No hay datos para graficar.');
            return;
        }

        GraficosEcharts.renderTorta('graficoTorta', datos, {
            titulo: 'Repuestos por Estado',
            useChartPalette: true,
            onClick: handleChartClick
        });

        GraficosEcharts.renderBarras('graficoBarras', datos, {
            titulo: 'Cantidad por Estado',
            useChartPalette: true,
            onClick: handleChartClick
        });
    }

    window.abrirModalDetalle = function (estado, jerarquia) {
        jerarquia = jerarquia || '';
        if (!window.AppModal || !window.AppModal.showFetch) {
            Logger.error('Falta AppModal.showFetch');
            Notify.error('No se pudo cargar el modal.');
            return;
        }

        ultimoEstadoModal = estado;
        let url = '/graficos_repuestos/detalle/' + encodeURIComponent(estado);
        if (jerarquia) url += '?jerarquia=' + encodeURIComponent(jerarquia);

        const loadingMessage = jerarquia
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

    function cargarDatosFiltrados(jerarquia) {
        let url = '/graficos_repuestos/datos';
        if (jerarquia) url += '?jerarquia=' + encodeURIComponent(jerarquia);

        FetchHelper.get(url, { showErrors: false })
            .then(renderizarGraficos)
            .catch(function () {
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
                if (modalEl && modalEl.classList.contains('show') && ultimoEstadoModal) {
                    window.abrirModalDetalle(ultimoEstadoModal, jerarquia);
                }
            });
        }

        const btnExport = document.getElementById('exportarPdf');
        if (btnExport) {
            btnExport.addEventListener('click', function () {
                const graficoDiv = document.getElementById('grafico');
                if (window.PdfExporter && window.PdfExporter.element) {
                    PdfExporter.element(graficoDiv, {
                        filename: 'graficos_repuestos.pdf',
                        title: 'Gráficos de Repuestos por Estado',
                        backgroundColor: '#111',
                        textColor: '#fff',
                        orientation: 'landscape'
                    });
                } else {
                    Notify.error('PdfExporter no disponible');
                }
            });
        }

        const modalDetalleEl = document.getElementById('modalDetalleEstado');
        if (modalDetalleEl) {
            modalDetalleEl.addEventListener('hidden.bs.modal', function () {
                ultimoEstadoModal = '';
            });
        }

        Logger.success('Módulo GraficosRepuestos inicializado');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();