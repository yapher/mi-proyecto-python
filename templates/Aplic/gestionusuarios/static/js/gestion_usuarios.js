/**
 * Gestión de Usuarios - Lógica específica
 * Usa Logger y Notify reutilizables
 */
document.addEventListener('DOMContentLoaded', () => {
    Logger.moduleInit('GestionUsuarios');

    const modal = new bootstrap.Modal(document.getElementById('modalUsuario'));
    let usuarioEnEdicion = null;

    // ========================================================
    // Cargar usuarios al iniciar
    // ========================================================
    cargarUsuarios();

    // ========================================================
    // Event listeners
    // ========================================================

    // Botón agregar (limpiar formulario)
    document.getElementById('btnAgregarUsuario').addEventListener('click', () => {
        limpiarFormulario();
        document.getElementById('modalUsuarioLabel').textContent = 'Agregar Usuario';
        document.getElementById('password').required = true;
    });

    // Submit del formulario
    document.getElementById('formUsuario').addEventListener('submit', async (e) => {
        e.preventDefault();
        await guardarUsuario();
    });

    // ========================================================
    // Funciones principales
    // ========================================================

    async function cargarUsuarios() {
        Logger.apiCall('GET', '/api/usuarios');
        try {
            const res = await fetch('/api/usuarios', { credentials: 'same-origin' });
            Logger.apiResponse('GET', '/api/usuarios', res.status);

            if (!res.ok) throw new Error(`HTTP ${res.status}`);

            const usuarios = await res.json();
            renderizarUsuarios(usuarios);
        } catch (err) {
            Logger.error('Error al cargar usuarios', err);
            Notify.error('Error al cargar los usuarios');
        } finally {
            // ✅ FIX: Ocultar loader siempre al terminar
            if (typeof ocultarLoader === 'function') ocultarLoader();
        }
    }

    function renderizarUsuarios(usuarios) {
        const tbody = document.getElementById('tablaUsuarios');
        if (!tbody) return;

        if (!usuarios || usuarios.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center text-muted">
                        No hay usuarios registrados
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = usuarios.map(u => `
            <tr>
                <td><strong>${escapeHtml(u.username)}</strong></td>
                <td>${renderRoles(u.roles)}</td>
                <td>${formatearFecha(u.created_at)}</td>
                <td>
                    <button class="btn btn-sm btn-editar" onclick="editarUsuario('${u.id}')">
                        Editar
                    </button>
                    <button class="btn btn-sm btn-eliminar" onclick="eliminarUsuario('${u.id}', '${escapeHtml(u.username)}')">
                        Eliminar
                    </button>
                </td>
            </tr>
        `).join('');
    }

    function renderRoles(roles) {
        if (!roles || roles.length === 0) return '<span class="text-muted">Sin roles</span>';

        const labels = {
            'admin': '👑 Admin',
            'editor': '✏️ Editor',
            'viewer': '👁️ Viewer'
        };

        return roles.map(r => `<span class="role-badge ${r}">${labels[r] || r}</span>`).join('');
    }

    async function guardarUsuario() {
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;
        const roles = obtenerRolesSeleccionados();

        // Validaciones
        if (!username) {
            Notify.warning('El nombre de usuario es obligatorio');
            return;
        }

        if (!usuarioEnEdicion && !password) {
            Notify.warning('La contraseña es obligatoria para nuevos usuarios');
            return;
        }

        if (password && password.length < 4) {
            Notify.warning('La contraseña debe tener al menos 4 caracteres');
            return;
        }

        if (roles.length === 0) {
            Notify.warning('Debe asignar al menos un rol');
            return;
        }

        const data = { username, roles };
        if (password) data.password = password;

        const url = usuarioEnEdicion ? `/api/usuarios/${usuarioEnEdicion}` : '/api/usuarios';
        const method = usuarioEnEdicion ? 'PUT' : 'POST';

        Logger.apiCall(method, url);
        try {
            const res = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
                credentials: 'same-origin'
            });

            const json = await res.json();
            Logger.apiResponse(method, url, res.status, json);

            if (!res.ok) throw new Error(json.msg || 'Error al guardar');

            Notify.success(json.msg || 'Usuario guardado');
            modal.hide();
            await cargarUsuarios();
            limpiarFormulario();
        } catch (err) {
            Logger.error('Error al guardar usuario', err);
            Notify.error(err.message || 'Error al guardar el usuario');
        } finally {
            // ✅ FIX: Ocultar loader siempre al terminar
            if (typeof ocultarLoader === 'function') ocultarLoader();
        }
    }

    function obtenerRolesSeleccionados() {
        const roles = [];
        if (document.getElementById('roleAdmin').checked) roles.push('admin');
        if (document.getElementById('roleEditor').checked) roles.push('editor');
        if (document.getElementById('roleViewer').checked) roles.push('viewer');
        return roles;
    }

    function limpiarFormulario() {
        document.getElementById('formUsuario').reset();
        document.getElementById('usuarioId').value = '';
        usuarioEnEdicion = null;
    }

    // ========================================================
    // Funciones globales (para onclick en tabla)
    // ========================================================

    window.editarUsuario = async (id) => {
        Logger.info('Editando usuario', { id });

        try {
            const res = await fetch('/api/usuarios', { credentials: 'same-origin' });
            const usuarios = await res.json();
            const usuario = usuarios.find(u => u.id === id);

            if (!usuario) {
                Notify.error('Usuario no encontrado');
                return;
            }

            usuarioEnEdicion = id;
            document.getElementById('usuarioId').value = usuario.id;
            document.getElementById('username').value = usuario.username;
            document.getElementById('password').value = ''; // No mostrar password
            document.getElementById('password').required = false;

            // Marcar roles
            document.getElementById('roleAdmin').checked = usuario.roles.includes('admin');
            document.getElementById('roleEditor').checked = usuario.roles.includes('editor');
            document.getElementById('roleViewer').checked = usuario.roles.includes('viewer');

            document.getElementById('modalUsuarioLabel').textContent = 'Editar Usuario';
            modal.show();
        } catch (err) {
            Logger.error('Error al cargar usuario para edición', err);
            Notify.error('Error al cargar los datos del usuario');
        } finally {
            // ✅ FIX: Ocultar loader siempre al terminar
            if (typeof ocultarLoader === 'function') ocultarLoader();
        }
    };

    window.eliminarUsuario = (id, username) => {
        Notify.confirm(
            'Eliminar usuario',
            `¿Está seguro que desea eliminar al usuario "${username}"? Esta acción no se puede deshacer.`,
            async () => {
                Logger.apiCall('DELETE', `/api/usuarios/${id}`);
                try {
                    const res = await fetch(`/api/usuarios/${id}`, {
                        method: 'DELETE',
                        credentials: 'same-origin'
                    });

                    const json = await res.json();
                    Logger.apiResponse('DELETE', `/api/usuarios/${id}`, res.status, json);

                    if (!res.ok) throw new Error(json.msg || 'Error al eliminar');

                    Notify.success(json.msg || 'Usuario eliminado');
                    await cargarUsuarios();
                } catch (err) {
                    Logger.error('Error al eliminar usuario', err);
                    Notify.error(err.message || 'Error al eliminar el usuario');
                } finally {
                    // ✅ FIX: Ocultar loader siempre al terminar
                    if (typeof ocultarLoader === 'function') ocultarLoader();
                }
            }
        );
    };

    // ========================================================
    // Utilidades
    // ========================================================

    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function formatearFecha(fechaStr) {
        if (!fechaStr) return '-';
        try {
            const fecha = new Date(fechaStr);
            return fecha.toLocaleDateString('es-AR', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit'
            });
        } catch {
            return fechaStr;
        }
    }

    Logger.success('Módulo GestiónUsuarios inicializado');
});