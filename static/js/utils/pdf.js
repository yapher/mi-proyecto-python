// static/js/utils/pdf.js
(function () {
    'use strict';

    if (window.__pdfExporterInitialized) {
        return;
    }

    window.__pdfExporterInitialized = true;

    const Logger = window.Logger || {
        error: function () {}
    };

    const Notify = window.Notify || {
        error: function (msg) {
            window.alert(msg || 'Error');
        }
    };

    function hexToRgb(hex) {
        if (typeof hex !== 'string') {
            return null;
        }

        hex = hex.trim();

        if (hex.startsWith('#')) {
            hex = hex.slice(1);
        }

        if (hex.length === 3) {
            hex = hex.split('').map(function (c) {
                return c + c;
            }).join('');
        }

        if (hex.length !== 6) {
            return null;
        }

        const num = parseInt(hex, 16);

        if (isNaN(num)) {
            return null;
        }

        return {
            r: (num >> 16) & 255,
            g: (num >> 8) & 255,
            b: num & 255
        };
    }

    async function element(el, options) {
        options = options || {};

        if (!el) {
            Notify.error('No se encontró el elemento a exportar.');
            return false;
        }

        if (!window.html2canvas || !window.jspdf) {
            Notify.error('No se pudieron cargar las librerías de exportación.');
            return false;
        }

        const filename = options.filename || 'exportacion.pdf';
        const title = options.title || '';
        const backgroundColor = options.backgroundColor || '#ffffff';
        const textColor = options.textColor || '#212529';

        try {
            const canvas = await window.html2canvas(el, {
                backgroundColor: backgroundColor,
                scale: options.scale || 2,
                useCORS: true
            });

            const imgData = canvas.toDataURL('image/png');
            const jsPDF = window.jspdf.jsPDF;

            const pdf = new jsPDF({
                orientation: options.orientation || 'landscape',
                unit: 'px',
                format: [
                    canvas.width / 2 + 60,
                    canvas.height / 2 + 100
                ]
            });

            const fillRgb = hexToRgb(backgroundColor);

            if (fillRgb) {
                pdf.setFillColor(fillRgb.r, fillRgb.g, fillRgb.b);
            } else {
                pdf.setFillColor(255, 255, 255);
            }

            pdf.rect(
                0,
                0,
                pdf.internal.pageSize.width,
                pdf.internal.pageSize.height,
                'F'
            );

            const textRgb = hexToRgb(textColor);

            if (textRgb) {
                pdf.setTextColor(textRgb.r, textRgb.g, textRgb.b);
            } else {
                pdf.setTextColor(33, 37, 41);
            }

            let y = 40;

            pdf.setFontSize(20);

            if (title) {
                pdf.text(title, 30, y);
                y += 20;
            }

            pdf.setFontSize(12);
            pdf.text(
                'Fecha: ' + new Date().toLocaleDateString('es-AR'),
                30,
                y
            );

            pdf.addImage(
                imgData,
                'PNG',
                30,
                y + 20,
                canvas.width / 2,
                canvas.height / 2
            );

            pdf.save(filename);
            return true;
        } catch (err) {
            Logger.error('PdfExporter.element: error exportando PDF', err);
            Notify.error('No se pudo exportar el PDF.');
            return false;
        }
    }

    window.PdfExporter = {
        element: element,
        hexToRgb: hexToRgb
    };
})();