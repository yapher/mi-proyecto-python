document.addEventListener("DOMContentLoaded", () => {
    Logger.moduleInit('CrearAlmacenes');
    
    const crud = new ArbolCRUD({
        apiArbol:     "/api/crear_almacenes_arbol",
        apiCrud:      "/api/crear_almacenes",
        claveHijos:   "subcrear_almacenes",
        campoRuta:    "ruta_crear_almacenes",
        nombreItem:   "almacén",
        selectoresId: "nivelesContainer",
        tablaId:      "tabla",
        camposForm: {
            nombre:   "nombre",
            emoji:    "emoji",
            ruta:     "ruta_crear_almaceneses",
            original: "ruta_original"
        },
        botones: {
            agregar:  "#btnAgregar",
            editar:   "#btnEditar",
            cancelar: "#btnCancelar"
        }
    });

    document.getElementById("btnAgregar").addEventListener("click", async () => {
        await crud.guardar();
    });

    document.getElementById("btnEditar").addEventListener("click", async () => {
        await crud.guardarEdicion();
    });

    document.getElementById("btnCancelar").addEventListener("click", () => {
        crud.cancelar();
    });
});