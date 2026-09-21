/**
 * detector_de_rostros.js
 * Usa FaceMeshTracker reutilizable
 */
let tracker = null;

document.addEventListener('DOMContentLoaded', () => {
    Logger.moduleInit('DetectorRostros');

    tracker = new FaceMeshTracker({
        videoId: 'inputVideo',
        canvasId: 'outputCanvas',
        fpsCounterId: 'fpsCounter',
        drawFullMesh: true,
        drawEyes: true,
        drawFaceOval: true,
        drawLips: true,
        onResults: (results, landmarks, dims) => {
            if (landmarks && dims) {
                const { sx, sy, faceWidth, faceHeight, width, height } = dims;
                const leftEye = landmarks[33];
                const rightEye = landmarks[263];
                const noseTip = landmarks[1];
                const forehead = landmarks[10];
                const chin = landmarks[152];

                const dx = chin.x - forehead.x;
                const dy = chin.y - forehead.y;
                const angleDeg = Math.atan2(dy, dx) * (180 / Math.PI);

                const midEyeX = (leftEye.x + rightEye.x) / 2;
                const gazeDiff = noseTip.x - midEyeX;

                let mirada = "Mirada al frente";
                if (gazeDiff < -0.01) mirada = "Mirando a la izquierda";
                else if (gazeDiff > 0.01) mirada = "Mirando a la derecha";

                let inclinacion = "Cabeza recta";
                if (angleDeg > 10) inclinacion = "Cabeza inclinada a la derecha";
                else if (angleDeg < -10) inclinacion = "Cabeza inclinada a la izquierda";

                const textoX = sx + faceWidth / 2;
                const textoY = sy + 30;

                tracker.canvasCtx.setTransform(1, 0, 0, 1, 0, 0);
                tracker.canvasCtx.font = "20px Arial";
                tracker.canvasCtx.fillStyle = "#00ffaa";
                tracker.canvasCtx.textAlign = "center";
                tracker.canvasCtx.fillText(mirada, textoX * (width / tracker.videoElement.videoWidth), textoY * (height / tracker.videoElement.videoHeight));
                tracker.canvasCtx.fillText(inclinacion, textoX * (width / tracker.videoElement.videoWidth), (textoY + 25) * (height / tracker.videoElement.videoHeight));
            }
        }
    });

    tracker.init();

    document.getElementById('captureBtn').addEventListener('click', () => {
        const imgData = tracker.getLatestFaceImage();
        Logger.info('Rostro capturado', { length: imgData.length });
        // Aquí puedes agregar lógica adicional si necesitas enviar la imagen
    });
});