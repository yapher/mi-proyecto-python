/**
 * JavaScript para el componente Crear Rubros
 * Maneja la gestión de rubros con funcionalidad de edición
 */

/**
 * Prepara el formulario para editar un rubro
 * @param {string} ruta_jerarquia - Ruta jerárquica del rubro
 * @param {string} nombre - Nombre del rubro
 * @param {string} emoji - Emoji del rubro
 * @param {string} ruta_menu - Ruta del menú
 */
function prepararEdicion(ruta_jerarquia, nombre, emoji, ruta_menu) {
    document.getElementById("nombre").value = nombre;
    document.getElementById("emoji").value = emoji;
    document.getElementById("ruta_menu").value = ruta_menu || "";
    document.getElementById("ruta_original").value = ruta_jerarquia;

    document.querySelector(".btn-agregar").style.display = "none";
    document.querySelector(".btn-editar").style.display = "inline";
    document.querySelector(".btn-cancelar").style.display = "inline";

    const rutaPadre = obtenerRutaPadreDesdeJerarquia(ruta_jerarquia);
    renderSelectoresNiveles(rutaPadre); // Renderiza los selectores con valor por defecto
}

/**
 * Carga la tabla con todos los rubros
 */
function cargarTabla() {
    fetch('/api/rubro_arbol')
        .then(res => res.json())
        .then(data => {
            const tabla = document.getElementById("tabla");
            tabla.innerHTML = "";
            
            function recorrer(menus, nivel = 0) {
                menus.forEach(menu => {
                    tabla.innerHTML += `
                    <tr>
                        <td>${menu.emoji}</td>
                        <td class="nivel-${nivel}">${menu.nombre}</td>
                        <td>${menu.ruta || ''}</td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary" data-bs-toggle="modal" data-bs-target="#agregarModal" onclick="prepararEdicion('${menu.ruta_jerarquia}','${menu.nombre}','${menu.emoji}','${menu.ruta || ""}')">✏️ Editar</button>
                            <button class="btn btn-sm btn-outline-danger" onclick="eliminar('${menu.ruta_jerarquia}')">🗑️ Eliminar</button>
                        </td>
                    </tr>
                `;
                    if (menu.submenues && menu.submenues.length > 0) {
                        recorrer(menu.submenues, nivel + 1);
                    }
                });
            }
            recorrer(data);
        });
}
