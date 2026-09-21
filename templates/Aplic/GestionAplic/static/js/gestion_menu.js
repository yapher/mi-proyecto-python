/**
 * Gestión de Menú - Lógica de la aplicación
 * ✅ Usa ArbolCRUD reutilizable (static/js/utils/arbol_crud.js)
 * ✅ Usa Logger y Notify globales
 */
document.addEventListener("DOMContentLoaded", () => {
    Logger.moduleInit('GestionMenu');

    // ========================================================
    // Instancia única de ArbolCRUD
    // ========================================================
    const crud = new ArbolCRUD({
        apiArbol:     "/api/menu_arbol",
        apiCrud:      "/api/menu",
        claveHijos:   "submenues",
        campoRuta:    "ruta_menu",
        nombreItem:   "menú",
        selectoresId: "nivelesContainer",
        tablaId:      "tabla",
        camposForm: {
            nombre:   "nombre",
            emoji:    "emoji",
            ruta:     "ruta_menu",
            original: "ruta_original"
        },
        botones: {
            agregar:  ".btn-agregar",
            editar:   ".btn-editar-menu",
            cancelar: ".btn-cancelar-menu"
        },
        // ====================================================
        // Render personalizado de filas (con botones específicos)
        // ====================================================
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
                            onclick="prepararEdicion('${rutaAttr}','${nombreAttr}','${emojiAttr}','${rutaValorAttr}')">
                            Editar
                        </button>
                        <button class="btn btn-sm btn-eliminar"
                            onclick="eliminar('${rutaAttr}')">
                            Eliminar
                        </button>
                    </td>
                </tr>
            `;
        }
    });

    // ========================================================
    // Exponer funciones globales para los onclick del HTML
    // ========================================================
    window.guardar = () => crud.guardar();
    window.editar = () => crud.guardarEdicion();
    window.cancelar = () => crud.cancelar();
    window.eliminar = (ruta) => crud.eliminarItem(ruta);
    window.prepararEdicion = (ruta, nombre, emoji, rutaValor) => {
        crud.prepararEdicion(ruta, nombre, emoji, rutaValor);
    };

    Logger.success('Módulo GestionMenu inicializado correctamente');
});