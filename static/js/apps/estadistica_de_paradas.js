// estadistica_de_paradas.js

const datos_iniciales = window.datos_iniciales;

// Paleta de colores vibrantes para los gráficos
const coloresPaleta = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
    '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788',
    '#E74C3C', '#3498DB', '#9B59B6', '#F39C12', '#1ABC9C'
];

function obtenerColor(index) {
    return coloresPaleta[index % coloresPaleta.length];
}

function renderizarGraficos(datos) {
    console.log('Renderizando gráficos con datos:', datos);
    
    if (!datos || !datos.categorias || !datos.valores) {
        console.error('Datos inválidos para renderizar');
        return;
    }
    
    // Gráfico de Torta 3D
    let tortaChart = echarts.init(document.getElementById('graficoTorta'));
    let tortaData = datos.categorias.map((cat, i) => ({
        name: cat,
        value: datos.valores[i],
        itemStyle: { color: obtenerColor(i) }
    }));

    let tortaOption = {
        title: {
            text: 'Distribución por Categoría (Torta 3D)',
            left: 'center',
            top: 20,
            textStyle: { 
                color: 'white',
                fontSize: 18,
                fontWeight: 'bold'
            }
        },
        tooltip: { 
            trigger: 'item',
            formatter: '{b}: {c} ({d}%)'
        },
        legend: {
            orient: 'vertical',
            right: 10,
            top: 'center',
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
            label: {
                show: true,
                formatter: '{c}',
                color: 'white',
                fontSize: 12,
                fontWeight: 'bold'
            },
            labelLine: {
                show: true,
                lineStyle: { color: 'white' }
            },
            itemStyle: {
                borderRadius: 10,
                borderColor: '#1a1a2e',
                borderWidth: 3,
                shadowBlur: 10,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
            },
            emphasis: {
                itemStyle: {
                    shadowBlur: 20,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(255, 255, 255, 0.5)'
                }
            }
        }],
        backgroundColor: '#1a1a2e'
    };
    tortaChart.setOption(tortaOption);

    // Gráfico de Barras 3D
    let barraChart = echarts.init(document.getElementById('graficoBarras'));
    let barraOption = {
        title: {
            text: 'Cantidad por Categoría (Barras 3D)',
            left: 'center',
            top: 20,
            textStyle: { 
                color: 'white',
                fontSize: 18,
                fontWeight: 'bold'
            }
        },
        tooltip: {
            formatter: function(params) {
                return params.value[0] + ': ' + params.value[2];
            }
        },
        xAxis3D: {
            type: 'category',
            data: datos.categorias,
            axisLabel: {
                color: '#fff',
                fontSize: 10,
                interval: 0,
                rotate: 45,
                formatter: function(value) {
                    return value.length > 15 ? value.substring(0, 15) + '...' : value;
                }
            },
            axisLine: { lineStyle: { color: '#fff' } }
        },
        yAxis3D: {
            type: 'category',
            data: ['Cantidad'],
            axisLabel: { color: '#fff' },
            axisLine: { lineStyle: { color: '#fff' } }
        },
        zAxis3D: {
            type: 'value',
            axisLabel: { color: '#fff' },
            axisLine: { lineStyle: { color: '#fff' } }
        },
        grid3D: {
            boxWidth: 200,
            boxDepth: 80,
            light: {
                main: { 
                    intensity: 1.5,
                    shadow: true
                },
                ambient: { 
                    intensity: 0.4 
                }
            },
            viewControl: { 
                alpha: 30,
                beta: 45,
                distance: 250,
                autoRotate: false
            },
            environment: '#1a1a2e'
        },
        series: [{
            type: 'bar3D',
            data: datos.categorias.map((cat, i) => [cat, 'Cantidad', datos.valores[i]]),
            shading: 'realistic',
            label: {
                show: true,
                formatter: function (params) {
                    return params.value[2];
                },
                textStyle: { 
                    color: '#fff',
                    fontSize: 12,
                    fontWeight: 'bold',
                    borderWidth: 1,
                    borderColor: '#000',
                    backgroundColor: 'rgba(0,0,0,0.5)',
                    padding: 3,
                    borderRadius: 3
                }
            },
            itemStyle: {
                color: function (params) {
                    return obtenerColor(params.dataIndex);
                },
                opacity: 0.9
            },
            emphasis: {
                itemStyle: {
                    color: '#fff'
                },
                label: {
                    textStyle: {
                        fontSize: 14
                    }
                }
            }
        }],
        backgroundColor: '#1a1a2e'
    };
    barraChart.setOption(barraOption);

    // Redimensionar gráficos al cambiar tamaño de ventana
    window.addEventListener('resize', function() {
        tortaChart.resize();
        barraChart.resize();
    });
}

// Renderizar gráficos iniciales
renderizarGraficos(datos_iniciales);

// Cargar archivo desde explorador
if (document.getElementById('archivoInput')) {
    document.getElementById('archivoInput').addEventListener('change', function(e) {
        const archivo = e.target.files[0];
        
        if (!archivo) return;
        
        // Mostrar nombre del archivo
        document.getElementById('nombreArchivo').textContent = `Archivo: ${archivo.name}`;
        
        // Crear FormData para enviar el archivo
        const formData = new FormData();
        formData.append('archivo', archivo);
        
        // Mostrar mensaje de carga
        console.log('Cargando archivo...');
        
        // Enviar archivo al servidor
        fetch('/estadistica_de_paradas/cargar_archivo', {
            method: 'POST',
            body: formData
        })
        .then(resp => {
            if (!resp.ok) {
                throw new Error('Error en la respuesta del servidor');
            }
            return resp.json();
        })
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
                return;
            }
            
            console.log(`Archivo cargado exitosamente. Total de avisos: ${data.total_avisos}`);
            
            // Renderizar gráficos con los nuevos datos
            renderizarGraficos({
                categorias: data.categorias,
                valores: data.valores
            });
            
            alert(`✓ Archivo cargado exitosamente!\nTotal de registros: ${data.total_avisos}`);
        })
        .catch(err => {
            console.error('Error al cargar archivo:', err);
            alert('Error al cargar el archivo. Verifica que el formato sea correcto.');
        });
    });
}

// Filtro por columna
if (document.getElementById('columnaSelect')) {
    document.getElementById('columnaSelect').addEventListener('change', function () {
        const seleccion = this.value;
        console.log('Columna seleccionada:', seleccion);
        
        fetch(`/estadistica_de_paradas/datos?columna=${encodeURIComponent(seleccion)}`)
            .then(resp => {
                if (!resp.ok) {
                    throw new Error('Error en la respuesta del servidor');
                }
                return resp.json();
            })
            .then(datos => {
                console.log('Datos recibidos:', datos);
                if (datos.categorias && datos.valores) {
                    renderizarGraficos(datos);
                } else {
                    console.error('Datos inválidos recibidos');
                }
            })
            .catch(err => {
                console.error('Error al cargar datos:', err);
                alert('Error al cargar los datos. Revisa la consola para más detalles.');
            });
    });
}

// Exportar a PDF
if (document.getElementById('exportarPdf')) {
    document.getElementById('exportarPdf').addEventListener('click', () => {
        const graficoDiv = document.getElementById('grafico');
        html2canvas(graficoDiv, { 
            backgroundColor: '#370d60',
            scale: 2
        }).then(canvas => {
            const imgData = canvas.toDataURL('image/png');
            const { jsPDF } = window.jspdf;
            const pdf = new jsPDF({
                orientation: 'landscape',
                unit: 'px',
                format: [canvas.width / 2 + 60, canvas.height / 2 + 100]
            });

            // Agregar título y fecha
            pdf.setFontSize(22);
            pdf.setTextColor(255, 255, 255);
            pdf.setFillColor(55, 13, 96);
            pdf.rect(0, 0, pdf.internal.pageSize.width, pdf.internal.pageSize.height, 'F');
            
            pdf.setTextColor(255, 255, 255);
            pdf.text('Estadística de Paradas', 30, 40);
            
            pdf.setFontSize(12);
            const columnaSeleccionada = document.getElementById('columnaSelect').value;
            pdf.text(`Agrupado por: ${columnaSeleccionada.replace('_', ' ')}`, 30, 60);
            pdf.text(`Fecha: ${new Date().toLocaleDateString('es-AR')}`, 30, 75);

            // Agregar imagen
            pdf.addImage(imgData, 'PNG', 30, 90, canvas.width / 2, canvas.height / 2);
            
            pdf.save(`estadistica_paradas_${new Date().toISOString().split('T')[0]}.pdf`);
        }).catch(err => {
            console.error('Error al generar PDF:', err);
            alert('Error al generar el PDF. Por favor intente nuevamente.');
        });
    });
}

// Variable global para columna actual
let columnaActual = 'Texto_codigo';

// Actualizar columnaActual cuando cambia el select
const selectOriginal = document.getElementById('columnaSelect');
if (selectOriginal) {
    selectOriginal.addEventListener('change', function() {
        columnaActual = this.value;
    });
}

// Agregar evento de clic al gráfico de torta
const graficoTortaElement = document.getElementById('graficoTorta');
if (graficoTortaElement) {
    const tortaChartInstance = echarts.getInstanceByDom(graficoTortaElement);
    if (tortaChartInstance) {
        tortaChartInstance.on('click', function(params) {
            mostrarModalDrillDown(params.name, columnaActual);
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
            </div>
        `;
        document.body.appendChild(modal);
    }

    document.getElementById('modalTitulo').textContent = `Detalle: ${categoria}`;
    modal.style.display = 'flex';

   // Tomar las fechas seleccionadas actualmente
    const fechaInicio = document.getElementById('fechaInicio').value;
    const fechaFin = document.getElementById('fechaFin').value;

    fetch(`/estadistica_de_paradas/drilldown?categoria=${encodeURIComponent(categoria)}&columna=${encodeURIComponent(columnaFiltro)}&fecha_inicio=${encodeURIComponent(convertirFechaInversa(fechaInicio))}&fecha_fin=${encodeURIComponent(convertirFechaInversa(fechaFin))}`)

        .then(resp => resp.json())
        .then(datos => {
            let modalChart = echarts.init(document.getElementById('graficoModal'));
            
            let tortaData = datos.categorias.map((cat, i) => ({
                name: cat,
                value: datos.valores[i],
                itemStyle: { color: obtenerColor(i) }
            }));

            modalChart.setOption({
                title: {
                    text: `Desglose de: ${categoria}`,
                    left: 'center',
                    textStyle: { color: '#333', fontSize: 16 }
                },
                tooltip: { 
                    trigger: 'item',
                    formatter: '{b}: {c} ({d}%)'
                },
                legend: {
                    orient: 'vertical',
                    right: 10,
                    top: 'center'
                },
                series: [{
                    type: 'pie',
                    radius: ['30%', '60%'],
                    data: tortaData,
                    label: { show: true, formatter: '{b}: {c}' }
                }],
                backgroundColor: '#f5f5f5'
            });
        });
}

function cerrarModal() {
    const modal = document.getElementById('modalDrillDown');
    if (modal) modal.style.display = 'none';
}

window.onclick = function(event) {
    const modal = document.getElementById('modalDrillDown');
    if (event.target === modal) cerrarModal();
}

// Variable para rastrear la categoría principal del primer modal
let categoriaPrincipal = '';
let columnaPrincipal = '';

// Modificar la función mostrarModalDrillDown existente para guardar contexto
const mostrarModalDrillDownOriginal = mostrarModalDrillDown;
mostrarModalDrillDown = function(categoria, columnaFiltro) {
    categoriaPrincipal = categoria;
    columnaPrincipal = columnaFiltro;
    mostrarModalDrillDownOriginal(categoria, columnaFiltro);
    
    // Agregar evento de clic al gráfico del modal después de renderizar
    setTimeout(() => {
        const modalChartElement = document.getElementById('graficoModal');
        if (modalChartElement) {
            const modalChartInstance = echarts.getInstanceByDom(modalChartElement);
            if (modalChartInstance) {
                modalChartInstance.on('click', function(params) {
                    const columnaSecundaria = columnaPrincipal === 'Texto_codigo' ? 'Ubicac_tecnica' : 'Texto_codigo';
                    mostrarTablaDetalle(categoriaPrincipal, params.name, columnaPrincipal, columnaSecundaria);
                });
            }
        }
    }, 500);
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
                        <div id="contadorRegistros" style="font-weight: bold; color: #667eea; background: #e3f2fd; padding: 10px 15px; border-radius: 8px; border-left: 4px solid #667eea;"></div>
                        <div id="totalDemoras" style="font-weight: bold; color: #f44336; background: #ffebee; padding: 10px 15px; border-radius: 8px; border-left: 4px solid #f44336;"></div>
                    </div>
                    <div style="overflow-x: auto;">
                        <table id="tablaDetalle" class="tabla-detalle">
                            <thead id="tablaHead"></thead>
                            <tbody id="tablaBody"></tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modalTabla);
    }

    document.getElementById('modalTituloTabla').textContent = `${catPrincipal} → ${catSecundaria}`;
    modalTabla.style.display = 'flex';

    // Tomar las fechas seleccionadas actualmente
    const fechaInicio = document.getElementById('fechaInicio').value;
    const fechaFin = document.getElementById('fechaFin').value;

    // Enviar también el rango de fechas al backend
    fetch(`/estadistica_de_paradas/detalle?categoria_principal=${encodeURIComponent(catPrincipal)}&categoria_secundaria=${encodeURIComponent(catSecundaria)}&columna_principal=${encodeURIComponent(colPrincipal)}&columna_secundaria=${encodeURIComponent(colSecundaria)}&fecha_inicio=${encodeURIComponent(convertirFechaInversa(fechaInicio))}&fecha_fin=${encodeURIComponent(convertirFechaInversa(fechaFin))}`)

        .then(resp => resp.json())
        .then(datos => {
            document.getElementById('contadorRegistros').textContent = `Total de registros: ${datos.total}`;
            
            // Calcular suma de DurParada y convertir a HH:MM
            let totalHoras = 0;
            datos.registros.forEach(reg => {
                const duracion = parseFloat(reg.DurParada || 0);
                totalHoras += duracion;
            });
            
            // Convertir decimal a HH:MM
            const horas = Math.floor(totalHoras);
            const minutos = Math.round((totalHoras - horas) * 60);
            const horasStr = String(horas).padStart(2, '0');
            const minutosStr = String(minutos).padStart(2, '0');
            
            document.getElementById('totalDemoras').textContent = `Total demoras: ${horasStr}:${minutosStr} Hs`;
            
            if (datos.registros.length === 0) {
                document.getElementById('tablaBody').innerHTML = '<tr><td colspan="12" style="text-align:center;">No hay datos</td></tr>';
                return;
            }

            // Generar encabezados
            const columnas = ['Aviso', 'Fecha', 'Descripcion', 'Equipo', 'Ubicac_tecnica', 'DurParada', 'Aut_aviso', 'Por', 'Orden', 'Fin_desead', 'Texto_codigo'];
            const encabezados = columnas.map(col => `<th>${col.replace('_', ' ')}</th>`).join('');
            document.getElementById('tablaHead').innerHTML = `<tr>${encabezados}</tr>`;

            // Generar filas
            const filas = datos.registros.map(reg => {
                const celdas = columnas.map(col => `<td>${reg[col] || ''}</td>`).join('');
                return `<tr>${celdas}</tr>`;
            }).join('');
            document.getElementById('tablaBody').innerHTML = filas;
        })
        .catch(err => {
            console.error('Error al cargar detalle:', err);
            alert('Error al cargar los datos detallados.');
        });
}

function cerrarModalTabla() {
    const modal = document.getElementById('modalTabla');
    if (modal) modal.style.display = 'none';
}

// Cerrar modal tabla al hacer clic fuera
window.addEventListener('click', function(event) {
    const modalTabla = document.getElementById('modalTabla');
    if (event.target === modalTabla) cerrarModalTabla();
});

// Configurar rangos de fechas iniciales
if (window.rango_fechas && window.rango_fechas.min && window.rango_fechas.max) {
    document.getElementById('fechaInicio').value = convertirFecha(window.rango_fechas.min);
    document.getElementById('fechaFin').value = convertirFecha(window.rango_fechas.max);
    document.getElementById('fechaInicio').min = convertirFecha(window.rango_fechas.min);
    document.getElementById('fechaInicio').max = convertirFecha(window.rango_fechas.max);
    document.getElementById('fechaFin').min = convertirFecha(window.rango_fechas.min);
    document.getElementById('fechaFin').max = convertirFecha(window.rango_fechas.max);
}

// Función para convertir fecha DD.MM.YYYY a YYYY-MM-DD
function convertirFecha(fecha) {
    if (!fecha) return '';
    const partes = fecha.split('.');
    if (partes.length === 3) {
        return `${partes[2]}-${partes[1]}-${partes[0]}`;
    }
    return fecha;
}

// Función para convertir fecha YYYY-MM-DD a DD.MM.YYYY
function convertirFechaInversa(fecha) {
    if (!fecha) return '';
    const partes = fecha.split('-');
    if (partes.length === 3) {
        return `${partes[2]}.${partes[1]}.${partes[0]}`;
    }
    return fecha;
}

// Actualizar rangos al cargar archivo
const archivoInputOriginal = document.getElementById('archivoInput');
archivoInputOriginal.addEventListener('change', function(e) {
    const archivo = e.target.files[0];
    if (!archivo) return;
    
    document.getElementById('nombreArchivo').textContent = `Archivo: ${archivo.name}`;
    
    const formData = new FormData();
    formData.append('archivo', archivo);
    
    fetch('/estadistica_de_paradas/cargar_archivo', {
        method: 'POST',
        body: formData
    })
    .then(resp => resp.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        // Actualizar rangos de fechas
        if (data.rango_fechas && data.rango_fechas.min && data.rango_fechas.max) {
            const fechaMin = convertirFecha(data.rango_fechas.min);
            const fechaMax = convertirFecha(data.rango_fechas.max);
            
            document.getElementById('fechaInicio').value = fechaMin;
            document.getElementById('fechaFin').value = fechaMax;
            document.getElementById('fechaInicio').min = fechaMin;
            document.getElementById('fechaInicio').max = fechaMax;
            document.getElementById('fechaFin').min = fechaMin;
            document.getElementById('fechaFin').max = fechaMax;
        }
        
        renderizarGraficos({
            categorias: data.categorias,
            valores: data.valores
        });
        
        alert(`✓ Archivo cargado!\nTotal: ${data.total_avisos}\nRango: ${data.rango_fechas.min} - ${data.rango_fechas.max}`);
    })
    .catch(err => {
        console.error('Error:', err);
        alert('Error al cargar el archivo.');
    });
});

// Filtrar por fechas
document.getElementById('btnFiltrarFechas').addEventListener('click', function() {
    const fechaInicio = convertirFechaInversa(document.getElementById('fechaInicio').value);
    const fechaFin = convertirFechaInversa(document.getElementById('fechaFin').value);
    
    if (!fechaInicio || !fechaFin) {
        alert('Selecciona ambas fechas');
        return;
    }
    
    const columna = document.getElementById('columnaSelect').value;
    
    fetch(`/estadistica_de_paradas/datos?columna=${columna}&fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`)
        .then(resp => resp.json())
        .then(datos => {
            renderizarGraficos(datos);
        })
        .catch(err => {
            console.error('Error:', err);
            alert('Error al filtrar por fechas');
        });
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