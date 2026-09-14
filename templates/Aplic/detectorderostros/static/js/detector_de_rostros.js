/**
 * JavaScript para el componente Detector de Rostros
 * Maneja la detección facial con MediaPipe y la captura de imágenes
 */

// Variables globales
let videoElement;
let canvasElement;
let canvasCtx;
let lastTime = performance.now();
let fps = 0;

// Canvas auxiliar para hacer zoom
let tempCanvas;
let tempCtx;

// Inicializar FaceMesh
const faceMesh = new FaceMesh({
    locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`
});

faceMesh.setOptions({
    maxNumFaces: 1,
    refineLandmarks: true,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5
});

// Función para procesar resultados de detección facial
faceMesh.onResults(results => {
    const now = performance.now();
    fps = Math.round(1000 / (now - lastTime));
    lastTime = now;
    document.getElementById('fpsCounter').textContent = `FPS: ${fps}`;
    const width = canvasElement.width;
    const height = canvasElement.height;

    canvasCtx.save();
    canvasCtx.clearRect(0, 0, width, height);

    if (results.multiFaceLandmarks && results.multiFaceLandmarks.length > 0) {
        const landmarks = results.multiFaceLandmarks[0];

        const xs = landmarks.map(p => p.x * videoElement.videoWidth);
        const ys = landmarks.map(p => p.y * videoElement.videoHeight);
        const minX = Math.min(...xs);
        const maxX = Math.max(...xs);
        const minY = Math.min(...ys);
        const maxY = Math.max(...ys);

        const padding = 40;
        const sx = Math.max(minX - padding, 0);
        const sy = Math.max(minY - padding, 0);
        const faceWidth = Math.min(videoElement.videoWidth - sx, maxX - minX + padding * 2);
        const faceHeight = Math.min(videoElement.videoHeight - sy, maxY - minY + padding * 2);

        // Canvas temporal para zoom
        tempCanvas.width = faceWidth;
        tempCanvas.height = faceHeight;
        tempCtx.drawImage(results.image, sx, sy, faceWidth, faceHeight, 0, 0, faceWidth, faceHeight);
        canvasCtx.drawImage(tempCanvas, 0, 0, width, height);

        // Transformar contexto para dibujar malla
        canvasCtx.scale(width / faceWidth, height / faceHeight);
        canvasCtx.translate(-sx, -sy);

        // Dibujar malla facial
        drawConnectors(canvasCtx, landmarks, FACEMESH_TESSELATION, { color: '#00FFAA', lineWidth: 1 });
        drawConnectors(canvasCtx, landmarks, FACEMESH_RIGHT_EYE, { color: '#FF3030' });
        drawConnectors(canvasCtx, landmarks, FACEMESH_LEFT_EYE, { color: '#30FF30' });
        drawConnectors(canvasCtx, landmarks, FACEMESH_FACE_OVAL, { color: '#FFFF00' });
        drawConnectors(canvasCtx, landmarks, FACEMESH_LIPS, { color: '#FF00FF' });

        // Cálculo de orientación de la cabeza y mirada
        const leftEye = landmarks[33];    // Ojo izquierdo (lado derecho del canvas)
        const rightEye = landmarks[263];  // Ojo derecho (lado izquierdo del canvas)
        const noseTip = landmarks[1];     // Punta de nariz
        const forehead = landmarks[10];   // Frente (arriba)
        const chin = landmarks[152];      // Mentón

        // Calcular inclinación de cabeza (ángulo entre frente y mentón)
        const dx = chin.x - forehead.x;
        const dy = chin.y - forehead.y;
        const angleDeg = Math.atan2(dy, dx) * (180 / Math.PI);

        // Calcular dirección de la mirada (diferencia horizontal entre ojos y nariz)
        const midEyeX = (leftEye.x + rightEye.x) / 2;
        const gazeDiff = noseTip.x - midEyeX;

        let mirada = "Mirada al frente";
        if (gazeDiff < -0.01) mirada = "Mirando a la izquierda";
        else if (gazeDiff > 0.01) mirada = "Mirando a la derecha";

        let inclinacion = "Cabeza recta";
        if (angleDeg > 10) inclinacion = "Cabeza inclinada a la derecha";
        else if (angleDeg < -10) inclinacion = "Cabeza inclinada a la izquierda";

        // Coordenadas del texto (arriba del rostro)
        const textoX = sx + faceWidth / 2;
        const textoY = sy + 30;

        // Volver al sistema original para dibujar texto en posición correcta
        canvasCtx.setTransform(1, 0, 0, 1, 0, 0);
        canvasCtx.font = "20px Arial";
        canvasCtx.fillStyle = "#00ffaa";
        canvasCtx.textAlign = "center";
        canvasCtx.fillText(mirada, textoX * (width / videoElement.videoWidth), textoY * (height / videoElement.videoHeight));
        canvasCtx.fillText(inclinacion, textoX * (width / videoElement.videoWidth), (textoY + 25) * (height / videoElement.videoHeight));

    } else {
        canvasCtx.drawImage(results.image, 0, 0, width, height);
    }

    canvasCtx.restore();
});

// Inicializar cámara
const camera = new Camera(videoElement, {
    onFrame: async () => {
        await faceMesh.send({ image: videoElement });
    },
    width: 1280,
    height: 720
});

camera.start();

// Configurar canvas cuando el video esté listo
videoElement.addEventListener('loadedmetadata', () => {
    canvasElement.width = videoElement.videoWidth;
    canvasElement.height = videoElement.videoHeight;
});

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Obtener elementos del DOM
    videoElement = document.getElementById('inputVideo');
    canvasElement = document.getElementById('outputCanvas');
    canvasCtx = canvasElement.getContext('2d');
    
    // Canvas auxiliar para hacer zoom
    tempCanvas = document.createElement('canvas');
    tempCtx = tempCanvas.getContext('2d');

});
