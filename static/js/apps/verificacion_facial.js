const videoElement = document.getElementById('inputVideo');
const canvasElement = document.getElementById('outputCanvas');
const canvasCtx = canvasElement.getContext('2d');
let lastTime = performance.now();
let fps = 0;

const tempCanvas = document.createElement('canvas');
const tempCtx = tempCanvas.getContext('2d');

const faceMesh = new FaceMesh({
  locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`
});

faceMesh.setOptions({
  maxNumFaces: 1,
  refineLandmarks: true,
  minDetectionConfidence: 0.5,
  minTrackingConfidence: 0.5
});

let lastFace = null;

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

    tempCanvas.width = faceWidth;
    tempCanvas.height = faceHeight;
    tempCtx.drawImage(results.image, sx, sy, faceWidth, faceHeight, 0, 0, faceWidth, faceHeight);
    canvasCtx.drawImage(tempCanvas, 0, 0, width, height);

    canvasCtx.scale(width / faceWidth, height / faceHeight);
    canvasCtx.translate(-sx, -sy);

    drawConnectors(canvasCtx, landmarks, FACEMESH_TESSELATION, { color: '#00FFAA', lineWidth: 1 });
    drawConnectors(canvasCtx, landmarks, FACEMESH_FACE_OVAL, { color: '#FFFF00' });

    canvasCtx.setTransform(1, 0, 0, 1, 0, 0);

    lastFace = tempCanvas.toDataURL('image/png');

  } else {
    canvasCtx.drawImage(results.image, 0, 0, width, height);
    lastFace = null;
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

camera.start();

videoElement.addEventListener('loadedmetadata', () => {
  canvasElement.width = videoElement.videoWidth;
  canvasElement.height = videoElement.videoHeight;
});

document.getElementById('captureBtn').addEventListener('click', () => {
  const mensaje = document.getElementById("mensaje");
  if (!lastFace) {
    mensaje.innerText = "No se detectó rostro para enviar.";
    return;
  }

  mensaje.innerText = "Verificando rostro...";
  fetch('/api/verificar_rostro', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ imagen: lastFace })
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
