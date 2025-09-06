/**
 * JavaScript para el componente Agenda
 * Maneja la funcionalidad del calendario y gestión de eventos
 */

// Prefijo del blueprint
const BASE = "/agenda";

// Variables globales
let eventos = [];
let modal;

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Obtener elementos del DOM
    modal = new bootstrap.Modal(document.getElementById('modalEvento'));
    
    // Configurar event listeners
    document.getElementById("mes").onchange = generarCalendario;
    document.getElementById("año").onchange = generarCalendario;
    
    // Cargar eventos iniciales
    cargarEventos();
});

/**
 * Carga los eventos desde la API
 */
function cargarEventos() {
    fetch(`${BASE}/eventos`)
        .then(res => res.json())
        .then(data => { 
            eventos = data; 
            generarCalendario(); 
        })
        .catch(err => {
            console.error("Error cargando eventos:", err);
            eventos = [];
            generarCalendario();
        });
}

/**
 * Obtiene la clase CSS para el día de la semana
 * @param {number} jsDay - Día de la semana (0=domingo, 1=lunes, etc.)
 * @returns {string} Clase CSS correspondiente
 */
function clasePorDiaSemana(jsDay) {
    const map = { 1: 'dia-lun', 2: 'dia-mar', 3: 'dia-mie', 4: 'dia-jue', 5: 'dia-vie', 6: 'dia-sab', 0: 'dia-dom' };
    return map[jsDay] || 'dia-lun';
}

/**
 * Obtiene la etiqueta del día de la semana
 * @param {number} jsDay - Día de la semana (0=domingo, 1=lunes, etc.)
 * @returns {string} Nombre del día
 */
function etiquetaDia(jsDay) {
    const map = { 1: 'Lunes', 2: 'Martes', 3: 'Miércoles', 4: 'Jueves', 5: 'Viernes', 6: 'Sábado', 0: 'Domingo' };
    return map[jsDay] || '';
}

/**
 * Genera el calendario con los eventos
 */
function generarCalendario() {
    const mes = parseInt(document.getElementById("mes").value);
    const año = parseInt(document.getElementById("año").value);

    // NOTA: conservo la lógica original que tenías para primerDia/ultimoDia
    const primerDia = new Date(año, mes - 1, 0);
    const ultimoDia = new Date(año, mes, 0);

    const calendario = document.getElementById("calendario");
    calendario.innerHTML = "";

    let fila = document.createElement("tr");

    // Placeholder inicial (mantengo la lógica original)
    for (let i = 0; i < (primerDia.getDay() + 7) % 7; i++) {
        const td = document.createElement("td");
        td.classList.add('vacio');
        fila.appendChild(td);
    }

    for (let d = 1; d <= ultimoDia.getDate(); d++) {
        const fechaStr = `${año}-${String(mes).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
        const celda = document.createElement("td");

        const jsDay = new Date(año, mes - 1, d).getDay(); // 0=Dom..6=Sáb
        const claseDia = clasePorDiaSemana(jsDay);

        const cont = document.createElement("div");
        cont.className = `dia ${claseDia}`;
        cont.title = `Agregar/editar eventos - ${fechaStr}`;
        cont.onclick = () => abrirModal(fechaStr);

        const labelSemana = document.createElement("div");
        labelSemana.className = "semana-label";
        labelSemana.textContent = etiquetaDia(jsDay);

        const num = document.createElement("div");
        num.className = "numero";
        num.textContent = d;

        cont.appendChild(labelSemana);
        cont.appendChild(num);

        // >>> PRIORIDAD: ordenar por prioridad (alta, media, baja)
        const ordenPrio = { alta: 1, media: 2, baja: 3 };
        const eventosDia = eventos
            .filter(e => e.fecha === fechaStr)
            .sort((a, b) => (ordenPrio[a?.prioridad] ?? 2) - (ordenPrio[b?.prioridad] ?? 2));

        eventosDia.forEach(e => {
            const pill = document.createElement("div");
            pill.className = "evento-pill";
            if (e.realizado) pill.classList.add("evento-realizado");

            // >>> PRIORIDAD: color visual según prioridad (si no está realizado)
            if (!e.realizado) {
                if (e.prioridad === "alta") pill.classList.add("prio-alta");
                else if (e.prioridad === "media") pill.classList.add("prio-media");
                else if (e.prioridad === "baja") pill.classList.add("prio-baja");
            }

            // Checkbox para marcar realizado (evita que abra modal)
            const chk = document.createElement("input");
            chk.type = "checkbox";
            chk.checked = !!e.realizado;
            chk.onclick = (ev) => {
                ev.stopPropagation();
                toggleRealizado(e.id, chk.checked);
            };

            const span = document.createElement("span");
            span.textContent = e.titulo;

            // Click en la pill (excepto el checkbox) abre modal
            pill.onclick = (ev) => { ev.stopPropagation(); abrirModal(e.fecha, e); };

            pill.appendChild(chk);
            pill.appendChild(span);
            cont.appendChild(pill);
        });

        // Resaltar hoy
        const hoy = new Date();
        const esHoy = hoy.getFullYear() === año && (hoy.getMonth() + 1) === mes && hoy.getDate() === d;
        if (esHoy) cont.classList.add('hoy');

        celda.appendChild(cont);
        fila.appendChild(celda);

        if ((primerDia.getDay() + d) % 7 === 0 || d === ultimoDia.getDate()) {
            calendario.appendChild(fila);
            fila = document.createElement("tr");
        }
    }
}

/**
 * Abre el modal para crear/editar un evento
 * @param {string} fecha - Fecha del evento
 * @param {Object} evento - Evento a editar (opcional)
 */
function abrirModal(fecha = "", evento = null) {
    document.getElementById("eventoId").value = evento?.id || "";
    document.getElementById("titulo").value = evento?.titulo || "";
    document.getElementById("fecha").value = fecha || evento?.fecha || "";
    document.getElementById("descripcion").value = evento?.descripcion || "";
    document.getElementById("email").value = evento?.email || "";
    document.getElementById("realizado").checked = evento?.realizado || false;

    // >>> PRIORIDAD: setear valor por defecto/actual
    const selPrio = document.getElementById("prioridad");
    if (selPrio) selPrio.value = evento?.prioridad || "media";

    modal.show();
}

/**
 * Cambia el estado de realizado de un evento
 * @param {number} id - ID del evento
 * @param {boolean} estado - Nuevo estado de realizado
 */
function toggleRealizado(id, estado) {
    fetch(`${BASE}/evento/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ realizado: estado })
    }).then(res => {
        if (!res.ok) throw new Error('Error al actualizar');
        cargarEventos();
    }).catch(err => {
        console.error("Error toggleRealizado:", err);
        Swal.fire({ icon: 'error', title: 'Ups', text: 'No se pudo actualizar el evento.' });
        cargarEventos();
    });
}
