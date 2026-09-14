// templates/Aplic/listarot/static/js/listar_ot.js
/**
 * Listar OT — Gráfico 3D con fallback automático a 2D
 */

const coloresPaleta = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
    '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788',
    '#E74C3C', '#3498DB', '#9B59B6', '#F39C12', '#1ABC9C'
];

let chart = null;
let modoActual = null; // '3d' o '2d'

// Detectar si echarts-gl está disponible
function tiene3D() {
    return typeof echarts !== 'undefined' && 
           typeof echarts.gl !== 'undefined';
}

document.addEventListener('DOMContentLoaded', function () {
    inicializarSelectores();
    const selector = document.getElementById('columnaSelector');
    if (selector && selector.options.length > 1) {
        selector.selectedIndex = 1;
        generarGrafico();
    }
    
    // ResizeObserver
    const chartEl = document.getElementById('graficoTorta');
    if (chartEl && typeof ResizeObserver !== 'undefined') {
        const ro = new ResizeObserver(() => {
            if (chart) chart.resize();
        });
        ro.observe(chartEl);
    }
});

function inicializarSelectores() {
    const tabla = document.querySelector('.tabla-scroll table');
    if (!tabla) return;
    const headers = tabla.querySelectorAll('thead th');
    const selector = document.getElementById('columnaSelector');
    if (!selector) return;

    headers.forEach((th) => {
        const texto = th.textContent.trim();
        if (texto && texto !== '' && !texto.match(/^\d+$/)) {
            const option = document.createElement('option');
            option.value = texto;
            option.textContent = texto;
            selector.appendChild(option);
        }
    });
}

function generarGrafico() {
    const columna = document.getElementById('columnaSelector').value;
    if (!columna) {
        limpiarGrafico();
        return;
    }

    const tabla = document.querySelector('.tabla-scroll table tbody');
    if (!tabla) { limpiarGrafico(); return; }

    const headers = Array.from(document.querySelectorAll('.tabla-scroll table thead th'))
        .map(th => th.textContent.trim());
    const idxColumna = headers.indexOf(columna);
    if (idxColumna === -1) { limpiarGrafico(); return; }

    const contador = {};
    tabla.querySelectorAll('tr').forEach(fila => {
        const celda = fila.children[idxColumna];
        if (!celda) return;
        const valor = celda.textContent.trim();
        if (!valor || valor === '' || valor === 'sin valor' || 
            valor === '-' || valor === 'null') return;
        contador[valor] = (contador[valor] || 0) + 1;
    });

    const entradas = Object.entries(contador)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 15);

    if (entradas.length === 0) {
        limpiarGrafico();
        if (typeof Notify !== 'undefined') {
            Notify.warning(`No hay datos válidos para "${columna}"`);
        }
        return;
    }

    const datos = {
        categorias: entradas.map(e => e[0]),
        valores: entradas.map(e => e[1]),
        columna
    };

    // Intentar 3D, si falla usar 2D
    if (tiene3D()) {
        try {
            renderizar3D(datos);
            setModo('3d');
        } catch (e) {
            console.warn('3D falló, usando 2D:', e);
            renderizar2D(datos);
            setModo('2d');
        }
    } else {
        renderizar2D(datos);
        setModo('2d');
    }
}

function setModo(modo) {
    modoActual = modo;
    const indicator = document.getElementById('graficoModo');
    if (indicator) {
        indicator.className = 'modo-indicator modo-' + modo;
        indicator.textContent = modo === '3d' ? '🎮 3D' : '📊 2D';
    }
}

function limpiarGrafico() {
    if (chart) {
        chart.dispose();
        chart = null;
    }
}

// ============================================================
// MODO 3D — Barras 3D con echarts-gl
// ============================================================
function renderizar3D(datos) {
    const el = document.getElementById('graficoTorta');
    if (!el) return;
    if (chart) chart.dispose();
    
    chart = echarts.init(el);

    chart.setOption({
        title: {
            text: `Distribución 3D por ${datos.columna}`,
            left: 'center',
            top: 10,
            textStyle: {
                color: '#88c999',
                fontSize: window.innerWidth < 480 ? 14 : 18,
                fontWeight: 'bold'
            }
        },
        tooltip: {
            formatter: function (params) {
                return `<b>${params.value[0]}</b><br/>${params.value[2]} órdenes`;
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
                formatter: v => v.length > 12 ? v.substring(0, 12) + '…' : v
            }
        },
        yAxis3D: {
            type: 'category',
            data: ['Órdenes']
        },
        zAxis3D: {
            type: 'value'
        },
        grid3D: {
            boxWidth: 200,
            boxDepth: 80,
            viewControl: {
                alpha: 25,
                beta: 40,
                rotateSensitivity: 2,
                autoRotate: false
            },
            light: {
                main: { intensity: 1.5, shadow: true, shadowQuality: 'high' },
                ambient: { intensity: 0.4 }
            },
            environment: '#1a1a2e',
            postEffect: {
                enable: true,
                bloom: { enable: true, intensity: 0.1 }
            }
        },
        series: [{
            type: 'bar3D',
            data: datos.categorias.map((cat, i) => [cat, 'Órdenes', datos.valores[i]]),
            shading: 'realistic',
            realisticMaterial: { roughness: 0.3, metalness: 0.1 },
            label: {
                show: true,
                formatter: p => p.value[2],
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
                    return new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: coloresPaleta[params.dataIndex % coloresPaleta.length] },
                        { offset: 1, color: ajustarBrillo(coloresPaleta[params.dataIndex % coloresPaleta.length], -40) }
                    ]);
                },
                opacity: 0.95
            }
        }],
        backgroundColor: 'transparent'
    });

    configurarClick(datos);
}

// ============================================================
// MODO 2D — Torta Nightingale (fallback)
// ============================================================
function renderizar2D(datos) {
    const el = document.getElementById('graficoTorta');
    if (!el) return;
    if (chart) chart.dispose();
    
    chart = echarts.init(el);

    const tortaData = datos.categorias.map((cat, i) => ({
        name: cat,
        value: datos.valores[i],
        itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: coloresPaleta[i % coloresPaleta.length] },
                { offset: 1, color: ajustarBrillo(coloresPaleta[i % coloresPaleta.length], -30) }
            ]),
            shadowBlur: 20,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
    }));

    chart.setOption({
        title: {
            text: `Distribución por ${datos.columna}`,
            left: 'center',
            top: 10,
            textStyle: {
                color: '#88c999',
                fontSize: window.innerWidth < 480 ? 14 : 18,
                fontWeight: 'bold'
            }
        },
        tooltip: {
            trigger: 'item',
            formatter: '{b}<br/>{c} órdenes ({d}%)',
            backgroundColor: 'rgba(62, 45, 89, 0.95)',
            borderColor: '#88c999',
            borderWidth: 2,
            textStyle: { color: '#fff' }
        },
        legend: {
            orient: window.innerWidth < 768 ? 'horizontal' : 'vertical',
            [window.innerWidth < 768 ? 'bottom' : 'right']: 10,
            top: 'middle',
            textStyle: { color: '#fff', fontSize: window.innerWidth < 480 ? 9 : 11 },
            formatter: name => name.length > 20 ? name.substring(0, 20) + '…' : name
        },
        series: [{
            type: 'pie',
            roseType: 'area',
            radius: ['20%', '70%'],
            center: window.innerWidth < 768 ? ['50%', '45%'] : ['40%', '55%'],
            data: tortaData,
            label: {
                show: window.innerWidth >= 480,
                formatter: '{c}',
                color: '#fff',
                fontSize: 12,
                fontWeight: 'bold'
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
            animationType: 'scale',
            animationEasing: 'elasticOut'
        }],
        backgroundColor: 'transparent'
    });

    configurarClick(datos);
}

function configurarClick(datos) {
    if (!chart) return;
    chart.off('click');
    chart.on('click', function (params) {
        let nombre;
        if (modoActual === '3d' && params.value) {
            nombre = params.value[0];
        } else {
            nombre = params.name;
        }
        if (nombre) abrirModalFiltro(datos.columna, nombre);
    });
}

// ============================================================
// UTILIDADES
// ============================================================
function ajustarBrillo(color, porcentaje) {
    const num = parseInt(color.replace('#', ''), 16);
    const amt = Math.round(2.55 * porcentaje);
    const R = Math.max(0, Math.min(255, (num >> 16) + amt));
    const G = Math.max(0, Math.min(255, (num >> 8 & 0x00FF) + amt));
    const B = Math.max(0, Math.min(255, (num & 0x0000FF) + amt));
    return '#' + (0x1000000 + R * 0x10000 + G * 0x100 + B).toString(16).slice(1);
}

function cambiarArchivo() {
    const archivo = document.getElementById('archivoSelector').value;
    window.location.href = '/listar_ot?archivo=' + encodeURIComponent(archivo);
}

function buscar() {
    const filtro = document.getElementById('busqueda').value.toLowerCase();
    const filas = document.querySelectorAll('.tabla-scroll table tbody tr');
    filas.forEach(fila => {
        const texto = fila.textContent.toLowerCase();
        fila.style.display = texto.includes(filtro) ? '' : 'none';
    });
}

function abrirModalFiltro(columna, grupo) {
    const archivo = document.getElementById('archivoSelector').value;
    const url = `/filtro_torta/${encodeURIComponent(columna)}/${encodeURIComponent(grupo)}?archivo=${encodeURIComponent(archivo)}`;

    fetch(url)
        .then(resp => resp.text())
        .then(html => {
            document.getElementById('modalContainer').innerHTML = html;
            const modal = new bootstrap.Modal(document.getElementById('filtroTortaModal'));
            modal.show();
        })
        .catch(err => {
            console.error('Error al cargar modal:', err);
            if (typeof Notify !== 'undefined') {
                Notify.error('Error al cargar los detalles');
            }
        });
}