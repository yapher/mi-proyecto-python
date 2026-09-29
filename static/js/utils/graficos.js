// static/js/utils/graficos.js
/**
 * Paleta de colores para gráficos (ECharts y afines).
 * Expone window.ChartPalette.getColor(categoria, index).
 *
 * Aditivo: mientras no se cargue en una página, no afecta a nada.
 * Diseñado para que graficos_repuestos.js deje de caer al gris #9E9E9E.
 */
(function () {
    'use strict';

    if (window.__chartPaletteInitialized) {
        return;
    }
    window.__chartPaletteInitialized = true;

    var PALETA = [
        '#2ecc71', '#e74c3c', '#f1c40f', '#3498db', '#9b59b6',
        '#e67e22', '#1abc9c', '#fd79a8', '#00b894', '#6c5ce7',
        '#fdcb6e', '#74b9ff', '#a29bfe', '#ff7675', '#55efc4', '#ffeaa7'
    ];

    var COLOR_MAP = {
        'disponible': '#2ecc71',
        'operativo': '#2ecc71',
        'en espera': '#f1c40f',
        'espera': '#f1c40f',
        'no disponible': '#e74c3c',
        'no operativo': '#e74c3c',
        'danado': '#e74c3c',
        'roto': '#e74c3c',
        'sin codigo': '#e67e22',
        'descontinuado': '#9b59b6',
        'actualizar codigo': '#3498db',
        'mantenimiento': '#e67e22',
        'reparando': '#e67e22',
        'reserva': '#9b59b6',
        'otros': '#9e9e9e',
        'otro': '#9e9e9e',
        'sin estado': '#9e9e9e'
    };

    var EMOJI_MAP = {
        '🟢': '#2ecc71', '🟡': '#f1c40f', '🔴': '#e74c3c',
        '🔵': '#3498db', '🟣': '#9b59b6', '🟠': '#e67e22',
        '⚪': '#ecf0f1', '⚫': '#7f8c8d', '🟤': '#8d6e63'
    };

    var KEYWORDS = [
        ['no disponible', '#e74c3c'], ['no operativo', '#e74c3c'],
        ['danado', '#e74c3c'], ['roto', '#e74c3c'],
        ['en espera', '#f1c40f'], ['espera', '#f1c40f'],
        ['mantenimiento', '#e67e22'], ['reparando', '#e67e22'],
        ['descontinuado', '#9b59b6'], ['reserva', '#9b59b6'],
        ['actualizar codigo', '#3498db'], ['sin codigo', '#e67e22'],
        ['disponible', '#2ecc71'], ['operativo', '#2ecc71'],
        ['otros', '#9e9e9e'], ['otro', '#9e9e9e']
    ];

    function norm(v) {
        return String(v || '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .trim();
    }

    function hashColor(texto) {
        var str = norm(texto) || 'sin-color';
        var hash = 0;
        for (var i = 0; i < str.length; i++) {
            hash = str.charCodeAt(i) + ((hash << 5) - hash);
            hash = hash & hash;
        }
        return 'hsl(' + (Math.abs(hash) % 360) + ', 70%, 55%)';
    }

    function getColor(categoria, index) {
        var raw = String(categoria || '');
        var n = norm(raw);

        if (COLOR_MAP[n]) return COLOR_MAP[n];

        for (var e in EMOJI_MAP) {
            if (raw.indexOf(e) !== -1) return EMOJI_MAP[e];
        }

        for (var k = 0; k < KEYWORDS.length; k++) {
            if (n.indexOf(KEYWORDS[k][0]) !== -1) return KEYWORDS[k][1];
        }

        if (typeof index === 'number' && index >= 0) {
            return PALETA[index % PALETA.length];
        }

        return hashColor(raw);
    }

    window.ChartPalette = {
        getColor: getColor,
        paleta: PALETA,
        colorMap: COLOR_MAP,
        emojiMap: EMOJI_MAP
    };
})();