/**
 * crear_procedimiento.js
 * Refactorizado: usa el módulo genérico ArbolCRUD.
 * Nota: este árbol usa separador "||" en ruta_jerarquia.
 */
document.addEventListener("DOMContentLoaded", () => {
    const crud = new ArbolCRUD({
        apiArbol:   "/api/proce_arbol",
        apiCrud:    "/api/proce",
        claveHijos: "submenues",
        campoRuta:  "ruta_menu",
        nombreItem: "procedimiento",
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
            editar:   ".btn-editar",
            cancelar: ".btn-cancelar"
        }
    });

    // Sobreescribir búsqueda para usar separador "||"
    crud.buscarNodoPorRuta = function(ruta) {
        if (!ruta) return null;
        const partes = ruta.split("||");
        let actual = this.arbol;
        let encontrado = null;
        for (const parte of partes) {
            const nodo = (actual || []).find(n => n.nombre === parte);
            if (!nodo) return null;
            encontrado = nodo;
            actual = nodo[this.cfg.claveHijos] || [];
        }
        return encontrado;
    };
});