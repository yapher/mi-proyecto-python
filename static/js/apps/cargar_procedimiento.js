/**
 * JavaScript para el componente Cargar Procedimiento
 * Maneja la funcionalidad de seleccionar todo y expandir/colapsar elementos
 */

document.addEventListener("DOMContentLoaded", function () {
    const selectAll = document.getElementById("selectAll");
    const toggleAll = document.getElementById("toggleAll");
    const checkboxes = document.querySelectorAll('input[type="checkbox"][name="seleccion"]');
    const collapses = document.querySelectorAll('.collapse');

    // Seleccionar/Deseleccionar todos los checkboxes
    if (selectAll) {
        selectAll.addEventListener("change", function () {
            checkboxes.forEach(cb => cb.checked = selectAll.checked);
        });
    }

    // Expandir/Colapsar todo
    if (toggleAll) {
        let expanded = false;
        toggleAll.addEventListener("click", function () {
            collapses.forEach(c => {
                const collapseInstance = bootstrap.Collapse.getOrCreateInstance(c);
                expanded ? collapseInstance.hide() : collapseInstance.show();
            });
            toggleAll.textContent = expanded ? 'Expandir todo' : 'Colapsar todo';
            expanded = !expanded;
        });
    }
});
