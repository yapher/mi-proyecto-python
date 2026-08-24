/**
* listarepuestos.js
* Toggle entre vista cards y lista, con persistencia en localStorage
*/
document.addEventListener('DOMContentLoaded', function () {
    const toggleBtns = document.querySelectorAll('.lr-view-btn');
    const container = document.getElementById('repuestosContainer');
    
    if (!toggleBtns.length || !container) return;
    
    const setView = (view) => {
        toggleBtns.forEach(b => b.classList.toggle('active', b.dataset.view === view));
        container.classList.toggle('lr-grid--list', view === 'list');
        try { localStorage.setItem('lr-view', view); } catch (e) {}
    };
    
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', () => setView(btn.dataset.view));
    });
    
    // Restaurar preferencia
    try {
        const saved = localStorage.getItem('lr-view');
        if (saved === 'list') setView('list');
    } catch (e) {}
});