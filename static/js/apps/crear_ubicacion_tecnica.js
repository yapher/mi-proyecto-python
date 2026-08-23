/**
 * crear_ubicacion_tecnica.js
 * Refactorizado: usa el módulo genérico ArbolCRUD.
 */
document.addEventListener("DOMContentLoaded", () => {
    new ArbolCRUD({
        apiArbol:   "/api/ubicacion_arbol",
        apiCrud:    "/api/ubicacion",
        claveHijos: "sububicaciones",
        campoRuta:  "ruta_ubicacion",
        nombreItem: "ubicación",
        selectoresId: "nivelesContainer",
        tablaId:      "tabla",
        camposForm: {
            nombre:   "nombre",
            emoji:    "emoji",
            ruta:     "ruta_ubicacion",
            original: "ruta_original"
        },
        botones: {
            agregar:  ".btn-agregar",
            editar:   ".btn-editar",
            cancelar: ".btn-cancelar"
        }
    });
});