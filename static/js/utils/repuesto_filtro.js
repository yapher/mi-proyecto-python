// static/js/utils/repuesto_filtro.js
/**
 * Filtro en vivo reutilizable para repuestos (cards o filas de tabla).
 * Ignora mayúsculas y tildes. Se activa solo con atributos data-*.
 *
 *  Contenedor : [data-repuesto-filtro]
 *               opcional data-filtro-contador="#selector" (cantidad visible)
 *  Texto      : <input data-filtro-campos="nombre,comentario" data-filtro-param="nombre">
 *               campos válidos: nombre, comentario, codigo, * (todo el texto del ítem)
 *  Igualdad   : <select|input data-filtro-igual="estado" data-filtro-param="estado">
 *               compara con data-<campo> del ítem (estado, fecha_creacion, fecha_fin)
 *  Vencidos   : <input type="checkbox" data-filtro-vencidos data-filtro-param="vencidos" value="1">
 *               un ítem está vencido si su data-fecha_fin es anterior a hoy
 *  Ítems      : [data-filtro-item] con data-nombre, data-codigo, data-comentario,
 *               data-estado, data-fecha_creacion, data-fecha_fin
 *  Sin result.: [data-filtro-vacio]
 *  Form PDF   : <form data-filtro-pdf>: al enviar copia cada data-filtro-param
 *               al input name=<param> del formulario.
 */
(function () {
    'use strict';

    if (window.RepuestoFiltro) {
        return;
    }

    const cache = new WeakMap();
    const timers = new WeakMap();

    const SELECTOR_CONTROLES =
        '[data-filtro-campos], [data-filtro-igual], [data-filtro-vencidos]';

    function normalizar(texto) {
        return String(texto == null ? '' : texto)
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .trim();
    }

    function hoyISO() {
        const d = new Date();
        const mm = String(d.getMonth() + 1).padStart(2, '0');
        const dd = String(d.getDate()).padStart(2, '0');
        return d.getFullYear() + '-' + mm + '-' + dd;
    }

    function indiceDe(item) {
        let idx = cache.get(item);

        if (!idx) {
            idx = {
                nombre: normalizar(item.dataset.nombre),
                comentario: normalizar(item.dataset.comentario),
                codigo: normalizar(item.dataset.codigo),
                '*': null
            };
            cache.set(item, idx);
        }

        return idx;
    }

    function valorDe(item, campo) {
        const idx = indiceDe(item);

        if (campo === '*') {
            if (idx['*'] === null) {
                idx['*'] = normalizar(item.textContent);
            }
            return idx['*'];
        }

        return idx[campo] || '';
    }

    function aplicar(contenedor) {
        const hoy = hoyISO();

        const filtrosTexto = Array.from(contenedor.querySelectorAll('[data-filtro-campos]'))
            .map(function (input) {
                return {
                    termino: normalizar(input.value),
                    campos: String(input.dataset.filtroCampos || '')
                        .split(',')
                        .map(function (c) { return c.trim(); })
                        .filter(Boolean)
                };
            })
            .filter(function (f) { return f.termino && f.campos.length; });

        const filtrosIgual = Array.from(contenedor.querySelectorAll('[data-filtro-igual]'))
            .map(function (input) {
                return {
                    campo: input.dataset.filtroIgual,
                    valor: String(input.value || '').trim()
                };
            })
            .filter(function (f) { return f.valor; });

        const vencidosInput = contenedor.querySelector('[data-filtro-vencidos]');
        const soloVencidos = !!(vencidosInput && vencidosInput.checked);

        const items = contenedor.querySelectorAll('[data-filtro-item]');
        let visibles = 0;

        items.forEach(function (item) {
            let ok = filtrosTexto.every(function (f) {
                return f.campos.some(function (campo) {
                    return valorDe(item, campo).indexOf(f.termino) !== -1;
                });
            });

            if (ok) {
                ok = filtrosIgual.every(function (f) {
                    return String(item.dataset[f.campo] || '').trim() === f.valor;
                });
            }

            if (ok && soloVencidos) {
                const fin = String(item.dataset.fecha_fin || '').trim();
                ok = !!fin && fin < hoy;
            }

            item.style.display = ok ? '' : 'none';

            if (ok) {
                visibles++;
            }
        });

        const selector = contenedor.dataset.filtroContador;

        if (selector) {
            const contador = document.querySelector(selector);

            if (contador) {
                contador.textContent = visibles;
            }
        }

        contenedor.querySelectorAll('[data-filtro-vacio]').forEach(function (aviso) {
            aviso.classList.toggle('d-none', visibles > 0 || items.length === 0);
        });
    }

    function programar(contenedor) {
        clearTimeout(timers.get(contenedor));
        timers.set(contenedor, setTimeout(function () {
            aplicar(contenedor);
        }, 80));
    }

    function alCambiar(event) {
        const control = event.target;

        if (!control || !control.closest || !control.matches(SELECTOR_CONTROLES)) {
            return;
        }

        const contenedor = control.closest('[data-repuesto-filtro]');

        if (contenedor) {
            programar(contenedor);
        }
    }

    // Delegación: funciona también con contenido cargado por fetch (modales)
    document.addEventListener('input', alCambiar);
    document.addEventListener('change', alCambiar);

    // El PDF sale con lo que se ve en pantalla
    document.addEventListener('submit', function (event) {
        const form = event.target;

        if (!form || !form.matches || !form.matches('[data-filtro-pdf]')) {
            return;
        }

        const contenedor = form.closest('[data-repuesto-filtro]');

        if (!contenedor) {
            return;
        }

        contenedor.querySelectorAll('[data-filtro-param]').forEach(function (control) {
            const destino = form.querySelector('input[name="' + control.dataset.filtroParam + '"]');

            if (!destino) {
                return;
            }

            if (control.type === 'checkbox') {
                destino.value = control.checked ? (control.value || '1') : '';
            } else {
                destino.value = (control.value || '').trim();
            }
        });
    }, true);

    function iniciar() {
        document.querySelectorAll('[data-repuesto-filtro]').forEach(aplicar);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', iniciar);
    } else {
        iniciar();
    }

    window.RepuestoFiltro = {
        normalizar: normalizar,
        aplicar: aplicar
    };
})();