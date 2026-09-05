/**
 * newPagos.js - Modal de Pagos
 * Usa SelectoresNivel reutilizable para cargar rubros desde /api/rubro_arbol
 * ✅ NOTIFICACIONES UNIFICADAS: usa Notify global
 */
let pagoEnEdicion = null;
let selectoresRubros = null;

// ------------------------ Funciones existentes ------------------------
function guardarPago() {
    let texto = selectoresRubros.obtenerRutaPadre();
    if (!texto && pagoEnEdicion) texto = pagoEnEdicion.rubro || '';
    let categoria, subcategoria;
    if (texto && texto.includes(".")) {
        [categoria, subcategoria] = texto.split(".");
    } else {
        categoria = texto || '';
        subcategoria = null;
    }

    const tipo = document.getElementById('tipo').value;
    const cuotas = parseInt(document.getElementById('cuotas').value) || 1;
    const importeTotal = parseFloat(document.getElementById('importe').value);
    let vencimiento = document.getElementById('vencimiento').value;

    if (!categoria || isNaN(importeTotal) || importeTotal <= 0) {
        // ✅ UNIFICADO: usa Notify en lugar de Noty directo
        Notify.warning('Debe seleccionar un rubro y un importe válido');
        return;
    }

    if (!vencimiento) vencimiento = new Date().toISOString().split('T')[0];
    const descripcion = subcategoria || document.getElementById('descripcion').value || "";

    if (pagoEnEdicion) {
        const pagoEditar = {
            id: pagoEnEdicion.id,
            rubro: categoria,
            descripcion: descripcion,
            importe: importeTotal,
            tipo: tipo,
            vencimiento: vencimiento,
            pagado: pagoEnEdicion.pagado
        };
        fetch(`/pagos/editar/${pagoEnEdicion.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(pagoEditar)
        })
        .then(response => {
            if (!response.ok) throw new Error('HTTP error');
            return response.json().catch(() => ({}));
        })
        .then(() => {
            filtrarPorMes();
            mostrarFormulario(null);
            cerrarModal();
            pagoEnEdicion = null;
            // ✅ UNIFICADO
            Notify.success('Editado con éxito');
        })
        .catch(err => console.error("Error real al guardar pago:", err));
    } else {
        let pagos = [];
        if (tipo === "cuotas") {
            const importeCuota = parseFloat((importeTotal / cuotas).toFixed(2));
            let fecha = new Date(vencimiento);
            for (let i = 0; i < cuotas; i++) {
                pagos.push({
                    id: Date.now() + i,
                    rubro: categoria,
                    descripcion: descripcion,
                    importe: importeCuota,
                    tipo: "cuota",
                    cuota_numero: i + 1,
                    cuota_total: cuotas,
                    vencimiento: fecha.toISOString().split('T')[0],
                    pagado: false
                });
                fecha.setMonth(fecha.getMonth() + 1);
            }
        } else {
            pagos.push({
                id: Date.now(),
                rubro: categoria,
                descripcion: descripcion,
                importe: importeTotal,
                tipo: "único",
                vencimiento: vencimiento,
                pagado: false
            });
        }
        fetch('/pagos/agregar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(pagos)
        })
        .then(response => {
            if (!response.ok) throw new Error('HTTP error');
            return response.json().catch(() => ({}));
        })
        .then(() => {
            filtrarPorMes();
            mostrarFormulario(null);
            cerrarModal();
            // ✅ UNIFICADO
            Notify.success('Pago creado con éxito');
        })
        .catch(err => console.error("Error real al crear pago:", err));
    }
}

// Mostrar formulario
function mostrarFormulario(p = null) {
    if (p) {
        pagoEnEdicion = p;
        document.getElementById('pagoId').value = p.id || '';
        document.getElementById('importe').value = p.importe || '';
        document.getElementById('tipo').value = p.tipo || 'único';
        document.getElementById('cuotas').value = p.cuotas || '';
        document.getElementById('vencimiento').value = p.vencimiento || '';
        document.getElementById('descripcion').value = p.descripcion || '';
        document.querySelector(".btn-cancelar").style.display = "inline";
        let rutaCompleta = p.rubro;
        if (p.descripcion) rutaCompleta += "." + p.descripcion;
        if (selectoresRubros) {
            selectoresRubros.renderSelectores(rutaCompleta);
        }
    } else {
        pagoEnEdicion = null;
        document.getElementById('pagoId').value = '';
        document.querySelectorAll('#formulario input, #formulario select').forEach(i => i.value = '');
        const hoy = new Date();
        const yyyy = hoy.getFullYear();
        const mm = String(hoy.getMonth() + 1).padStart(2, '0');
        const dd = String(hoy.getDate()).padStart(2, '0');
        document.getElementById('vencimiento').value = `${yyyy}-${mm}-${dd}`;
        if (selectoresRubros) {
            selectoresRubros.renderSelectores();
        }
        document.querySelector(".btn-cancelar").style.display = "none";
    }
}

// Funciones existentes
function cancelar() { mostrarFormulario(null); }
function abrirModal() { const modal = new bootstrap.Modal(document.getElementById('agregarModal')); modal.show(); }
function cerrarModal() { const modal = bootstrap.Modal.getInstance(document.getElementById('agregarModal'))?.hide(); }

// Inicializar selectores de rubros desde /api/rubro_arbol (NO /api/menu_arbol)
window.addEventListener('DOMContentLoaded', () => {
    Logger.moduleInit('NewPagos');
    selectoresRubros = new SelectoresNivel({
        containerId: 'nivelesContainer',
        apiUrl: '/api/rubro_arbol',  // ← CLAVE: cargar RUBROS, no menú
        separador: '.',
        loggerPrefix: '[NewPagos:Rubros]',
        onLoaded: (arbol) => {
            Logger.info('Rubros cargados correctamente', { cantidad: arbol.length });
        }
    });
});