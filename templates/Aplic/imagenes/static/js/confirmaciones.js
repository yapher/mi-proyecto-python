// confirmaciones.js: manejar confirmaciones de agregar, editar y eliminar
document.addEventListener('DOMContentLoaded', function () {
    if (typeof Swal === 'undefined') return;

    // Confirmación para agregar planos
    document.querySelectorAll('.btn-agregar-plano').forEach(btn => {
        btn.addEventListener('click', () => {
            Swal.fire({ icon: 'success', title: 'Listo!!', timer: 1200, showConfirmButton: false });
        });
    });

    // Confirmación editar
    document.querySelectorAll('.btn-editar-plano').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const form = btn.closest('form');
            Swal.fire({
                title: '¿Guardar cambios?',
                text: '¿Deseas actualizar este plano?',
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Sí, actualizar',
                cancelButtonText: 'Cancelar',
                buttonsStyling: false,
                customClass: { confirmButton: 'btn-editar', cancelButton: 'btn-cancelar' }
            }).then(result => {
                if (result.isConfirmed) form.submit();
            });
        });
    });

    // Confirmación eliminar
    document.querySelectorAll('.btn-eliminar-plano').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const form = btn.closest('form');
            Swal.fire({
                title: '¿Estás seguro?',
                text: 'Esta acción eliminará el plano definitivamente.',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar',
                buttonsStyling: false,
                customClass: { confirmButton: 'btn-eliminar', cancelButton: 'btn-cancelar' }
            }).then(result => {
                if (result.isConfirmed) form.submit();
            });
        });
    });
});
