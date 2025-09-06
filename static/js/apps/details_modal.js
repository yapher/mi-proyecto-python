// details_modal.js

document.addEventListener('DOMContentLoaded', function () {
  var myModal = new bootstrap.Modal(document.getElementById('productModal'));

  document.body.addEventListener('click', function (e) {
    if (e.target.classList.contains('product-image')) {
      const img = e.target;
      document.getElementById('modalTitle').textContent = img.dataset.nombre || '';
      document.getElementById('modalImage').src = img.src;
      document.getElementById('modalImage').alt = img.alt;
      document.getElementById('modalCodigo').textContent = img.dataset.codigo || '';
      document.getElementById('modalCantidad').textContent = img.dataset.cantidad || '';
      document.getElementById('modalFecha').textContent = img.dataset.fecha || '';
      document.getElementById('modalEquipo').textContent = img.dataset.equipo || '';
      document.getElementById('modalUbicacion').textContent = img.dataset.ubicacion || '';
      document.getElementById('modalEmojy').textContent = img.dataset.emojy || '';

      const modalLinkSpan = document.getElementById('modalLink');
      const linkUrl = img.dataset.link || '';
      if (linkUrl) {
        modalLinkSpan.innerHTML = `<a href="${linkUrl}" target="_blank" class="text-info text-decoration-none">${linkUrl}</a>`;
      } else {
        modalLinkSpan.textContent = '';
      }

      const fechaFin = img.dataset.fechafin || '';
      const fechaFinLi = document.getElementById('modalFechaFinLi');
      const fechaFinSpan = document.getElementById('modalFechaFin');
      if (fechaFin) {
        fechaFinSpan.textContent = fechaFin;
        fechaFinLi.style.display = '';
      } else {
        fechaFinSpan.textContent = '';
        fechaFinLi.style.display = 'none';
      }

      myModal.show();
    }
  });
});
