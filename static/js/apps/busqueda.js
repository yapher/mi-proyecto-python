// busqueda.js: filtrar y resaltar coincidencias
document.addEventListener('DOMContentLoaded', function () {
    const input = document.getElementById('buscarPlano');
    if (!input) return;

    input.addEventListener('keyup', function () {
        const filtro = input.value.toLowerCase();
        const collapses = document.querySelectorAll('tr.collapse');

        collapses.forEach(tr => {
            const rows = tr.querySelectorAll('tbody tr');
            let matchFound = false;

            rows.forEach(row => {
                const tds = row.querySelectorAll('td');
                let rowMatch = false;

                tds.forEach(td => {
                    const texto = td.textContent;
                    const lower = texto.toLowerCase();

                    // Limpiar marcas anteriores
                    td.innerHTML = texto;

                    if (filtro && lower.includes(filtro)) {
                        // Resaltar coincidencia
                        const regex = new RegExp(`(${filtro})`, 'gi');
                        td.innerHTML = texto.replace(regex, '<span class="bg-warning text-dark">$1</span>');
                        rowMatch = true;
                    }
                });

                // Mostrar u ocultar fila según coincidencia
                if (rowMatch) {
                    row.style.display = '';
                    matchFound = true;
                } else {
                    row.style.display = 'none';
                }
            });

            // Expandir si hay coincidencia en la línea
            if (matchFound) {
                tr.classList.add('show');
            } else {
                tr.classList.remove('show');
            }
        });
    });
});
