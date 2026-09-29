// static/js/utils/chart.js
(function () {
    'use strict';

    if (window.__chartPaletteInitialized) {
        return;
    }

    window.__chartPaletteInitialized = true;

    const PALETA = [
        '#2ecc71',
        '#e74c3c',
        '#f1c40f',
        '#3498db',
        '#9b59b6',
        '#e67e22',
        '#1abc9c',
        '#fd79a8',
        '#00b894',
        '#6c5ce7',
        '#fdcb6e',
        '#74b9ff',
        '#a29bfe',
        '#ff7675',
        '#55efc4',
        '#ffeaa7'
    ];

    const COLOR_MAP = {
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

    const EMOJI_MAP = {
        '🟢': '#2ecc71',
        '🟡': '#f1c40f',
        '🔴': '#e74c3c',
        '🔵': '#3498db',
        '🟣': '#9b59b6',
        '🟠': '#e67e22',
        '⚪': '#ecf0f1',
        '⚫': '#7f8c8d',
        '🟤': '#8d6e63'
    };

    const KEYWORDS = [
        ['no disponible', '#e74c3c'],
        ['no operativo', '#e74c3c'],
        ['danado', '#e74c3c'],
        ['roto', '#e74c3c'],
        ['en espera', '#f1c40f'],
        ['espera', '#f1c40f'],
        ['mantenimiento', '#e67e22'],
        ['reparando', '#e67e22'],
        ['descontinuado', '#9b59b6'],
        ['reserva', '#9b59b6'],
        ['actualizar codigo', '#3498db'],
        ['sin codigo', '#e67e22'],
        ['disponible', '#2ecc71'],
        ['operativo', '#2ecc71'],
        ['otros', '#9e9e9e'],
        ['otro', '#9e9e9e']
    ];

    function normalizarTexto(valor) {
        return String(valor || '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .trim();
    }

    function hashColor(texto) {
        const str = normalizarTexto(texto) || 'sin-color';
        let hash = 0;

        for (let i = 0; i < str.length; i++) {
            hash = str.charCodeAt(i) + ((hash << 5) - hash);
            hash = hash & hash;
        }

        const hue = Math.abs(hash) % 360;
        return 'hsl(' + hue + ', 70%, 55%)';
    }

    function getColor(categoria, index) {
        const raw = String(categoria || '');
        const norm = normalizarTexto(raw);

        if (COLOR_MAP[norm]) {
            return COLOR_MAP[norm];
        }

        for (const emoji of Object.keys(EMOJI_MAP)) {
            if (raw.indexOf(emoji) !== -1) {
                return EMOJI_MAP[emoji];
            }
        }

        for (let i = 0; i < KEYWORDS.length; i++) {
            const keyword = KEYWORDS[i][0];
            const color = KEYWORDS[i][1];

            if (norm.indexOf(keyword) !== -1) {
                return color;
            }
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