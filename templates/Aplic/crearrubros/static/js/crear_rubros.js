/**
 * Crear Rubros - Lógica de la aplicación
 * Usa el módulo genérico ArbolCRUD y Logger reutilizable
 */
document.addEventListener("DOMContentLoaded", () => {
    Logger.moduleInit('CrearRubros');

    // Instanciar ArbolCRUD con configuración específica
    const crud = new ArbolCRUD({
        apiArbol:      '/api/rubro_arbol',
        apiCrud:       '/api/rubro',
        claveHijos:    'submenues',
        campoRuta:     'ruta_menu',
        nombreItem:    'rubro',
        selectoresId:  'nivelesContainer',
        tablaId:       'tabla',
        camposForm: {
            nombre:   'nombre',
            emoji:    'emoji',
            ruta:     'ruta_menu',
            original: 'ruta_original'
        },
        botones: {
            agregar:  '#btnAgregar',
            editar:   '#btnEditar',
            cancelar: '#btnCancelar'
        },
        // Personalizar la fila de la tabla para usar los mismos estilos que otras apps
        onRenderFila: (nodo, nivel, crudInstance) => {
            const rutaAttr = crudInstance._escapeAttr(nodo.ruta_jerarquia);
            const nombreAttr = crudInstance._escapeAttr(nodo.nombre);
            const emojiAttr = crudInstance._escapeAttr(nodo.emoji || "");
            const rutaValorAttr = crudInstance._escapeAttr(nodo.ruta || "");
            
            return `
                <tr>
                    <td>${nodo.emoji || ""}</td>
                    <td class="nivel-${nivel}">${nodo.nombre}</td>
                    <td>${nodo.ruta || ""}</td>
                    <td>
                        <button class="btn btn-sm btn-editar"
                            onclick="window.__arbolCRUD_editar__.call(null,
                            '${rutaAttr}','${nombreAttr}','${emojiAttr}','${rutaValorAttr}')">
                            Editar
                        </button>
                        <button class="btn btn-sm btn-eliminar"
                            onclick="window.__arbolCRUD_eliminar__.call(null, '${rutaAttr}')">
                            Eliminar
                        </button>
                    </td>
                </tr>
            `;
        }
    });

    // Modal de Bootstrap
    const modalEl = document.getElementById('rubroModal');
    const modal = new bootstrap.Modal(modalEl);

    // Sobreescribir prepararEdicion para abrir el modal
    const prepararEdicionOriginal = crud.prepararEdicion.bind(crud);
    crud.prepararEdicion = function(ruta, nombre, emoji, rutaValor) {
        Logger.info('Preparando edición de rubro', { ruta, nombre, emoji });
        prepararEdicionOriginal(ruta, nombre, emoji, rutaValor);
        modal.show();
    };

    // Sobreescribir eliminarItem para usar SweetAlert2
    crud.eliminarItem = async function(ruta) {
        Logger.info('Solicitando eliminación de rubro', { ruta });
        
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: '¿Eliminar este rubro?',
                text: 'Esta acción no se puede deshacer',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#dc3545',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar'
            }).then(async (result) => {
                if (result.isConfirmed) {
                    try {
                        const res = await fetch(this.cfg.apiCrud, {
                            method: 'DELETE',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ ruta })
                        });
                        
                        const contentType = res.headers.get('content-type');
                        if (!contentType || !contentType.includes('application/json')) {
                            throw new Error('El servidor devolvió HTML en lugar de JSON');
                        }
                        
                        const data = await res.json();
                        
                        if (res.ok) {
                            Logger.success('Rubro eliminado correctamente', { ruta });
                            if (typeof Noty !== 'undefined') {
                                new Noty({
                                    type: 'success',
                                    layout: 'topRight',
                                    timeout: 3000,
                                    theme: 'mint',
                                    text: data.msg || 'Rubro eliminado'
                                }).show();
                            }
                            await this.init();
                            this.cancelar();
                        } else {
                            throw new Error(data.msg || 'Error al eliminar');
                        }
                    } catch (err) {
                        Logger.error('Error al eliminar rubro', { ruta, error: err.message });
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: err.message
                        });
                    }
                }
            });
        } else {
            // Fallback sin SweetAlert2
            if (confirm(`¿Eliminar este ${this.cfg.nombreItem}?`)) {
                try {
                    const res = await fetch(this.cfg.apiCrud, {
                        method: 'DELETE',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ ruta })
                    });
                    const data = await res.json();
                    Logger.success('Rubro eliminado', { ruta });
                    alert(data.msg || 'Eliminado');
                    await this.init();
                    this.cancelar();
                } catch (err) {
                    Logger.error('Error al eliminar', { ruta, error: err.message });
                    alert('Error al eliminar: ' + err.message);
                }
            }
        }
    };

    // Eventos de botones del modal
    document.getElementById('btnAgregar').addEventListener('click', async () => {
        Logger.info('Click en botón Agregar');
        await crud.guardar();
        modal.hide();
    });

    document.getElementById('btnEditar').addEventListener('click', async () => {
        Logger.info('Click en botón Editar');
        await crud.guardarEdicion();
        modal.hide();
    });

    document.getElementById('btnCancelar').addEventListener('click', () => {
        Logger.info('Click en botón Cancelar');
        crud.cancelar();
        modal.hide();
    });

    // Abrir modal en modo "Agregar" cuando se hace clic en el botón principal
    document.getElementById('btnAbrirModal').addEventListener('click', () => {
        Logger.info('Abriendo modal en modo Agregar');
        crud.cancelar();
        modal.show();
    });

    Logger.success('Módulo CrearRubros inicializado correctamente');
});