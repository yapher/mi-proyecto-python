// static/js/utils/login_modal.js
/**
 * login_modal.js - Lógica del modal de login
 * Maneja la visualización automática y el toggle de contraseña
 */

document.addEventListener('DOMContentLoaded', function() {
    const loginModal = document.getElementById('loginModal');
    
    if (!loginModal) return;
    
    // Si el modal existe y el usuario no está autenticado, mostrarlo automáticamente
    const modal = new bootstrap.Modal(loginModal, {
        backdrop: 'static',
        keyboard: false
    });
    
    // Verificar si necesitamos mostrar el modal
    const body = document.body;
    if (body.dataset.requireLogin === 'true') {
        modal.show();
    }
    
    // Toggle para mostrar/ocultar contraseña
    const toggleBtn = document.getElementById('togglePasswordBtn');
    const passwordInput = document.getElementById('loginPassword');
    
    if (toggleBtn && passwordInput) {
        toggleBtn.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            const icon = this.querySelector('i');
            if (icon) {
                icon.classList.toggle('bi-eye-fill');
                icon.classList.toggle('bi-eye-slash-fill');
            }
        });
    }
});