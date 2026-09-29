/**
 * cambiar_password.js
 * Lógica de cambio de contraseña.
 * - Abre automáticamente el modal si corresponde.
 * - Usa CSRF utility.
 * - Usa Logger y Notify reutilizables.
 */
document.addEventListener('DOMContentLoaded', function () {
    Logger.moduleInit('CambiarPassword');

    const page = document.getElementById('cambiarPasswordPage');
    const form = document.getElementById('formCambiarPassword');
    const modalEl = document.getElementById('modalCambiarPassword');

    if (!form || !modalEl) {
        Logger.warn('Formulario o modal de cambio de password no encontrados');
        return;
    }

    if (page && page.dataset.autoOpen === 'true') {
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    }

    document.querySelectorAll('.btn-toggle-pass').forEach(btn => {
        btn.addEventListener('click', function () {
            const targetId = this.dataset.target;
            const input = document.getElementById(targetId);
            if (!input) return;

            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);

            const icon = this.querySelector('i');
            if (icon) {
                icon.classList.toggle('bi-eye-fill');
                icon.classList.toggle('bi-eye-slash-fill');
            }

            Logger.info('Toggle password visibility', { target: targetId, type });
        });
    });

    const passwordNueva = document.getElementById('passwordNueva');
    const strengthContainer = document.getElementById('passwordStrength');

    if (passwordNueva && strengthContainer) {
        passwordNueva.addEventListener('input', function () {
            const password = this.value;
            const fortaleza = calcularFortaleza(password);

            strengthContainer.innerHTML = `
                <div class="password-strength-bar ${fortaleza.class}"></div>
                <small class="form-text" style="color: ${fortaleza.color};">
                    ${fortaleza.texto}
                </small>
            `;
        });
    }

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const passwordActual = document.getElementById('passwordActual').value;
        const passwordNueva = document.getElementById('passwordNueva').value;
        const passwordConfirmar = document.getElementById('passwordConfirmar').value;

        Logger.info('Intentando cambiar contraseña');

        if (!passwordActual || !passwordNueva || !passwordConfirmar) {
            Notify.warning('Todos los campos son obligatorios');
            return;
        }

        if (passwordNueva.length < 4) {
            Notify.warning('La nueva contraseña debe tener al menos 4 caracteres');
            return;
        }

        if (passwordNueva !== passwordConfirmar) {
            Notify.error('Las contraseñas nuevas no coinciden');
            return;
        }

        if (passwordActual === passwordNueva) {
            Notify.warning('La nueva contraseña debe ser diferente a la actual');
            return;
        }

        if (typeof mostrarLoader === 'function') mostrarLoader();

        try {
            Logger.apiCall('POST', '/api/cambiar_password');

            const response = await CSRF.post('/api/cambiar_password', {
                password_actual: passwordActual,
                password_nueva: passwordNueva,
                password_confirmar: passwordConfirmar
            });

            const data = await response.json();
            Logger.apiResponse('POST', '/api/cambiar_password', response.status, data);

            if (data.status === 'ok') {
                Notify.success(data.msg || 'Contraseña cambiada exitosamente');

                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();

                form.reset();
                if (strengthContainer) strengthContainer.innerHTML = '';
            } else {
                Notify.error(data.msg || 'Error al cambiar la contraseña');
            }
        } catch (err) {
            Logger.error('Error al cambiar contraseña', err);
            Notify.error('Error de conexión al cambiar la contraseña');
        } finally {
            if (typeof ocultarLoader === 'function') ocultarLoader();
        }
    });

    Logger.success('Módulo CambiarPassword inicializado correctamente');
});

function calcularFortaleza(password) {
    if (!password) {
        return { class: '', texto: '', color: '#b8b8b8' };
    }

    let score = 0;

    if (password.length >= 4) score++;
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;

    if (score <= 2) {
        return { class: 'weak', texto: '🔴 Débil', color: '#dc3545' };
    } else if (score <= 4) {
        return { class: 'medium', texto: '🟡 Media', color: '#ffc107' };
    } else {
        return { class: 'strong', texto: '🟢 Fuerte', color: '#28a745' };
    }
}