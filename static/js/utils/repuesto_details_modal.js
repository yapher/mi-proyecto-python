// static/js/utils/repuesto_details_modal.js
(function () {
    'use strict';

    if (window.__repuestoDetailsModalInitialized) {
        return;
    }

    window.__repuestoDetailsModalInitialized = true;

    const Logger = window.Logger || {
        warn: function () {},
        error: function () {}
    };

    function clean(value) {
        return String(value == null ? '' : value).trim();
    }

    function setText(id, value) {
        const el = document.getElementById(id);

        if (el) {
            el.textContent = clean(value);
        }
    }

    function parseLocations(img) {
        const rawJson = img.getAttribute('data-ruta_jerarquia') || '';

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
                Logger.warn('No se pudo parsear data-ruta_jerarquia en modal detalle', rawJson);
            }
        }

        const rawText = img.getAttribute('data-ubicacion') || '';

        if (rawText) {
            const text = clean(rawText);

            if (text.startsWith('[')) {
                try {
                    const parsed = JSON.parse(text);

                    if (Array.isArray(parsed)) {
                        return parsed.map(clean).filter(Boolean);
                    }
                } catch (e) {
                    // fallback
                }
            }

            return text
                .split(',')
                .map(clean)
                .filter(Boolean);
        }

        return [];
    }

    function renderUbicacion(container, valores) {
        if (!container) {
            return;
        }

        container.innerHTML = '';

        if (!valores || valores.length === 0) {
            const empty = document.createElement('span');
            empty.className = 'rep-chip rep-chip-vacio';
            empty.textContent = 'Sin ubicación';
            container.appendChild(empty);
            return;
        }

        const wrapper = document.createElement('span');
        wrapper.className = 'rep-chips';

        valores.forEach(function (ruta) {
            const chip = document.createElement('span');
            chip.className = 'rep-chip rep-chip-ubicacion';
            chip.title = ruta;
            chip.textContent = ruta;
            wrapper.appendChild(chip);
        });

        container.appendChild(wrapper);
    }

    function renderLink(container, url) {
        if (!container) {
            return;
        }

        container.innerHTML = '';

        const link = clean(url);

        if (!link) {
            return;
        }

        const a = document.createElement('a');
        a.href = link;
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
        a.className = 'text-info text-decoration-none';
        a.textContent = link;

        container.appendChild(a);
    }

    document.addEventListener('click', function (event) {
        const img = event.target.closest('.product-image');

        if (!img) {
            return;
        }

        const modalEl = document.getElementById('productModal');

        if (!modalEl) {
            Logger.warn('No se encontró #productModal para detalle de repuesto');
            return;
        }

        if (!window.bootstrap || !window.bootstrap.Modal) {
            Logger.error('Bootstrap no está disponible para abrir el modal de repuesto');
            return;
        }

        let modal = window.bootstrap.Modal.getInstance(modalEl);

        if (!modal) {
            modal = new window.bootstrap.Modal(modalEl);
        }

        setText('modalTitle', img.getAttribute('data-nombre'));
        
        const modalImage = document.getElementById('modalImage');

        if (modalImage) {
            modalImage.src = img.src || '';
            modalImage.alt = img.getAttribute('data-nombre') || 'Repuesto';
        }

        setText('modalCodigo', img.getAttribute('data-codigo'));
        setText('modalCantidad', img.getAttribute('data-cantidad'));
        setText('modalFecha', img.getAttribute('data-fecha') || img.getAttribute('data-fecha_creacion'));
        setText('modalEquipo', img.getAttribute('data-equipo'));
        setText('modalEmojy', img.getAttribute('data-emojy') || img.getAttribute('data-estado'));

        renderUbicacion(document.getElementById('modalUbicacion'), parseLocations(img));
        renderLink(document.getElementById('modalLink'), img.getAttribute('data-link'));

        const fechaFin = clean(img.getAttribute('data-fechafin') || img.getAttribute('data-fecha_fin'));
        const fechaFinLi = document.getElementById('modalFechaFinLi');
        const fechaFinSpan = document.getElementById('modalFechaFin');

        if (fechaFinLi && fechaFinSpan) {
            if (fechaFin) {
                fechaFinSpan.textContent = fechaFin;
                fechaFinLi.style.display = '';
            } else {
                fechaFinSpan.textContent = '';
                fechaFinLi.style.display = 'none';
            }
        }

        const comentario = clean(img.getAttribute('data-comentario'));
        const comentarioLi = document.getElementById('modalComentarioLi');
        const comentarioSpan = document.getElementById('modalComentario');

        if (comentarioLi && comentarioSpan) {
            if (comentario) {
                comentarioSpan.textContent = comentario;
                comentarioLi.style.display = '';
            } else {
                comentarioSpan.textContent = '';
                comentarioLi.style.display = 'none';
            }
        }

        modal.show();
    });
})();