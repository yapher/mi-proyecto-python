/**
 * face_mesh_tracker.js
 * Módulo reutilizable para inicializar y manejar MediaPipe FaceMesh.
 * Usa Logger global.
 */
class FaceMeshTracker {
    constructor(config = {}) {
        this.config = Object.assign({
            videoId: 'inputVideo',
            canvasId: 'outputCanvas',
            fpsCounterId: 'fpsCounter',
            onResults: null,
            drawFullMesh: true,
            drawFaceOval: true,
            drawEyes: true,
            drawLips: true
        }, config);

        this.videoElement = document.getElementById(this.config.videoId);
        this.canvasElement = document.getElementById(this.config.canvasId);
        this.canvasCtx = this.canvasElement.getContext('2d');
        this.tempCanvas = document.createElement('canvas');
        this.tempCtx = this.tempCanvas.getContext('2d');
        this.lastTime = performance.now();
        this.camera = null;
        this.faceMesh = null;
    }

    async init() {
        if (typeof FaceMesh === 'undefined') {
            Logger.error('MediaPipe FaceMesh no está cargado');
            return;
        }

        this.faceMesh = new FaceMesh({
            locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`
        });

        this.faceMesh.setOptions({
            maxNumFaces: 1, refineLandmarks: true,
            minDetectionConfidence: 0.5, minTrackingConfidence: 0.5
        });

        this.faceMesh.onResults((results) => this._onResults(results));

        this.camera = new Camera(this.videoElement, {
            onFrame: async () => { await this.faceMesh.send({ image: this.videoElement }); },
            width: 1280, height: 720
        });

        this.videoElement.addEventListener('loadedmetadata', () => {
            this.canvasElement.width = this.videoElement.videoWidth;
            this.canvasElement.height = this.videoElement.videoHeight;
        });

        await this.camera.start();
        Logger.success('FaceMeshTracker inicializado correctamente');
    }

    _onResults(results) {
        const now = performance.now();
        const fps = Math.round(1000 / (now - this.lastTime));
        this.lastTime = now;

        if (this.config.fpsCounterId) {
            const fpsEl = document.getElementById(this.config.fpsCounterId);
            if (fpsEl) fpsEl.textContent = `FPS: ${fps}`;
        }

        const width = this.canvasElement.width;
        const height = this.canvasElement.height;

        this.canvasCtx.save();
        this.canvasCtx.clearRect(0, 0, width, height);

        if (results.multiFaceLandmarks && results.multiFaceLandmarks.length > 0) {
            const landmarks = results.multiFaceLandmarks[0];
            const xs = landmarks.map(p => p.x * this.videoElement.videoWidth);
            const ys = landmarks.map(p => p.y * this.videoElement.videoHeight);

            const minX = Math.min(...xs), maxX = Math.max(...xs);
            const minY = Math.min(...ys), maxY = Math.max(...ys);
            const padding = 40;
            const sx = Math.max(minX - padding, 0);
            const sy = Math.max(minY - padding, 0);
            const faceWidth = Math.min(this.videoElement.videoWidth - sx, maxX - minX + padding * 2);
            const faceHeight = Math.min(this.videoElement.videoHeight - sy, maxY - minY + padding * 2);

            this.tempCanvas.width = faceWidth;
            this.tempCanvas.height = faceHeight;
            this.tempCtx.drawImage(results.image, sx, sy, faceWidth, faceHeight, 0, 0, faceWidth, faceHeight);
            this.canvasCtx.drawImage(this.tempCanvas, 0, 0, width, height);
            this.canvasCtx.scale(width / faceWidth, height / faceHeight);
            this.canvasCtx.translate(-sx, -sy);

            if (this.config.drawFullMesh) drawConnectors(this.canvasCtx, landmarks, FACEMESH_TESSELATION, { color: '#00FFAA', lineWidth: 1 });
            if (this.config.drawEyes) {
                drawConnectors(this.canvasCtx, landmarks, FACEMESH_RIGHT_EYE, { color: '#FF3030' });
                drawConnectors(this.canvasCtx, landmarks, FACEMESH_LEFT_EYE, { color: '#30FF30' });
            }
            if (this.config.drawFaceOval) drawConnectors(this.canvasCtx, landmarks, FACEMESH_FACE_OVAL, { color: '#FFFF00' });
            if (this.config.drawLips) drawConnectors(this.canvasCtx, landmarks, FACEMESH_LIPS, { color: '#FF00FF' });

            this.canvasCtx.setTransform(1, 0, 0, 1, 0, 0);

            if (this.config.onResults) {
                this.config.onResults(results, landmarks, { sx, sy, faceWidth, faceHeight, width, height });
            }
        } else {
            this.canvasCtx.drawImage(results.image, 0, 0, width, height);
            if (this.config.onResults) this.config.onResults(results, null, null);
        }
        this.canvasCtx.restore();
    }

    getLatestFaceImage() {
        return this.tempCanvas.toDataURL('image/png');
    }
}

window.FaceMeshTracker = FaceMeshTracker;