/**
 * crear_almacenes.js
 * Refactorizado: usa el módulo genérico ArbolCRUD.
 */
document.addEventListener("DOMContentLoaded", () => {
    new ArbolCRUD({
        apiArbol:   "/api/crear_almacenes_arbol",
        apiCrud:    "/api/crear_almacenes",
        claveHijos: "subcrear_almacenes",
        campoRuta:  "ruta_crear_almacenes",
        nombreItem: "almacén",
        selectoresId: "nivelesContainer",
        tablaId:      "tabla",
        camposForm: {
            nombre:   "nombre",
            emoji:    "emoji",
            ruta:     "ruta_crear_almaceneses",
            original: "ruta_original"
        },
        botones: {
            agregar:  ".btn-agregar",
            editar:   ".btn-editar",
            cancelar: ".btn-cancelar"
        }
    });
});