/**
 * login_facial.js
 * Reconocimiento facial para login.
 * - Usa CSRF correctamente.
 * - No usa document.write.
 * - Redirige de forma limpia según respuesta del servidor.
 */
(function () {
    'use strict';

    if (window.__loginFacialInitialized) return;
    window.__loginFacialInitialized = true;

    const videoElement = document.getElementById('inputVideo');
    const canvasElement = document.getElementById('outputCanvas');
    const faceRecognitionSection = document.getElementById('faceRecognitionSection');
    const showFaceRecBtn = document.getElementById('showFaceRecBtn');
    const captureBtn = document.getElementById('captureBtn');
    const fpsCounter = document.getElementById('fpsCounter');

    if (!videoElement || !canvasElement || !faceRecognitionSection || !showFaceRecBtn || !captureBtn) {
        return;
    }

    const canvasCtx = canvasElement.getContext('2d');
    const tempCanvas = document.createElement('canvas');
    const tempCtx = tempCanvas.getContext('2d');

    let cameraStarted = false;
    let lastTime = performance.now();

    function dataURLtoBlob(dataurl) {
        const arr = dataurl.split(',');
        const mime = arr[0].match(/:(.*?);/)[1];
        const bstr = atob(arr[1]);
        let n = bstr.length;
        const u8arr = new Uint8Array(n);

        while (n--) {
            u8arr[n] = bstr.charCodeAt(n);
        }

        return new Blob([u8arr], { type: mime });
    }

    function getCsrfToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.content : '';
    }

    if (typeof FaceMesh === 'undefined') {
        console.error('MediaPipe FaceMesh no está cargado.');
        return;
    }

    const faceMesh = new FaceMesh({
        locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`
    });

    faceMesh.setOptions({
        maxNumFaces: 1,
        refineLandmarks: true,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5
    });

    faceMesh.onResults(results => {
        if (faceRecognitionSection.style.display === 'none') {
            return;
        }

        const now = performance.now();
        const fps = Math.round(1000 / (now - lastTime));
        lastTime = now;

        if (fpsCounter) {
            fpsCounter.textContent = `FPS: ${fps}`;
        }

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

            tempCanvas.width = faceWidth;
            tempCanvas.height = faceHeight;

            tempCtx.drawImage(results.image, sx, sy, faceWidth, faceHeight, 0, 0, faceWidth, faceHeight);

            canvasCtx.drawImage(tempCanvas, 0, 0, width, height);

            canvasCtx.scale(width / faceWidth, height / faceHeight);
            canvasCtx.translate(-sx, -sy);

            if (typeof drawConnectors !== 'undefined') {
                drawConnectors(canvasCtx, landmarks, FACEMESH_TESSELATION, { color: '#00FFAA', lineWidth: 1 });
                drawConnectors(canvasCtx, landmarks, FACEMESH_RIGHT_EYE, { color: '#FF3030' });
                drawConnectors(canvasCtx, landmarks, FACEMESH_LEFT_EYE, { color: '#30FF30' });
                drawConnectors(canvasCtx, landmarks, FACEMESH_FACE_OVAL, { color: '#FFFF00' });
                drawConnectors(canvasCtx, landmarks, FACEMESH_LIPS, { color: '#FF00FF' });
            }

            canvasCtx.setTransform(1, 0, 0, 1, 0, 0);
        } else {
            canvasCtx.drawImage(results.image, 0, 0, width, height);
        }

        canvasCtx.restore();
    });

    const camera = new Camera(videoElement, {
        onFrame: async () => {
            await faceMesh.send({ image: videoElement });
        },
        width: 1280,
        height: 720
    });

    showFaceRecBtn.addEventListener('click', () => {
        if (!cameraStarted) {
            camera.start();
            cameraStarted = true;

            videoElement.addEventListener('loadedmetadata', () => {
                canvasElement.width = videoElement.videoWidth;
                canvasElement.height = videoElement.videoHeight;
            });
        }

        faceRecognitionSection.style.display = 'flex';
        showFaceRecBtn.style.display = 'none';
    });

    captureBtn.addEventListener('click', async () => {
        try {
            captureBtn.disabled = true;

            const dataUrl = tempCanvas.toDataURL('image/png');
            const blob = dataURLtoBlob(dataUrl);

            const formData = new FormData();
            formData.append('rostro', blob, 'rostro.png');
            formData.append('_csrf_token', getCsrfToken());

            const response = await fetch('/login_rostro', {
                method: 'POST',
                body: formData,
                credentials: 'same-origin'
            });

            window.location.href = response.url || '/login';
        } catch (err) {
            console.error('Error al enviar imagen:', err);

            if (typeof Notify !== 'undefined') {
                Notify.error('Error al intentar el reconocimiento facial.');
            } else {
                alert('Error al intentar el reconocimiento facial.');
            }

            captureBtn.disabled = false;
        }
    });
})();