// ============================================================
// newRep.js - Versión ultra-simple y robusta
// ============================================================

document.addEventListener('DOMContentLoaded', function () {
    console.log('✅ newRep.js cargado');

    const modal = document.getElementById('agregarModal');
    const form = document.getElementById('formAgregarRepuesto');
    const modalLabel = document.getElementById('agregarModalLabel');
    const editarUrlInput = document.getElementById('editar-repuesto-url');

    if (!modal || !form) {
        console.error('❌ No se encontró el modal o el formulario');
        return;
    }

    // Guardar la URL original del form (para agregar)
    const agregarUrl = form.action;
    const editarUrl = editarUrlInput ? editarUrlInput.value : agregarUrl;

    // Inicializar Select2 (sin $(document).ready, directo)
    try {
        if (typeof $ !== 'undefined' && $.fn.select2) {
            $('#ubicacion').select2({
                placeholder: "Selecciona ubicaciones técnicas",
                allowClear: true,
                width: '100%',
                dropdownParent: $('#agregarModal')
            });
            console.log('✅ Select2 inicializado');
        }
    } catch (e) {
        console.warn('⚠️ Select2 no se pudo inicializar:', e);
    }

    // ============================================================
    // CUANDO EL MODAL SE VA A ABRIR (evento clave de Bootstrap)
    // ============================================================
    modal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        console.log('🔵 Modal abriéndose. Botón:', button);

        if (!button) {
            console.warn('No hay botón relacionado');
            return;
        }

        // --------- MODO EDITAR ---------
        if (button.classList.contains('btn-editar')) {
            console.log('✏️ Modo EDITAR activado');

            // 1. Cambiar título PRIMERO
            modalLabel.textContent = "Editar Repuesto";
            form.action = editarUrl;

            // 2. Cargar cada campo
            const setVal = (id, val) => {
                const el = document.getElementById(id);
                if (el) el.value = (val === null || val === undefined) ? '' : val;
            };

            setVal('nombre', button.getAttribute('data-nombre'));
            setVal('codigo', button.getAttribute('data-codigo'));
            setVal('codigo_original', button.getAttribute('data-codigo'));
            setVal('cantidad', button.getAttribute('data-cantidad'));
            setVal('equipo', button.getAttribute('data-equipo'));
            setVal('fecha_creacion', button.getAttribute('data-fecha_creacion'));
            setVal('fecha_fin', button.getAttribute('data-fecha_fin'));
            setVal('link', button.getAttribute('data-link'));
            setVal('estado', button.getAttribute('data-emojy'));
            setVal('tab_activo', button.getAttribute('data-tab_activo'));

            document.getElementById('codigo').readOnly = true;

            // 3. Select2 (ubicaciones)
            try {
                const raw = button.getAttribute('data-ruta_jerarquia') || '[]';
                let rutas = JSON.parse(raw);
                if (!Array.isArray(rutas)) rutas = rutas ? [rutas] : [];
                $('#ubicacion').val(rutas).trigger('change');
                console.log('📍 Ubicaciones cargadas:', rutas);
            } catch (e) {
                console.warn('Error parseando rutas:', e);
            }

            // 4. Imagen
            const img = button.getAttribute('data-imagen');
            const imgPreview = document.getElementById('imgPreview');
            const imgNombre = document.getElementById('imgNombre');
            if (img && img !== 'None' && img !== '' && img !== 'null') {
                imgPreview.src = '/static/uploads/Imagenes/' + img;
                imgPreview.style.display = 'block';
                imgNombre.textContent = img;
            } else {
                imgPreview.style.display = 'none';
                imgNombre.textContent = '';
            }

            // 5. Botón submit
            form.querySelector('button[type="submit"]').textContent = "Guardar Cambios";

            console.log('✅ Modal de edición cargado con éxito');
        }
        // --------- MODO AGREGAR ---------
        else {
            console.log('➕ Modo AGREGAR activado');
            modalLabel.textContent = "Agregar Nuevo Repuesto";
            form.action = agregarUrl;
            form.reset();
            document.getElementById('codigo').readOnly = false;
            document.getElementById('codigo_original').value = '';
            document.getElementById('imgPreview').style.display = 'none';
            document.getElementById('imgNombre').textContent = '';
            form.querySelector('button[type="submit"]').textContent = "Guardar Repuesto";
            if (typeof $ !== 'undefined') $('#ubicacion').val(null).trigger('change');
        }
    });

    // ============================================================
    // CUANDO EL MODAL SE CIERRA → resetear a modo AGREGAR
    // ============================================================
    modal.addEventListener('hidden.bs.modal', function () {
        modalLabel.textContent = "Agregar Nuevo Repuesto";
        form.reset();
        document.getElementById('codigo').readOnly = false;
        document.getElementById('codigo_original').value = '';
        document.getElementById('imgPreview').style.display = 'none';
        document.getElementById('imgNombre').textContent = '';
        form.querySelector('button[type="submit"]').textContent = "Guardar Repuesto";
        if (typeof $ !== 'undefined') $('#ubicacion').val(null).trigger('change');
    });
});