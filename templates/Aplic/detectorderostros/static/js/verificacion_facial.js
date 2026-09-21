/**
 * verificacion_facial.js
 * Usa FaceMeshTracker reutilizable
 */
let tracker = null;

document.addEventListener('DOMContentLoaded', () => {
    Logger.moduleInit('VerificacionFacial');

    tracker = new FaceMeshTracker({
        videoId: 'inputVideo',
        canvasId: 'outputCanvas',
        fpsCounterId: 'fpsCounter',
        drawFullMesh: true,
        drawEyes: false, // Más limpio para verificación
        drawFaceOval: true,
        drawLips: false,
        onResults: (results, landmarks, dims) => {
            // No necesita dibujar texto extra, solo el tracking
        }
    });

    tracker.init();

    document.getElementById('captureBtn').addEventListener('click', () => {
        const mensaje = document.getElementById("mensaje");
        const imgData = tracker.getLatestFaceImage();
        
        if (!imgData || imgData.length < 1000) {
            mensaje.innerText = "No se detectó rostro para enviar.";
            return;
        }

        mensaje.innerText = "Verificando rostro...";
        
        fetch('/api/verificar_rostro', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ imagen: imgData })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                mensaje.innerText = "Acceso concedido. Redirigiendo...";
                setTimeout(() => window.location.href = data.redirect, 1000);
            } else {
                mensaje.innerText = "❌ " + data.msg;
            }
        })
        .catch(() => {
            mensaje.innerText = "Error al enviar la imagen.";
        });
    });
});