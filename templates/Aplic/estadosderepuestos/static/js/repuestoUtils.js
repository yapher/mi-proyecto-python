// templates/Aplic/estadosderepuestos/static/js/repuestoUtils.js
/*
    Compatibilidad mínima.
    La lógica real está en:
    - /static/js/utils/table.js
    - /static/js/utils/repuesto_form.js
*/

(function () {
    'use strict';

    window.RepuestoUtils = window.RepuestoUtils || {};
    window.RepuestoUtils.limpiar = function (valor) {
        return String(valor || '').trim();
    };

    if (window.__repuestoCompatLoader) {
        return;
    }

    window.__repuestoCompatLoader = true;

    var files = [
        '/static/js/utils/table.js',
        '/static/js/utils/repuesto_form.js'
    ];

    function load(index) {
        if (index >= files.length) {
            return;
        }

        var script = document.createElement('script');
        script.src = files[index];
        script.onload = function () {
            load(index + 1);
        };
        document.head.appendChild(script);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            load(0);
        });
    } else {
        load(0);
    }
})();