/**
 * repuestoForm.js
 * Lógica de manipulación del formulario.
 * Responsabilidad: Resetear campos, cargar datos de edición y manejar la imagen.
 */
const RepuestoForm = {
    /**
     * Resetea el formulario a su estado inicial (modo "Agregar")
     */
    resetear: () => {
        const form = document.getElementById('formAgregarRepuesto');
        if (form) form.reset();
        
        if (typeof $ !== 'undefined' && $('#ubicacion').length) {
            $('#ubicacion').val(null).trigger('change');
        }
        
        document.getElementById('agregarModalLabel').textContent = "Agregar Nuevo Repuesto";
        document.getElementById('codigo').readOnly = false;
        document.getElementById('codigo_original').value = '';
        document.getElementById('imgPreview').style.display = 'none';
        document.getElementById('imgNombre').textContent = '';
        
        const btnSubmit = document.querySelector('#formAgregarRepuesto button[type="submit"]');
        if (btnSubmit) btnSubmit.textContent = "Guardar Repuesto";
    },

    /**
     * Carga los datos del repuesto en el formulario (modo "Editar")
     */
    cargarDatos: (btn) => {
        document.getElementById('agregarModalLabel').textContent = "Editar Repuesto";
        document.getElementById('codigo').readOnly = true;
        
        const btnSubmit = document.querySelector('#formAgregarRepuesto button[type="submit"]');
        if (btnSubmit) btnSubmit.textContent = "Guardar Cambios";

        // 1. Campos de texto
        document.getElementById('nombre').value = RepuestoUtils.limpiar(btn.getAttribute('data-nombre'));
        document.getElementById('codigo').value = RepuestoUtils.limpiar(btn.getAttribute('data-codigo'));
        document.getElementById('codigo_original').value = RepuestoUtils.limpiar(btn.getAttribute('data-codigo'));
        document.getElementById('cantidad').value = RepuestoUtils.limpiar(btn.getAttribute('data-cantidad'));
        document.getElementById('equipo').value = RepuestoUtils.limpiar(btn.getAttribute('data-equipo'));
        document.getElementById('fecha_creacion').value = RepuestoUtils.limpiar(btn.getAttribute('data-fecha_creacion'));
        document.getElementById('fecha_fin').value = RepuestoUtils.limpiar(btn.getAttribute('data-fecha_fin'));
        document.getElementById('link').value = RepuestoUtils.limpiar(btn.getAttribute('data-link'));
        document.getElementById('estado').value = RepuestoUtils.limpiar(btn.getAttribute('data-emojy'));
        document.getElementById('tab_activo').value = RepuestoUtils.limpiar(btn.getAttribute('data-tab_activo'));

        // 2. Select2 (Ubicaciones)
        const rutas = RepuestoUtils.parsearRutas(btn.getAttribute('data-ruta_jerarquia'));
        if (typeof $ !== 'undefined' && $('#ubicacion').length) {
            $('#ubicacion').val(rutas).trigger('change');
        }

        // 3. Previsualización de Imagen
        const imagen = RepuestoUtils.limpiar(btn.getAttribute('data-imagen'));
        const imgPreview = document.getElementById('imgPreview');
        const imgNombre = document.getElementById('imgNombre');
        
        if (imagen && imagen !== '') {
            imgPreview.src = '/static/uploads/Imagenes/' + imagen;
            imgPreview.style.display = 'block';
            imgNombre.textContent = imagen;
        } else {
            imgPreview.style.display = 'none';
            imgNombre.textContent = '';
        }

        console.log("✅ Modal de edición cargado con:", {
            codigo: document.getElementById('codigo').value,
            nombre: document.getElementById('nombre').value,
            estado: document.getElementById('estado').value,
            ubicaciones: rutas
        });
    },

    /**
     * Configura la URL de acción del formulario según el modo
     */
    configurarAccion: (esEdicion, tabActivo = '') => {
        const form = document.getElementById('formAgregarRepuesto');
        const editarUrl = document.getElementById('editar-repuesto-url')?.value;
        const agregarUrl = form?.getAttribute('action');
        
        if (form) {
            form.action = esEdicion && editarUrl ? editarUrl : agregarUrl;
        }
        
        const inputTab = document.getElementById('tab_activo');
        if (inputTab) inputTab.value = tabActivo;
    }
};