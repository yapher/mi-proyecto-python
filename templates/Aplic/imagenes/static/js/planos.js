console.log('planos.js cargado');
document.addEventListener('DOMContentLoaded', function () {
    if (typeof Swal !== 'undefined') {
        console.log('SweetAlert2 está disponible en planos.js');

        // Rotar flechas en expandir/colapsar (Bootstrap altera aria-expanded en el botón)
        document.querySelectorAll('.btn-toggle').forEach(btn => {
            btn.addEventListener('click', function () {
                const icon = btn.querySelector('i');
                // dejamos un timeout corto para que Bootstrap actualice aria-expanded
                setTimeout(() => {
                    if (btn.getAttribute('aria-expanded') === 'true') {
                        icon.classList.remove('bi-caret-right-fill');
                        icon.classList.add('bi-caret-down-fill');
                    } else {
                        icon.classList.remove('bi-caret-down-fill');
                        icon.classList.add('bi-caret-right-fill');
                    }
                }, 120);
            });
        });

        // Confirmación para editar planos
        document.querySelectorAll('.btn-editar-plano').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                const form = btn.closest('form');
                Swal.fire({
                    title: '¿Guardar cambios?',
                    text: '¿Deseas actualizar este plano?',
                    icon: 'question',
                    showCancelButton: true,
                    confirmButtonColor: '#3085d6',
                    cancelButtonColor: '#d33',
                    confirmButtonText: 'Sí, actualizar',
                    cancelButtonText: 'Cancelar',
                    buttonsStyling: false,
                    customClass: {
                        confirmButton: 'btn-editar',
                        cancelButton: 'btn-cancelar'
                    }
                }).then((result) => {
                    if (result.isConfirmed) {
                        form.submit();
                    }
                });
            });
        });

        // Confirmación para eliminar planos
        document.querySelectorAll('.btn-eliminar-plano').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                const form = btn.closest('form');
                Swal.fire({
                    title: '¿Estás seguro?',
                    text: 'Esta acción eliminará el plano definitivamente.',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#d33',
                    cancelButtonColor: '#3085d6',
                    confirmButtonText: 'Sí, eliminar',
                    cancelButtonText: 'Cancelar',
                    buttonsStyling: false,
                    customClass: {
                        confirmButton: 'btn-eliminar',
                        cancelButton: 'btn-cancelar'
                    }
                }).then((result) => {
                    if (result.isConfirmed) {
                        form.submit();
                    }
                });
            });
        });

        // Si querés mostrar una alerta de "agregado" cuando se hace submit y vuelve la vista,
        // podés dispararla desde servidor con un flash y un pequeño script aquí que la lea.
    } else {
        console.error('SweetAlert2 NO está disponible en planos.js');
    }
});
