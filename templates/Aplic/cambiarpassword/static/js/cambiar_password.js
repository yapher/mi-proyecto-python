/**
 * cambiar_password.js - Lógica de cambio de contraseña
 * ✅ Usa Logger y Notify reutilizables
 * ✅ Cumple estándar: código mínimo, reutilizable
 */
document.addEventListener('DOMContentLoaded', function() {
    Logger.moduleInit('CambiarPassword');
    
    const form = document.getElementById('formCambiarPassword');
    if (!form) {
        Logger.warn('Formulario de cambio de password no encontrado');
        return;
    }
    
    // ========================================================
    // 1. TOGGLE: Mostrar/Ocultar contraseñas
    // ========================================================
    document.querySelectorAll('.btn-toggle-pass').forEach(btn => {
        btn.addEventListener('click', function() {
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
    
    // ========================================================
    // 2. INDICADOR DE FORTALEZA DE CONTRASEÑA
    // ========================================================
    const passwordNueva = document.getElementById('passwordNueva');
    const strengthContainer = document.getElementById('passwordStrength');
    
    if (passwordNueva && strengthContainer) {
        passwordNueva.addEventListener('input', function() {
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
    
    // ========================================================
    // 3. SUBMIT DEL FORMULARIO
    // ========================================================
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const passwordActual = document.getElementById('passwordActual').value;
        const passwordNueva = document.getElementById('passwordNueva').value;
        const passwordConfirmar = document.getElementById('passwordConfirmar').value;
        
        Logger.info('Intentando cambiar contraseña');
        
        // Validaciones del lado cliente
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
        
        // Mostrar loader
        if (typeof mostrarLoader === 'function') mostrarLoader();
        
        try {
            Logger.apiCall('POST', '/api/cambiar_password');
            
            const response = await fetch('/api/cambiar_password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    password_actual: passwordActual,
                    password_nueva: passwordNueva,
                    password_confirmar: passwordConfirmar
                }),
                credentials: 'same-origin'
            });
            
            const data = await response.json();
            Logger.apiResponse('POST', '/api/cambiar_password', response.status, data);
            
            if (data.status === 'ok') {
                Notify.success(data.msg || 'Contraseña cambiada exitosamente');
                
                // Cerrar modal
                const modalEl = document.getElementById('modalCambiarPassword');
                if (modalEl) {
                    const modal = bootstrap.Modal.getInstance(modalEl);
                    if (modal) modal.hide();
                }
                
                // Limpiar formulario
                form.reset();
                if (strengthContainer) strengthContainer.innerHTML = '';
                
                // Opcional: cerrar sesión después de cambiar contraseña
                // (descomentar si se desea)
                // setTimeout(() => {
                //     window.location.href = '/logout';
                // }, 2000);
                
            } else {
                Notify.error(data.msg || 'Error al cambiar la contraseña');
            }
            
        } catch (err) {
            Logger.error('Error al cambiar contraseña', err);
            Notify.error('Error de conexión al cambiar la contraseña');
        } finally {
            // Ocultar loader
            if (typeof ocultarLoader === 'function') ocultarLoader();
        }
    });
    
    Logger.success('Módulo CambiarPassword inicializado correctamente');
});

// ========================================================
// FUNCIÓN AUXILIAR: Calcular fortaleza de contraseña
// ========================================================
function calcularFortaleza(password) {
    if (!password) {
        return { class: '', texto: '', color: '#b8b8b8' };
    }
    
    let score = 0;
    
    // Longitud
    if (password.length >= 4) score++;
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    
    // Complejidad
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;
    
    // Clasificación
    if (score <= 2) {
        return { 
            class: 'weak', 
            texto: '🔴 Débil', 
            color: '#dc3545' 
        };
    } else if (score <= 4) {
        return { 
            class: 'medium', 
            texto: '🟡 Media', 
            color: '#ffc107' 
        };
    } else {
        return { 
            class: 'strong', 
            texto: '🟢 Fuerte', 
            color: '#28a745' 
        };
    }
}