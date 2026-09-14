/**
 * modal_animations.js
 * ===================
 * Captura la posición del click que abre un modal
 * y aplica una animación de apertura/cierre desde ese punto.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Capturar clicks en elementos que abren modales
    document.addEventListener('click', function(e) {
        const target = e.target.closest('[data-bs-toggle="modal"]');
        
        if (target) {
            const modalSelector = target.getAttribute('data-bs-target');
            
            if (modalSelector) {
                const modal = document.querySelector(modalSelector);
                
                if (modal) {
                    // Calcular posición del click relativa a la ventana
                    const clickX = e.clientX;
                    const clickY = e.clientY;
                    
                    // Convertir a porcentajes para transform-origin
                    const percentX = (clickX / window.innerWidth) * 100;
                    const percentY = (clickY / window.innerHeight) * 100;
                    
                    // Aplicar como variables CSS al modal
                    modal.style.setProperty('--modal-origin-x', `${percentX}%`);
                    modal.style.setProperty('--modal-origin-y', `${percentY}%`);
                    
                    // Agregar clase para activar la animación con origen
                    modal.classList.add('modal-origin-click');
                }
            }
        }
    });
    
    // Limpiar la clase cuando el modal se cierra
    document.addEventListener('hidden.bs.modal', function(e) {
        const modal = e.target;
        if (modal) {
            modal.classList.remove('modal-origin-click');
        }
    });
});