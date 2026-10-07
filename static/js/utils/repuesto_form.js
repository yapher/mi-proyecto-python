// static/js/utils/repuesto_form.js
(function () {
    'use strict';

    if (window.__repuestoFormInitialized) {
        return;
    }

    window.__repuestoFormInitialized = true;

    const Logger = window.Logger || {
        info: function () {},
        warn: function () {},
        error: function () {},
        success: function () {}
    };

    window.RepuestoUtils = window.RepuestoUtils || {};

    if (typeof window.RepuestoUtils.limpiar !== 'function') {
        window.RepuestoUtils.limpiar = function (valor) {
            return String(valor == null ? '' : valor).trim();
        };
    }

    const state = {
        mode: 'add',
        pendingCodigo: null
    };

    const IMAGES_BASE = '/static/uploads/Imagenes/';

    const PATH_TO_ENDPOINT = [
        ['/graficos_repuestos', 'indexgraficos_repuestos.indexgraficos_repuestos'],
        ['/lista_repuestos', 'indexlista_repuestos.indexlista_repuestos'],
        ['/inventario', 'indexinventario.indexinventario'],
        ['/estadosRep', 'indexEstadoRep.indexEstadoRep']
    ];

    function qs(selector, context) {
        return (context || document).querySelector(selector);
    }

    function clean(value) {
        return String(value == null ? '' : value).trim();
    }

    function getAttr(el, names) {
        if (!el) return '';

        for (const name of names) {
            if (el.hasAttribute(name)) {
                return clean(el.getAttribute(name));
            }
        }

        return '';
    }

    function setVal(selector, value) {
        const el = qs(selector);
        if (el) {
            el.value = value == null ? '' : value;
        }
    }

    function findForm() {
        return qs('#formAgregarRepuesto');
    }

    // ============================================================
    // IMAGE UPLOADER (componente reutilizable, el mismo de Instalaciones)
    // ============================================================
    let uploader = null;

    function getUploader() {
        if (uploader) {
            return uploader;
        }

        if (typeof window.ImageUploader !== 'function' || !qs('#repImagenInput')) {
            return null;
        }

        uploader = new window.ImageUploader({
            previewId: 'repImagenPreview',
            placeholderId: 'repImagenPlaceholder',
            inputId: 'repImagenInput',
            removeBtnId: 'repImagenQuitar',
            infoId: 'repImagenInfo',
            wrapperId: 'repImagenWrapper',
            loggerPrefix: '[Repuestos:Image]'
        });

        return uploader;
    }

    function imageUrlFromButton(btn) {
        const raw = getAttr(btn, ['data-imagen']).replace(/\\/g, '/');

        if (!raw) {
            return '';
        }

        const sinQuery = raw.split('?')[0];

        if (/^(https?:)?\/\//.test(sinQuery) || sinQuery.charAt(0) === '/') {
            return sinQuery;
        }

        const archivo = sinQuery.split('/').pop();

        return archivo ? IMAGES_BASE + encodeURIComponent(archivo) : '';
    }

    function getUrlById(id, fallback) {
        const el = qs(id);
        return clean(el ? el.value : '') || fallback;
    }

    function agregarUrl() {
        return getUrlById('#agregar-repuesto-url', '/agregar_repuesto');
    }

    function editarUrl() {
        return getUrlById('#editar-repuesto-url', '/editar_repuesto');
    }

    function eliminarUrl() {
        const explicit = getUrlById('#eliminar-repuesto-url', '');
        if (explicit) return explicit;

        return editarUrl().replace('/editar_repuesto', '/eliminar_repuesto');
    }

    function endpointFromPath(path) {
        const normalized = clean(path).toLowerCase();

        for (const [route, endpoint] of PATH_TO_ENDPOINT) {
            if (normalized.startsWith(route.toLowerCase())) {
                return endpoint;
            }
        }

        return 'indexEstadoRep.indexEstadoRep';
    }

    function defaultReturnTo() {
        return endpointFromPath(window.location.pathname);
    }

    function resolveReturnTo(btn) {
        return (
            getAttr(btn, ['data-return_to', 'data-return-to']) ||
            clean(qs('#return_to') ? qs('#return_to').value : '') ||
            (window.RepuestoEndpoints && window.RepuestoEndpoints.returnTo) ||
            defaultReturnTo()
        );
    }

    function resolveTab(btn) {
        return (
            getAttr(btn, ['data-tab_activo', 'data-tab-activo']) ||
            clean(qs('#tab_activo') ? qs('#tab_activo').value : '') ||
            ''
        );
    }

    function setModalTitle(text) {
        const title = qs('#agregarModalLabel');
        if (title) {
            title.textContent = text;
        }
    }

    function setSubmitText(text) {
        const button = qs('#btnSubmitRepuesto');
        if (button) {
            button.textContent = text;
        }
    }

    function setFormAction(url) {
        const form = findForm();
        if (form) {
            form.action = url;
        }
    }

    function hasJquerySelect2() {
        return !!(window.jQuery && window.jQuery.fn && window.jQuery.fn.select2);
    }

    function ensureSelect2() {
        const select = qs('#ubicacion');

        if (!select || !hasJquerySelect2()) {
            return null;
        }

        const $select = window.jQuery(select);

        if ($select.data('rs-select2-initialized')) {
            return $select;
        }

        const modal = qs('#agregarModal');

        $select.select2({
            placeholder: select.getAttribute('data-placeholder') || 'Seleccioná una o más ubicaciones técnicas',
            allowClear: true,
            width: '100%',
            dropdownParent: modal ? window.jQuery(modal) : window.jQuery('body'),
            minimumResultsForSearch: 0,
            dropdownCssClass: 'rep-ubicacion-dropdown'
        });

        $select.data('rs-select2-initialized', true);

        return $select;
    }

    function setLocations(values) {
        const select = qs('#ubicacion');

        if (!select) {
            return;
        }

        const lista = Array.isArray(values) ? values.map(clean).filter(Boolean) : [];

        if (hasJquerySelect2()) {
            const $select = ensureSelect2();

            if ($select) {
                $select.val(lista).trigger('change');
                return;
            }
        }

        Array.from(select.options).forEach(function (option) {
            option.selected = lista.indexOf(clean(option.value)) !== -1;
        });
    }

    function parseLocations(btn) {
        const rawJson = getAttr(btn, ['data-ruta_jerarquia', 'data-ruta-jerarquia']);

        if (rawJson) {
            try {
                const parsed = JSON.parse(rawJson);

                if (Array.isArray(parsed)) {
                    return parsed.map(function (item) {
                        if (item && typeof item === 'object') {
                            return clean(item.ruta_jerarquia || item.ruta || item.nombre || item.value || '');
                        }

                        return clean(item);
                    }).filter(Boolean);
                }

                if (typeof parsed === 'string') {
                    return [clean(parsed)].filter(Boolean);
                }
            } catch (e) {
                Logger.warn('No se pudo parsear data-ruta_jerarquia', rawJson);
            }
        }

        const rawText = getAttr(btn, ['data-ubicacion', 'data-ubicacion-tecnica']);

        if (rawText) {
            const text = clean(rawText);

            if (text.startsWith('[')) {
                try {
                    const parsed = JSON.parse(text);

                    if (Array.isArray(parsed)) {
                        return parsed.map(clean).filter(Boolean);
                    }
                } catch (e) {
                    // fallback a split por coma
                }
            }

            return text
                .split(',')
                .map(clean)
                .filter(Boolean);
        }

        return [];
    }

    function resetForm(keepContext) {
        const form = findForm();

        if (!form) {
            return;
        }

        form.reset();

        setVal('#codigo', '');
        setVal('#nombre', '');
        setVal('#cantidad', '0');
        setVal('#equipo', '');
        setVal('#link', '');
        setVal('#estado', '');
        setVal('#comentario', '');
        setVal('#fecha_creacion', '');
        setVal('#fecha_fin', '');
        setVal('#sanitized_id', '');
        setVal('#codigo_original', '');
        setVal('#repEliminarImagen', '');

        if (!keepContext) {
            setVal('#return_to', defaultReturnTo());
            setVal('#tab_activo', '');
        }

        setLocations([]);

        const up = getUploader();
        if (up) {
            up.reset();
        }

        setModalTitle('Agregar nuevo repuesto');
        setSubmitText('Guardar Repuesto');
        setFormAction(agregarUrl());

        state.mode = 'add';
        state.pendingCodigo = null;
    }

    function fillEdit(btn) {
        const codigo = getAttr(btn, ['data-codigo', 'data-sanitized_id']);

        if (!codigo) {
            Logger.warn('Botón de edición sin data-codigo');
            return;
        }

        state.mode = 'edit';
        state.pendingCodigo = codigo;

        setVal('#codigo', getAttr(btn, ['data-codigo']) || codigo);
        setVal('#codigo_original', codigo);
        setVal('#sanitized_id', getAttr(btn, ['data-sanitized_id']) || codigo);

        setVal('#nombre', getAttr(btn, ['data-nombre']));
        setVal('#cantidad', getAttr(btn, ['data-cantidad']) || '0');
        setVal('#equipo', getAttr(btn, ['data-equipo']));
        setVal('#link', getAttr(btn, ['data-link']));

        setVal(
            '#estado',
            getAttr(btn, ['data-estado', 'data-emojy', 'data-emoji'])
        );

        setVal('#comentario', getAttr(btn, ['data-comentario']));

        setVal(
            '#fecha_creacion',
            getAttr(btn, ['data-fecha', 'data-fecha_creacion', 'data-fecha-creacion'])
        );

        setVal(
            '#fecha_fin',
            getAttr(btn, ['data-fecha_fin', 'data-fecha-fin', 'data-fechafin'])
        );

        setVal('#return_to', resolveReturnTo(btn));
        setVal('#tab_activo', resolveTab(btn));
        setVal('#repEliminarImagen', '');

        setLocations(parseLocations(btn));

        // ✅ Imagen actual del repuesto en el uploader
        const up = getUploader();
        if (up) {
            const url = imageUrlFromButton(btn);

            if (url) {
                up.loadExisting(url);
            } else {
                up.reset();
            }
        }

        setModalTitle('Editar repuesto');
        setSubmitText('Guardar cambios');
        setFormAction(editarUrl());
    }

    function addHiddenInput(form, name, value) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = name;
        input.value = value == null ? '' : value;
        form.appendChild(input);
    }

    function deleteRepuesto(btn) {
        const codigo = getAttr(btn, ['data-codigo', 'data-sanitized_id']);

        if (!codigo) {
            if (window.Notify && window.Notify.warning) {
                window.Notify.warning('No se identificó el repuesto a eliminar.');
            } else {
                alert('No se identificó el repuesto a eliminar.');
            }

            return;
        }

        const nombre = getAttr(btn, ['data-nombre']) || codigo;
        const returnTo = resolveReturnTo(btn);
        const tabActivo = resolveTab(btn);

        const doDelete = function () {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = eliminarUrl();
            form.style.display = 'none';

            addHiddenInput(form, 'codigo', codigo);
            addHiddenInput(form, 'return_to', returnTo);
            addHiddenInput(form, 'tab_activo', tabActivo);

            document.body.appendChild(form);
            form.submit();
        };

        if (window.Notify && window.Notify.delete) {
            window.Notify.delete(nombre, doDelete);
        } else if (window.confirm('¿Eliminar "' + nombre + '"? Esta acción no se puede deshacer.')) {
            doDelete();
        }
    }

    document.addEventListener('click', function (event) {
        const target = event.target;

        if (!target || !target.closest) {
            return;
        }

        const editBtn = target.closest(
            '.repuesto-btn-editar, .btn-editar[data-repuesto="1"], .btn-editar[data-codigo][data-bs-target="#agregarModal"]'
        );

        if (editBtn) {
            fillEdit(editBtn);
            return;
        }

        const deleteBtn = target.closest(
            '.repuesto-btn-eliminar, .btn-eliminar[data-repuesto="1"], .btn-eliminar[data-codigo]'
        );

        if (deleteBtn) {
            event.preventDefault();
            event.stopPropagation();
            deleteRepuesto(deleteBtn);
            return;
        }

        const addBtn = target.closest('[data-bs-toggle="modal"][data-bs-target="#agregarModal"]');

        if (addBtn && !editBtn) {
            state.mode = 'add';
        }
    }, true);

    document.addEventListener('shown.bs.modal', function (event) {
        if (!event.target || event.target.id !== 'agregarModal') {
            return;
        }

        ensureSelect2();
        getUploader();

        if (state.mode === 'add') {
            resetForm(false);
        }
    }, true);

    document.addEventListener('hidden.bs.modal', function (event) {
        if (!event.target || event.target.id !== 'agregarModal') {
            return;
        }

        resetForm(false);
    }, true);

    document.addEventListener('submit', function (event) {
        const form = event.target;

        if (!form || form.id !== 'formAgregarRepuesto') {
            return;
        }

        const returnTo = clean(qs('#return_to') ? qs('#return_to').value : '') || resolveReturnTo(null);
        const tabActivo = clean(qs('#tab_activo') ? qs('#tab_activo').value : '') || resolveTab(null);

        setVal('#return_to', returnTo);
        setVal('#tab_activo', tabActivo);

        // ✅ Si se quitó la imagen y no se eligió otra, avisar al backend
        const up = getUploader();
        const quitada = !!(up && up.wasRemoved() && !up.getSelectedFile());
        setVal('#repEliminarImagen', quitada ? 'true' : '');

        if (state.mode === 'edit') {
            const codigoOriginal = state.pendingCodigo ||
                clean(qs('#codigo_original') ? qs('#codigo_original').value : '') ||
                clean(qs('#sanitized_id') ? qs('#sanitized_id').value : '');

            setVal('#codigo_original', codigoOriginal);
            setVal('#sanitized_id', codigoOriginal);
            setFormAction(editarUrl());
        } else {
            setVal('#codigo_original', '');
            setVal('#sanitized_id', '');
            setFormAction(agregarUrl());
        }
    }, true);

    window.RepuestoForm = {
        reset: resetForm,
        editar: fillEdit,
        eliminar: deleteRepuesto,
        setLocations: setLocations,
        getLocations: function () {
            const select = qs('#ubicacion');

            if (!select) {
                return [];
            }

            if (hasJquerySelect2()) {
                const $select = window.jQuery(select);

                if ($select.data('rs-select2-initialized')) {
                    return ($select.val() || []).map(clean).filter(Boolean);
                }
            }

            return Array.from(select.selectedOptions)
                .map(function (option) {
                    return clean(option.value);
                })
                .filter(Boolean);
        }
    };

    Logger.success('RepuestoForm inicializado');
})();