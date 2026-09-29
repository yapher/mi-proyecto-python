/**
 * estadistica_de_paradas.js
 * Usa GraficosEcharts reutilizable (static/js/utils/graficos_echarts.js)
 */
document.addEventListener('DOMContentLoaded', function () {
    Logger.moduleInit('EstadisticaParadas');

    const datos_iniciales = window.datos_iniciales;
    const rango_fechas = window.rango_fechas;

    // Renderizar gráficos iniciales
    if (datos_iniciales) {
        renderizarGraficos(datos_iniciales);
    }

    // Configurar rangos de fechas iniciales
    if (rango_fechas && rango_fechas.min && rango_fechas.max) {
        document.getElementById('fechaInicio').value = convertirFecha(rango_fechas.min);
        document.getElementById('fechaFin').value = convertirFecha(rango_fechas.max);
        document.getElementById('fechaInicio').min = convertirFecha(rango_fechas.min);
        document.getElementById('fechaInicio').max = convertirFecha(rango_fechas.max);
        document.getElementById('fechaFin').min = convertirFecha(rango_fechas.min);
        document.getElementById('fechaFin').max = convertirFecha(rango_fechas.max);
    }

    // Cargar archivo
    const archivoInput = document.getElementById('archivoInput');
    if (archivoInput) {
        archivoInput.addEventListener('change', handleFileUpload);
    }

    // Filtro por columna
    const columnaSelect = document.getElementById('columnaSelect');
    if (columnaSelect) {
        columnaSelect.addEventListener('change', handleColumnChange);
    }

    // Filtrar por fechas
    const btnFiltrar = document.getElementById('btnFiltrarFechas');
    if (btnFiltrar) {
        btnFiltrar.addEventListener('click', handleDateFilter);
    }

    // Limpiar filtros
    const btnLimpiar = document.getElementById('btnLimpiarFechas');
    if (btnLimpiar) {
        btnLimpiar.addEventListener('click', handleClearFilters);
    }

    // Exportar a PDF
    const btnExport = document.getElementById('exportarPdf');
    if (btnExport) {
        btnExport.addEventListener('click', handleExportPDF);
    }

    // Drilldown en torta
    setupDrilldown();

    // ============================================
    // FUNCIONES
    // ============================================

    function renderizarGraficos(datos) {
        if (!datos || !datos.categorias || !datos.valores) {
            Logger.warn('Datos inválidos para renderizar');
            return;
        }

        // Torta
        GraficosEcharts.renderTorta('graficoTorta', datos, {
            titulo: 'Distribución por Categoría',
            useChartPalette: false,
            onClick: function (params) {
                const columnaFiltro = document.getElementById('columnaSelect').value;
                mostrarModalDrillDown(params.name, columnaFiltro);
            }
        });

        // Barras
        GraficosEcharts.renderBarras('graficoBarras', datos, {
            titulo: 'Cantidad por Categoría',
            useChartPalette: false,
            onClick: function (params) {
                const columnaFiltro = document.getElementById('columnaSelect').value;
                mostrarModalDrillDown(params.name, columnaFiltro);
            }
        });
    }

    function handleFileUpload(e) {
        const archivo = e.target.files[0];
        if (!archivo) return;

        document.getElementById('nombreArchivo').textContent = 'Archivo: ' + archivo.name;

        const formData = new FormData();
        formData.append('archivo', archivo);

        FetchHelper.postForm('/estadistica_de_paradas/cargar_archivo', formData)
            .then(function (data) {
                if (data.error) {
                    Notify.error(data.error);
                    return;
                }
                renderizarGraficos({ categorias: data.categorias, valores: data.valores });

                if (data.rango_fechas && data.rango_fechas.min && data.rango_fechas.max) {
                    document.getElementById('fechaInicio').value = convertirFecha(data.rango_fechas.min);
                    document.getElementById('fechaFin').value = convertirFecha(data.rango_fechas.max);
                    document.getElementById('fechaInicio').min = convertirFecha(data.rango_fechas.min);
                    document.getElementById('fechaInicio').max = convertirFecha(data.rango_fechas.max);
                    document.getElementById('fechaFin').min = convertirFecha(data.rango_fechas.min);
                    document.getElementById('fechaFin').max = convertirFecha(data.rango_fechas.max);
                }

                Notify.success('✓ Archivo cargado! Total: ' + data.total_avisos);
            })
            .catch(function () {
                Notify.error('Error al cargar el archivo.');
            });
    }

    function handleColumnChange() {
        const seleccion = this.value;
        const fechaInicio = document.getElementById('fechaInicio').value;
        const fechaFin = document.getElementById('fechaFin').value;

        let url = '/estadistica_de_paradas/datos?columna=' + encodeURIComponent(seleccion);
        if (fechaInicio) url += '&fecha_inicio=' + convertirFechaInversa(fechaInicio);
        if (fechaFin) url += '&fecha_fin=' + convertirFechaInversa(fechaFin);

        FetchHelper.get(url)
            .then(function (datos) {
                renderizarGraficos(datos);
            })
            .catch(function () {
                Notify.error('Error al cargar datos');
            });
    }

    function handleDateFilter() {
        const fechaInicio = document.getElementById('fechaInicio').value;
        const fechaFin = document.getElementById('fechaFin').value;

        if (!fechaInicio || !fechaFin) {
            Notify.warning('Selecciona ambas fechas');
            return;
        }

        const columna = document.getElementById('columnaSelect').value;
        const url = '/estadistica_de_paradas/datos?columna=' + columna +
            '&fecha_inicio=' + convertirFechaInversa(fechaInicio) +
            '&fecha_fin=' + convertirFechaInversa(fechaFin);

        FetchHelper.get(url)
            .then(renderizarGraficos)
            .catch(function () { Notify.error('Error al filtrar'); });
    }

    function handleClearFilters() {
        if (rango_fechas && rango_fechas.min && rango_fechas.max) {
            document.getElementById('fechaInicio').value = convertirFecha(rango_fechas.min);
            document.getElementById('fechaFin').value = convertirFecha(rango_fechas.max);
        }

        const columna = document.getElementById('columnaSelect').value;
        FetchHelper.get('/estadistica_de_paradas/datos?columna=' + columna)
            .then(renderizarGraficos);
    }

    function handleExportPDF() {
        const graficoDiv = document.getElementById('grafico');
        if (!window.PdfExporter || !window.PdfExporter.element) {
            Notify.error('PdfExporter no disponible');
            return;
        }

        const columna = document.getElementById('columnaSelect').value;
        PdfExporter.element(graficoDiv, {
            filename: 'estadistica_paradas_' + new Date().toISOString().split('T')[0] + '.pdf',
            title: 'Estadística de Paradas',
            backgroundColor: '#370d60',
            textColor: '#ffffff',
            orientation: 'landscape'
        });
    }

    function setupDrilldown() {
        // Se configura en el onClick del renderTorta
    }

    function mostrarModalDrillDown(categoria, columnaFiltro) {
        let modal = document.getElementById('modalDrillDown');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'modalDrillDown';
            modal.className = 'chart-drilldown-modal';
            modal.innerHTML = '<div class="chart-drilldown-content">' +
                '<div class="chart-drilldown-header">' +
                '<h2 id="modalTitulo">Detalle</h2>' +
                '<button class="chart-drilldown-close" onclick="cerrarModal()">&times;</button>' +
                '</div>' +
                '<div class="chart-drilldown-body">' +
                '<div id="graficoModal" style="width: 100%; height: 450px;"></div>' +
                '</div></div>';
            document.body.appendChild(modal);
        }

        document.getElementById('modalTitulo').textContent = 'Detalle: ' + categoria;
        modal.classList.add('active');

        const fechaInicio = document.getElementById('fechaInicio').value;
        const fechaFin = document.getElementById('fechaFin').value;

        let url = '/estadistica_de_paradas/drilldown?categoria=' + encodeURIComponent(categoria) +
            '&columna=' + encodeURIComponent(columnaFiltro);
        if (fechaInicio) url += '&fecha_inicio=' + convertirFechaInversa(fechaInicio);
        if (fechaFin) url += '&fecha_fin=' + convertirFechaInversa(fechaFin);

        FetchHelper.get(url)
            .then(function (datos) {
                const chart = GraficosEcharts.renderTorta('graficoModal', datos, {
                    titulo: 'Desglose de: ' + categoria,
                    titleColor: '#333',
                    useChartPalette: false,
                    onClick: function (params) {
                        const columnaSecundaria = columnaFiltro === 'Texto_codigo' ? 'Ubicac_tecnica' : 'Texto_codigo';
                        mostrarTablaDetalle(categoria, params.name, columnaFiltro, columnaSecundaria);
                    }
                });
            })
            .catch(function () {
                Notify.error('Error al cargar drilldown');
            });
    }

    function mostrarTablaDetalle(catPrincipal, catSecundaria, colPrincipal, colSecundaria) {
        let modalTabla = document.getElementById('modalTabla');
        if (!modalTabla) {
            modalTabla = document.createElement('div');
            modalTabla.id = 'modalTabla';
            modalTabla.className = 'chart-drilldown-modal';
            modalTabla.innerHTML = '<div class="chart-drilldown-content">' +
                '<div class="chart-drilldown-header">' +
                '<h2 id="modalTituloTabla">Registros Detallados</h2>' +
                '<button class="chart-drilldown-close" onclick="cerrarModalTabla()">&times;</button>' +
                '</div>' +
                '<div class="chart-drilldown-body">' +
                '<div style="display: flex; gap: 20px; margin-bottom: 15px; flex-wrap: wrap;">' +
                '<div id="contadorRegistros" class="chart-summary"></div>' +
                '<div id="totalDemoras" class="chart-summary"></div>' +
                '</div>' +
                '<div style="overflow-x: auto;">' +
                '<table id="tablaDetalle" class="chart-detail-table">' +
                '<thead id="tablaHead"></thead>' +
                '<tbody id="tablaBody"></tbody>' +
                '</table></div></div></div>';
            document.body.appendChild(modalTabla);
        }

        document.getElementById('modalTituloTabla').textContent = catPrincipal + ' → ' + catSecundaria;
        modalTabla.classList.add('active');

        const fechaInicio = document.getElementById('fechaInicio').value;
        const fechaFin = document.getElementById('fechaFin').value;

        let url = '/estadistica_de_paradas/detalle?categoria_principal=' + encodeURIComponent(catPrincipal) +
            '&categoria_secundaria=' + encodeURIComponent(catSecundaria) +
            '&columna_principal=' + encodeURIComponent(colPrincipal) +
            '&columna_secundaria=' + encodeURIComponent(colSecundaria);
        if (fechaInicio) url += '&fecha_inicio=' + convertirFechaInversa(fechaInicio);
        if (fechaFin) url += '&fecha_fin=' + convertirFechaInversa(fechaFin);

        FetchHelper.get(url)
            .then(function (datos) {
                document.getElementById('contadorRegistros').textContent = 'Total de registros: ' + datos.total;

                let totalHoras = 0;
                datos.registros.forEach(function (reg) {
                    totalHoras += parseFloat(reg.DurParada || 0);
                });
                const horas = Math.floor(totalHoras);
                const minutos = Math.round((totalHoras - horas) * 60);
                document.getElementById('totalDemoras').textContent =
                    'Total demoras: ' + String(horas).padStart(2, '0') + ':' + String(minutos).padStart(2, '0') + ' Hs';

                if (datos.registros.length === 0) {
                    document.getElementById('tablaBody').innerHTML =
                        '<tr><td colspan="12" style="text-align:center;">No hay datos</td></tr>';
                    return;
                }

                const columnas = ['Aviso', 'Fecha', 'Descripcion', 'Equipo', 'Ubicac_tecnica',
                    'DurParada', 'Aut_aviso', 'Por', 'Orden', 'Fin_desead', 'Texto_codigo'];

                document.getElementById('tablaHead').innerHTML = '<tr>' +
                    columnas.map(function (col) { return '<th>' + col.replace('_', ' ') + '</th>'; }).join('') + '</tr>';

                document.getElementById('tablaBody').innerHTML = datos.registros.map(function (reg) {
                    return '<tr>' + columnas.map(function (col) {
                        return '<td>' + (reg[col] || '') + '</td>';
                    }).join('') + '</tr>';
                }).join('');
            })
            .catch(function () {
                Notify.error('Error al cargar detalle');
            });
    }

    // Utilidades de fechas
    function convertirFecha(fecha) {
        if (!fecha) return '';
        const partes = fecha.split('.');
        if (partes.length === 3) return partes[2] + '-' + partes[1] + '-' + partes[0];
        return fecha;
    }

    function convertirFechaInversa(fecha) {
        if (!fecha) return '';
        const partes = fecha.split('-');
        if (partes.length === 3) return partes[2] + '.' + partes[1] + '.' + partes[0];
        return fecha;
    }

    // Cerrar modales (globales para onclick)
    window.cerrarModal = function () {
        const modal = document.getElementById('modalDrillDown');
        if (modal) modal.classList.remove('active');
    };

    window.cerrarModalTabla = function () {
        const modal = document.getElementById('modalTabla');
        if (modal) modal.classList.remove('active');
    };

    window.addEventListener('click', function (event) {
        if (event.target.id === 'modalDrillDown') window.cerrarModal();
        if (event.target.id === 'modalTabla') window.cerrarModalTabla();
    });

    Logger.success('Módulo EstadisticaParadas inicializado');
});