/**
 * JavaScript para el componente Spotify
 * Maneja la funcionalidad de control de reproducción de Spotify
 */

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    const playBtn = document.getElementById('btnPlay');
    const pauseBtn = document.getElementById('btnPause');
    const nextBtn = document.getElementById('btnNext');

    // Event listener para el botón de play
    playBtn?.addEventListener('click', async () => {
        const res = await fetch('/spotify/play', {method: 'POST'});
        if (res.ok) alert('Reproducción iniciada');
        else alert('Error al iniciar reproducción');
    });

    // Event listener para el botón de pause
    pauseBtn?.addEventListener('click', async () => {
        const res = await fetch('/spotify/pause', {method: 'POST'});
        if (res.ok) alert('Reproducción pausada');
        else alert('Error al pausar reproducción');
    });

    // Event listener para el botón de siguiente
    nextBtn?.addEventListener('click', async () => {
        const res = await fetch('/spotify/next', {method: 'POST'});
        if (res.ok) alert('Siguiente canción');
        else alert('Error al pasar a la siguiente canción');
    });
});
