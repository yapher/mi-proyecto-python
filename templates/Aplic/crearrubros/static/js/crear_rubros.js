/**
 * Crear Rubros - Lógica de la aplicación
 * Usa el módulo genérico ArbolCRUD, Logger y Notify reutilizables
 */
document.addEventListener("DOMContentLoaded", () => {
    Logger.moduleInit('CrearRubros');

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

    const modalEl = document.getElementById('rubroModal');
    const modal = new bootstrap.Modal(modalEl);

    const prepararEdicionOriginal = crud.prepararEdicion.bind(crud);
    crud.prepararEdicion = function(ruta, nombre, emoji, rutaValor) {
        Logger.info('Preparando edición de rubro', { ruta, nombre, emoji });
        prepararEdicionOriginal(ruta, nombre, emoji, rutaValor);
        modal.show();
    };

    crud.eliminarItem = async function(ruta) {
        Logger.info('Solicitando eliminación de rubro', { ruta });
        Notify.delete("este rubro", async () => {
            try {
                const res = await fetch(this.cfg.apiCrud, {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ruta })
                });
                const data = await res.json();
                if (res.ok) {
                    Logger.success('Rubro eliminado correctamente', { ruta });
                    Notify.success(data.msg || 'Rubro eliminado');
                    await this.init();
                    this.cancelar();
                } else {
                    Notify.error(data.msg || 'Error al eliminar');
                }
            } catch (err) {
                Logger.error('Error al eliminar rubro', { ruta, error: err.message });
                Notify.error('Error al eliminar: ' + err.message);
            }
        });
    };

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

    document.getElementById('btnAbrirModal').addEventListener('click', () => {
        Logger.info('Abriendo modal en modo Agregar');
        crud.cancelar();
        modal.show();
    });

    Logger.success('Módulo CrearRubros inicializado correctamente');
});