// static/js/apps/busqueda.js
// Filtrar y resaltar coincidencias sin romper botones ni eventos
document.addEventListener('DOMContentLoaded', function () {
    const input = document.getElementById('buscarPlano');
    if (!input) return;

    input.addEventListener('keyup', function () {
        const filtro = input.value.toLowerCase().trim();
        const collapses = document.querySelectorAll('tr.collapse');

        collapses.forEach(tr => {
            const rows = tr.querySelectorAll('tbody tr');
            let matchFound = false;

            rows.forEach(row => {
                const tds = row.querySelectorAll('td');
                let rowMatch = false;

                tds.forEach((td, index) => {
                    const texto = td.textContent;
                    const lower = texto.toLowerCase();

                    // Solo aplicar resaltado en columnas de texto (no acciones con botones)
                    if (index === 1 || index === 2) { 
                        // Limpiar resaltado previo
                        td.innerHTML = texto;

                        if (filtro && lower.includes(filtro)) {
                            // Resaltar coincidencia
                            const regex = new RegExp(`(${filtro})`, 'gi');
                            td.innerHTML = texto.replace(regex, '<span class="bg-warning text-dark">$1</span>');
                            rowMatch = true;
                        }
                    } else {
                        // Para columnas con botones no tocamos innerHTML, solo chequeamos coincidencia
                        if (filtro && lower.includes(filtro)) {
                            rowMatch = true;
                        }
                    }
                });

                // Mostrar u ocultar fila según coincidencia
                if (rowMatch || !filtro) {
                    row.style.display = '';
                    matchFound = true;
                } else {
                    row.style.display = 'none';
                }
            });

            // Mostrar/ocultar la sección de la línea
            if (matchFound) {
                tr.style.display = '';
                // Expandir automáticamente si hay coincidencias
                tr.classList.add('show');
            } else {
                tr.style.display = 'none';
                tr.classList.remove('show');
            }
        });
    });
});
