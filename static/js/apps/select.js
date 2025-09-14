// select.js: poblar select de rutas desde el servidor
document.addEventListener('DOMContentLoaded', function () {
    const rutas = window.rutasServidor || [];
    const select = document.getElementById('nombre_linea');
    if (!select) return;

    if (Array.isArray(rutas) && rutas.length) {
        const existing = Array.from(select.options).map(o => o.value);
        rutas.forEach(r => {
            if (!existing.includes(r)) {
                const opt = document.createElement('option');
                opt.value = r;
                opt.textContent = r;
                select.appendChild(opt);
            }
        });
        document.getElementById('rutas-empty')?.classList.add('d-none');
    } else {
        const warn = document.getElementById('rutas-empty');
        if (warn) warn.classList.remove('d-none');
        console.warn('No se encontraron rutas en el servidor (verificar DataBase/dataRep/ubicacion_tecnica.json).');
    }
});
