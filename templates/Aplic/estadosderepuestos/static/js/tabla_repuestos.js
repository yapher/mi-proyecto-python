// tabla_repuestos.js

function filtrarTabla(input) {
  const tabPane = input.closest('.tab-pane');
  const filtro = input.value.toLowerCase();
  const filas = tabPane.querySelectorAll('tbody tr');

  filas.forEach(fila => {
    const texto = fila.textContent.toLowerCase();
    fila.style.display = texto.includes(filtro) ? '' : 'none';
  });
}

document.addEventListener('DOMContentLoaded', () => {
  // Filtrado por texto al tipear
  document.querySelectorAll('.buscar_input').forEach(input => {
    input.addEventListener('keyup', function () {
      filtrarTabla(this);
    });
  });

  // Filtrado por select de estado
  document.querySelectorAll('.select_estado').forEach(select => {
    select.addEventListener('change', function () {
      const tabPane = this.closest('.tab-pane');
      const buscarInput = tabPane.querySelector('.buscar_input');
      if (buscarInput) {
        buscarInput.value = this.value;
        filtrarTabla(buscarInput);
      }
    });
  });

  // Exportar PDF por pestaña
  document.querySelectorAll('.form-exportar-pdf').forEach(form => {
    form.addEventListener('submit', function () {
      const tabPane = this.closest('.tab-pane');
      const buscarInput = tabPane.querySelector('.buscar_input');
      const buscarPdf = this.querySelector('.buscar_pdf');
      if (buscarInput && buscarPdf) {
        buscarPdf.value = buscarInput.value || '';
      }
    });
  });
});
