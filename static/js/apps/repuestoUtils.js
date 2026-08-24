/**
 * repuestoUtils.js
 * Funciones auxiliares y de utilidad para el manejo de repuestos.
 * Responsabilidad: Limpieza de datos, parseo y configuración de plugins.
 */
const RepuestoUtils = {
    /**
     * Limpia valores nulos, "None" o "null" que vienen de Jinja/Backend
     */
    limpiar: (valor) => {
        if (valor === null || valor === undefined) return '';
        const str = String(valor).trim();
        if (str === 'None' || str === 'null' || str === 'undefined') return '';
        return str;
    },

    /**
     * Parsea de forma segura el atributo data-ruta_jerarquia (que viene como JSON string)
     */
    parsearRutas: (rawRutas) => {
        let rutas = [];
        try {
            const parsed = JSON.parse(rawRutas || '[]');
            if (Array.isArray(parsed)) {
                rutas = parsed;
            } else if (parsed) {
                rutas = [parsed];
            }
        } catch (e) {
            console.warn("⚠️ Error al parsear ruta_jerarquia:", e);
ا
        }
        return rutas;
    },

    /**
     * Inicializa Select2 de forma segura si la librería está disponible
     */
    initSelect2: () => {
        if (typeof $ !== 'undefined' && $('#ubicacion').length) {
            $('#ubicacion').select2({
                placeholder: "Selecciona una o más ubicaciones técnicas",
                allowClear: true,
                width: '100%',
                dropdownParent: $('#agregarModal')
            });
        }
    }
};