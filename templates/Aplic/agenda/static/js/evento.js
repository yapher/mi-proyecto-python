// evento.js
function actualizarDatalistEmails() {
    const datalist = document.getElementById('lista-emails');
    datalist.innerHTML = '';
    const emails = JSON.parse(localStorage.getItem('emailsGuardados') || '[]');
    emails.forEach(email => {
        let option = document.createElement('option');
        option.value = email;
        datalist.appendChild(option);
    });
}
actualizarDatalistEmails();

function guardarEvento() {
    const id = document.getElementById("eventoId").value;
    const titulo = document.getElementById("titulo").value.trim();
    const fecha = document.getElementById("fecha").value;
    const descripcion = document.getElementById("descripcion").value.trim();
    const email = document.getElementById("email").value.trim();
    const realizado = document.getElementById("realizado").checked;
    const prioridad = (document.getElementById("prioridad")?.value) || "media";

    if (!titulo || !fecha || !email) {
        Notify.warning("Título, fecha y email son obligatorios.");
        return;
    }

    if (!validarEmail(email)) {
        Notify.error("Por favor, ingresa un correo válido.");
        return;
    }

    // Guardar el email en localStorage
    if (email) {
        let emails = JSON.parse(localStorage.getItem('emailsGuardados') || '[]');
        if (!emails.includes(email)) {
            emails.push(email);
            localStorage.setItem('emailsGuardados', JSON.stringify(emails));
            actualizarDatalistEmails();
        }
    }

    const data = { titulo, fecha, descripcion, email, realizado, prioridad };
    const url = id ? `${BASE}/evento/${id}` : `${BASE}/evento`;
    const method = id ? "PUT" : "POST";

    fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    }).then(res => {
        if (!res.ok) throw new Error('Error al guardar');
        modal.hide();
        cargarEventos();
        Notify.success("Evento guardado correctamente");
    }).catch(() => {
        Notify.error("No se pudo guardar el evento.");
    });
}

function eliminarEvento() {
    const id = document.getElementById("eventoId").value;
    if (!id) { modal.hide(); return; }

    Notify.delete("este evento", () => {
        fetch(`${BASE}/evento/${id}`, { method: "DELETE" })
            .then(res => {
                if (!res.ok) throw new Error('Error al eliminar');
                modal.hide();
                cargarEventos();
                Notify.success("Evento eliminado");
            })
            .catch(() => {
                Notify.error("No se pudo eliminar el evento.");
            });
    });
}

function validarEmail(valor) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(String(valor).toLowerCase());
}