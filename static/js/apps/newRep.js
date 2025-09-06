$(document).ready(function () {
    $('#ubicacion').select2({
        placeholder: "Selecciona una o más ubicaciones técnicas",
        allowClear: true,
        width: 'resolve',
        dropdownParent: $('#agregarModal')
    });
});

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-bs-target="#agregarModal"].btn-agregar').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const form = document.getElementById('formAgregarRepuesto');
            form.reset();
            $('#ubicacion').val(null).trigger('change');

            document.getElementById('agregarModalLabel').textContent = "Agregar Nuevo Repuesto";
            form.action = "{{ url_for('indexEstadoRep.agregar_repuesto') }}";
            document.getElementById('codigo').readOnly = false;
            document.getElementById('tab_activo').value = btn.getAttribute('data-sanitized_id') || '';

            document.getElementById('imgPreview').style.display = 'none';
            document.getElementById('imgNombre').textContent = '';
            form.querySelector('button[type="submit"]').textContent = "Guardar Repuesto";
        });
    });

    document.querySelectorAll('.btn-editar').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const form = document.getElementById('formAgregarRepuesto');

            document.getElementById('agregarModalLabel').textContent = "Editar Repuesto";
            form.action = "{{ url_for('indexEstadoRep.editar_repuesto') }}";

            document.getElementById('nombre').value = btn.getAttribute('data-nombre') || '';
            document.getElementById('codigo').value = btn.getAttribute('data-codigo') || '';
            document.getElementById('codigo_original').value = btn.getAttribute('data-codigo') || '';
            document.getElementById('cantidad').value = btn.getAttribute('data-cantidad') || '';
            document.getElementById('equipo').value = btn.getAttribute('data-equipo') || '';
            document.getElementById('fecha_creacion').value = btn.getAttribute('data-fecha_creacion') || '';
            document.getElementById('fecha_fin').value = btn.getAttribute('data-fecha_fin') || '';
            document.getElementById('link').value = btn.getAttribute('data-link') || '';
            document.getElementById('estado').value = btn.getAttribute('data-emojy') || '';
            document.getElementById('tab_activo').value = btn.getAttribute('data-tab_activo') || '';

            const rutasSeleccionadas = btn.getAttribute('data-ruta_jerarquia') || '[]';
            let valoresSeleccionados = [];
            try {
                valoresSeleccionados = JSON.parse(rutasSeleccionadas);
                if (!Array.isArray(valoresSeleccionados)) {
                    valoresSeleccionados = [valoresSeleccionados];
                }
            } catch {
                if (rutasSeleccionadas && rutasSeleccionadas !== '[]') {
                    valoresSeleccionados = [rutasSeleccionadas];
                }
            }
            $('#ubicacion').val(valoresSeleccionados).trigger('change');

            const imagen = btn.getAttribute('data-imagen');
            if (imagen && imagen !== "None") {
                document.getElementById('imgPreview').src = '/static/uploads/Imagenes/' + imagen;
                document.getElementById('imgPreview').style.display = 'block';
                document.getElementById('imgNombre').textContent = imagen;
            } else {
                document.getElementById('imgPreview').style.display = 'none';
                document.getElementById('imgNombre').textContent = '';
            }

            form.querySelector('button[type="submit"]').textContent = "Guardar Cambios";
        });
    });
});
