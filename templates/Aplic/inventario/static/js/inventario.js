// templates/Aplic/inventario/static/js/inventario.js
/**
 * inventario.js — Lógica de Inventario + Gestión de Almacenes
 * Usa ArbolCRUD reutilizable para el CRUD de almacenes
 */
document.addEventListener('DOMContentLoaded', function () {
    if (typeof Logger !== 'undefined') {
        Logger.moduleInit('Inventario');
    }

    // ============================================================
    // TABS: asegurar que el tab activo se muestre correctamente
    // ============================================================
    const activeTab = document.querySelector('.inventario-tabs .nav-link.active');
    if (activeTab) {
        const target = activeTab.getAttribute('data-bs-target');
        if (target) {
            const pane = document.querySelector(target);
            if (pane) {
                pane.classList.add('show', 'active');
            }
        }
    }

    // ============================================================
    // GESTIÓN DE ALMACENES (CRUD con ArbolCRUD)
    // ============================================================
    const modalAlmacenesEl = document.getElementById('modalGestionAlmacenes');
    let almacenesCrud = null;

    if (modalAlmacenesEl) {
        // Inicializar ArbolCRUD cuando se abre el modal
        modalAlmacenesEl.addEventListener('shown.bs.modal', function () {
            if (!almacenesCrud) {
                almacenesCrud = new ArbolCRUD({
                    apiArbol: "/api/inventario/almacenes_arbol",
                    apiCrud: "/api/inventario/almacenes",
                    claveHijos: "subcrear_almacenes",
                    campoRuta: "ruta_crear_almacenes",
                    nombreItem: "almacén",
                    selectoresId: "almacenesNivelesContainer",
                    tablaId: "almacenesTabla",
                    camposForm: {
                        nombre: "almacenNombre",
                        emoji: "almacenEmoji",
                        ruta: "almacenRuta",
                        original: "almacenRutaOriginal"
                    },
                    botones: {
                        agregar: "#btnAlmacenAgregar",
                        editar: "#btnAlmacenEditar",
                        cancelar: "#btnAlmacenCancelar"
                    },
                    mensajeExito: "Almacén guardado correctamente",
                    onInit: function (crud) {
                        Logger.info('ArbolCRUD de almacenes inicializado');
                    }
                });
            } else {
                // Recargar datos si ya estaba inicializado
                almacenesCrud.init();
            }
        });

        // Al cerrar el modal, recargar la página para reflejar cambios en los tabs
        modalAlmacenesEl.addEventListener('hidden.bs.modal', function () {
            // Solo recargar si se hicieron cambios
            if (almacenesCrud && almacenesCrud._cambiosRealizados) {
                almacenesCrud._cambiosRealizados = false;
                window.location.reload();
            }
        });
    }

    // ============================================================
    // BIND DE BOTONES DEL FORMULARIO DE ALMACENES
    // ============================================================
    const btnAgregar = document.getElementById('btnAlmacenAgregar');
    const btnEditar = document.getElementById('btnAlmacenEditar');
    const btnCancelar = document.getElementById('btnAlmacenCancelar');

    if (btnAgregar) {
        btnAgregar.addEventListener('click', async function () {
            if (almacenesCrud) {
                await almacenesCrud.guardar();
                almacenesCrud._cambiosRealizados = true;
            }
        });
    }

    if (btnEditar) {
        btnEditar.addEventListener('click', async function () {
            if (almacenesCrud) {
                await almacenesCrud.guardarEdicion();
                almacenesCrud._cambiosRealizados = true;
            }
        });
    }

    if (btnCancelar) {
        btnCancelar.addEventListener('click', function () {
            if (almacenesCrud) {
                almacenesCrud.cancelar();
            }
        });
    }

    if (typeof Logger !== 'undefined') {
        Logger.success('Módulo Inventario + Almacenes inicializado');
    }
});