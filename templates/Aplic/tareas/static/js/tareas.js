/**
 * tareas.js — Módulo de gestión de tareas
 * Usa Logger y Notify reutilizables
 */
const API_BASE = '/api/tareas';
let modalEditar = null;
let tareaActualId = null;

document.addEventListener('DOMContentLoaded', () => {
    Logger.moduleInit('Tareas');
    const modalEl = document.getElementById('modalEditarTarea');
    if (modalEl) {
        modalEditar = new bootstrap.Modal(modalEl);
    }
    configurarFormularios();
    cargarTareas();
    Logger.success('Módulo Tareas inicializado');
});

async function cargarTareas() {
    Logger.apiCall('GET', API_BASE);
    try {
        const res = await fetch(API_BASE, { credentials: 'same-origin' });
        Logger.apiResponse('GET', API_BASE, res.status);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const tareas = await res.json();
        renderizarTareas(tareas);
    } catch (err) {
        Logger.error('Error al cargar tareas', err);
        Notify.error('Error al cargar las tareas');
        renderizarEstadoVacio();
    }
}

function renderizarTareas(tareas) {
    const lista = document.getElementById('listaTareas');
    if (!lista) return;
    if (!tareas || tareas.length === 0) {
        renderizarEstadoVacio();
        return;
    }
    lista.innerHTML = tareas.map(tarea => `
        <li>
            <div class="event-info"
                data-id="${tarea.id}"
                data-titulo="${escapeHtml(tarea.titulo)}"
                data-fecha="${escapeHtml(tarea.fecha)}"
                data-descripcion="${escapeHtml(tarea.descripcion || '')}">
                <strong>${escapeHtml(tarea.titulo)}</strong>
                <div class="event-fecha">
                    <i class="bi bi-calendar-event"></i> ${formatearFecha(tarea.fecha)}
                </div>
                ${tarea.descripcion ? `<div class="descripcion-text">${escapeHtml(tarea.descripcion)}</div>` : ''}
            </div>
            <button class="btn btn-eliminar btn-sm" onclick="confirmarEliminar(${tarea.id})">
                Eliminar
            </button>
        </li>
    `).join('');

    lista.querySelectorAll('.event-info').forEach(el => {
        el.addEventListener('click', () => abrirModalEdicion(el.dataset));
    });
    Logger.info('Tareas renderizadas', { cantidad: tareas.length });
}

function renderizarEstadoVacio() {
    const lista = document.getElementById('listaTareas');
    if (!lista) return;
    lista.innerHTML = `
        <li class="tareas-empty">
            <i class="bi bi-clipboard-check"></i>
            <p>No hay tareas registradas</p>
            <small>Usá el formulario de arriba para agregar una nueva tarea</small>
        </li>
    `;
}

function abrirModalEdicion(data) {
    if (!modalEditar) return;
    tareaActualId = data.id;
    document.getElementById('edit-id').value = data.id;
    document.getElementById('edit-titulo').value = data.titulo;
    document.getElementById('edit-fecha').value = data.fecha;
    document.getElementById('edit-descripcion').value = data.descripcion || '';
    modalEditar.show();
}

function cerrarModalEdicion() {
    if (modalEditar) modalEditar.hide();
    tareaActualId = null;
}

async function crearTarea(data) {
    Logger.apiCall('POST', API_BASE);
    try {
        const res = await fetch(API_BASE, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
            credentials: 'same-origin'
        });
        const json = await res.json();
        Logger.apiResponse('POST', API_BASE, res.status, json);
        if (!res.ok) throw new Error(json.msg || 'Error al crear');
        Notify.success(json.msg || 'Tarea creada');
        await cargarTareas();
        return true;
    } catch (err) {
        Logger.error('Error al crear tarea', err);
        Notify.error(err.message || 'Error al crear la tarea');
        return false;
    }
}

async function actualizarTarea(id, data) {
    const url = `${API_BASE}/${id}`;
    Logger.apiCall('PUT', url);
    try {
        const res = await fetch(url, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
            credentials: 'same-origin'
        });
        const json = await res.json();
        Logger.apiResponse('PUT', url, res.status, json);
        if (!res.ok) throw new Error(json.msg || 'Error al actualizar');
        Notify.success(json.msg || 'Tarea actualizada');
        cerrarModalEdicion();
        await cargarTareas();
        return true;
    } catch (err) {
        Logger.error('Error al actualizar tarea', err);
        Notify.error(err.message || 'Error al actualizar');
        return false;
    }
}

async function eliminarTarea(id) {
    const url = `${API_BASE}/${id}`;
    Logger.apiCall('DELETE', url);
    try {
        const res = await fetch(url, {
            method: 'DELETE',
            credentials: 'same-origin'
        });
        const json = await res.json();
        Logger.apiResponse('DELETE', url, res.status, json);
        if (!res.ok) throw new Error(json.msg || 'Error al eliminar');
        Notify.success(json.msg || 'Tarea eliminada');
        cerrarModalEdicion();
        await cargarTareas();
        return true;
    } catch (err) {
        Logger.error('Error al eliminar tarea', err);
        Notify.error(err.message || 'Error al eliminar');
        return false;
    }
}

function confirmarEliminar(id) {
    Notify.delete("esta tarea", () => eliminarTarea(id));
}

function configurarFormularios() {
    const formAgregar = document.getElementById('formAgregarTarea');
    if (formAgregar) {
        formAgregar.addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = {
                titulo: document.getElementById('titulo').value.trim(),
                fecha: document.getElementById('fecha').value,
                descripcion: document.getElementById('descripcion').value.trim()
            };
            if (!data.titulo || !data.fecha) {
                Notify.warning('Título y fecha son obligatorios');
                return;
            }
            const exito = await crearTarea(data);
            if (exito) formAgregar.reset();
        });
    }

    const formEditar = document.getElementById('formEditarTarea');
    if (formEditar) {
        formEditar.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (!tareaActualId) return;
            const data = {
                titulo: document.getElementById('edit-titulo').value.trim(),
                fecha: document.getElementById('edit-fecha').value,
                descripcion: document.getElementById('edit-descripcion').value.trim()
            };
            if (!data.titulo || !data.fecha) {
                Notify.warning('Título y fecha son obligatorios');
                return;
            }
            await actualizarTarea(tareaActualId, data);
        });
    }

    const btnEliminar = document.getElementById('btnEliminarTarea');
    if (btnEliminar) {
        btnEliminar.addEventListener('click', () => {
            if (tareaActualId) confirmarEliminar(tareaActualId);
        });
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatearFecha(fechaStr) {
    if (!fechaStr) return '';
    try {
        const [year, month, day] = fechaStr.split('-');
        return `${day}/${month}/${year}`;
    } catch {
        return fechaStr;
    }
}