// Manejo correcto de submenús anidados en Bootstrap 5 sin eliminar estilos
function setupSubmenus() {
    document.querySelectorAll('.dropdown-submenu > a').forEach(function (element) {
        element.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            const parentLi = this.parentElement;

            // Cierra otros submenús abiertos en el mismo nivel
            parentLi.parentElement.querySelectorAll('.dropdown-submenu.show').forEach(function (submenu) {
                if (submenu !== parentLi) {
                    submenu.classList.remove('show');
                }
            });

            // Alterna la visibilidad del submenú actual
            parentLi.classList.toggle('show');
        });
    });

    // Cierra submenús al cerrar dropdown principal
    document.querySelectorAll('.dropdown').forEach(function (dropdown) {
        dropdown.addEventListener('hide.bs.dropdown', function () {
            this.querySelectorAll('.dropdown-submenu').forEach(function (submenu) {
                submenu.classList.remove('show');
            });
        });
    });
}

document.addEventListener('DOMContentLoaded', setupSubmenus);

// Filtro de menú por búsqueda
function setupMenuSearch() {
    const menuSearch = document.getElementById("menuSearch");
    if (!menuSearch) return;
    menuSearch.addEventListener("keyup", function () {
        const filtro = this.value.toLowerCase();
        document.querySelectorAll(".navbar-nav > .nav-item").forEach(item => {
            let match = false;
            const textoItem = item.querySelector(".nav-link")?.innerText.toLowerCase() || "";
            item.querySelectorAll(".dropdown-item").forEach(sub => {
                const textoSub = sub.innerText.toLowerCase();
                const coincide = textoSub.includes(filtro);
                sub.parentElement.style.display = coincide ? "" : "none";
                if (coincide) match = true;
            });
            item.style.display = textoItem.includes(filtro) || match ? "" : "none";
        });
    });
}
document.addEventListener('DOMContentLoaded', setupMenuSearch);

// Mostrar y ocultar loader
function mostrarLoader() {
    const loader = document.getElementById("loader");
    if (loader) loader.style.display = "flex";
}
function ocultarLoader() {
    const loader = document.getElementById("loader");
    if (loader) loader.style.display = "none";
}
function setupLoader() {
    document.querySelectorAll("a[href]").forEach(link => {
        link.addEventListener("click", function (e) {
            const href = link.getAttribute("href");
            if (
                href &&
                !href.startsWith("http") &&
                !href.startsWith("#") &&
                !href.startsWith("javascript") &&
                !link.target
            ) {
                mostrarLoader();
            }
        });
    });
    document.querySelectorAll("form:not(.no-loader)").forEach(form => {
        form.addEventListener("submit", () => {
            mostrarLoader();
        });
    });
    document.querySelectorAll('.form-eliminar').forEach(form => {
        form.addEventListener('submit', e => {
            e.preventDefault();
            Swal.fire({
                title: '¿Estás seguro?',
                text: "¡Esta acción no se puede deshacer!",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar',
                customClass: {
                    popup: 'swal-custom-popup',
                    title: 'swal-custom-title',
                    confirmButton: 'btn btn-eliminar',
                    cancelButton: 'btn btn-outline-light'
                }
            }).then((result) => {
                if (result.isConfirmed) {
                    mostrarLoader();
                    form.submit();
                }
            });
        });
    });
}
document.addEventListener('DOMContentLoaded', setupLoader);
