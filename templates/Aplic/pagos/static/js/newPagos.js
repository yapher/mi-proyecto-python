/**
 * newPagos.js - Modal de Pagos
 * Usa SelectoresNivel reutilizable para cargar rubros desde /api/rubro_arbol
 * ✅ Errores visibles al usuario (Notify)
 * ✅ Tras guardar, el filtro salta al mes del pago para que se vea
 */
let pagoEnEdicion = null;
let selectoresRubros = null;
let guardando = false;

// ------------------------ Utilidades ------------------------
function ultimoDiaDelMes(anio, mes) {
    return new Date(anio, mes, 0).getDate(); // mes: 1-12
}

// Suma n meses a 'YYYY-MM-DD' sin desbordar (31/01 + 1 mes = 28/02)
function sumarMeses(fechaISO, n) {
    const [y, m, d] = fechaISO.split('-').map(Number);
    const total = (m - 1) + n;
    const ny = y + Math.floor(total / 12);
    const nm = (total % 12) + 1;
    const nd = Math.min(d, ultimoDiaDelMes(ny, nm));
    return `${ny}-${String(nm).padStart(2, '0')}-${String(nd).padStart(2, '0')}`;
}

async function enviarJSON(url, method, body) {
    const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
        credentials: 'same-origin'
    });

    if (res.redirected) {
        throw new Error('Tu sesión expiró. Volvé a iniciar sesión.');
    }

    let data = {};
    try { data = await res.json(); } catch (e) { /* respuesta sin JSON */ }

    if (!res.ok) {
        throw new Error(data.error || data.msg || `Error del servidor (HTTP ${res.status})`);
    }
    return data;
}

// Mueve el filtro Año/Mes al mes del pago guardado y recarga la tabla
function irAlMesDe(vencimiento) {
    const partes = String(vencimiento || '').split('-');
    if (partes.length >= 2) {
        document.getElementById('filtroAnio').value = parseInt(partes[0], 10);
        document.getElementById('filtroMes').value = parseInt(partes[1], 10);
    }
    if (typeof filtrarPorMes === 'function') filtrarPorMes();
}

// ------------------------ Guardar ------------------------
async function guardarPago() {
    if (guardando) return;

    let texto = selectoresRubros ? selectoresRubros.obtenerRutaPadre() : '';
    if (!texto && pagoEnEdicion) texto = pagoEnEdicion.rubro || '';

    let categoria, subcategoria;
    if (texto && texto.includes('.')) {
        [categoria, subcategoria] = texto.split('.');
    } else {
        categoria = texto || '';
        subcategoria = null;
    }

    const tipoForm = document.getElementById('tipo').value || 'único';
    const cuotas = Math.max(parseInt(document.getElementById('cuotas').value, 10) || 1, 1);
    const importeTotal = parseFloat(document.getElementById('importe').value);
    let vencimiento = document.getElementById('vencimiento').value;

    if (!categoria) {
        Notify.warning('Seleccioná un rubro');
        return;
    }
    if (isNaN(importeTotal) || importeTotal <= 0) {
        Notify.warning('Ingresá un importe válido (mayor a 0)');
        return;
    }

    if (!vencimiento) vencimiento = new Date().toISOString().split('T')[0];
    const descripcion = subcategoria || document.getElementById('descripcion').value || '';

    guardando = true;
    try {
        if (pagoEnEdicion) {
            // En edición se conserva el tipo original (único / cuota)
            const pagoEditar = {
                rubro: categoria,
                descripcion: descripcion,
                importe: importeTotal,
                tipo: pagoEnEdicion.tipo || tipoForm,
                vencimiento: vencimiento,
                pagado: pagoEnEdicion.pagado
            };
            await enviarJSON(`/pagos/editar/${pagoEnEdicion.id}`, 'PUT', pagoEditar);

            pagoEnEdicion = null;
            cerrarModal();
            mostrarFormulario(null);
            irAlMesDe(vencimiento);
            Notify.success('Editado con éxito');
        } else {
            const pagos = [];

            if (tipoForm === 'cuotas') {
                const importeCuota = Math.floor((importeTotal / cuotas) * 100) / 100;
                let acumulado = 0;
                for (let i = 0; i < cuotas; i++) {
                    // La última cuota absorbe la diferencia de centavos
                    const imp = (i === cuotas - 1)
                        ? parseFloat((importeTotal - acumulado).toFixed(2))
                        : importeCuota;
                    acumulado += imp;
                    pagos.push({
                        rubro: categoria,
                        descripcion: descripcion,
                        importe: imp,
                        tipo: 'cuota',
                        cuotas: cuotas,
                        cuota_numero: i + 1,
                        cuota_total: cuotas,
                        vencimiento: sumarMeses(vencimiento, i),
                        pagado: false
                    });
                }
            } else {
                pagos.push({
                    rubro: categoria,
                    descripcion: descripcion,
                    importe: importeTotal,
                    tipo: 'único',
                    vencimiento: vencimiento,
                    pagado: false
                });
            }

            await enviarJSON('/pagos/agregar', 'POST', pagos);

            cerrarModal();
            mostrarFormulario(null);
            irAlMesDe(pagos[0].vencimiento);
            Notify.success(pagos.length > 1
                ? `${pagos.length} cuotas creadas con éxito`
                : 'Pago creado con éxito');
        }
    } catch (err) {
        console.error('Error al guardar pago:', err);
        Notify.error(err.message || 'No se pudo guardar el pago');
    } finally {
        guardando = false;
    }
}

// ------------------------ Formulario ------------------------
function mostrarFormulario(p = null) {
    const btnCancelar = document.querySelector('#agregarModal .btn-cancelar');

    if (p) {
        pagoEnEdicion = p;
        document.getElementById('pagoId').value = p.id || '';
        document.getElementById('importe').value = p.importe || '';
        document.getElementById('tipo').value = (p.tipo === 'cuota') ? 'cuotas' : (p.tipo || 'único');
        document.getElementById('cuotas').value = p.cuota_total || p.cuotas || '';
        document.getElementById('vencimiento').value = p.vencimiento || '';
        document.getElementById('descripcion').value = p.descripcion || '';
        if (btnCancelar) btnCancelar.style.display = 'inline';

        let rutaCompleta = p.rubro;
        if (p.descripcion) rutaCompleta += '.' + p.descripcion;
        if (selectoresRubros) selectoresRubros.renderSelectores(rutaCompleta);
    } else {
        pagoEnEdicion = null;
        document.getElementById('pagoId').value = '';
        document.getElementById('importe').value = '';
        document.getElementById('descripcion').value = '';
        document.getElementById('tipo').value = 'único';
        document.getElementById('cuotas').value = '';

        const hoy = new Date();
        const yyyy = hoy.getFullYear();
        const mm = String(hoy.getMonth() + 1).padStart(2, '0');
        const dd = String(hoy.getDate()).padStart(2, '0');
        document.getElementById('vencimiento').value = `${yyyy}-${mm}-${dd}`;

        if (selectoresRubros) selectoresRubros.renderSelectores();
        if (btnCancelar) btnCancelar.style.display = 'none';
    }
}

function cancelar() { mostrarFormulario(null); }

function abrirModal() {
    const modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('agregarModal'));
    modal.show();
}

function cerrarModal() {
    const el = document.getElementById('agregarModal');
    const modal = bootstrap.Modal.getInstance(el);
    if (modal) modal.hide();
}

// Inicializar selectores de rubros desde /api/rubro_arbol
window.addEventListener('DOMContentLoaded', () => {
    Logger.moduleInit('NewPagos');
    selectoresRubros = new SelectoresNivel({
        containerId: 'nivelesContainer',
        apiUrl: '/api/rubro_arbol',
        separador: '.',
        loggerPrefix: '[NewPagos:Rubros]',
        onLoaded: (arbol) => {
            Logger.info('Rubros cargados correctamente', { cantidad: arbol.length });
        }
    });
});