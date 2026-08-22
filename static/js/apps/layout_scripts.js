/* ================================================================
   layout_scripts.js — Comportamiento global del layout
   - Submenús anidados (desktop y mobile)
   - Loader global
   - Auto-cierre de menú mobile al navegar
   ================================================================ */

/* ================================================================
   1. SUBMENÚS ANIDADOS — modo desktop vs mobile
   ================================================================ */
function setupSubmenus() {
    const isMobile = () => window.innerWidth < 992;

    // Prevenir comportamiento por defecto de Bootstrap en submenús mobile
    document.querySelectorAll('.dropdown-submenu .dropdown-toggle').forEach(toggle => {
        toggle.addEventListener('click', function (e) {
            if (isMobile()) {
                e.preventDefault();
                e.stopPropagation();

                const parentLi = this.closest('.dropdown-submenu');
                const subMenu = parentLi.querySelector('.dropdown-menu');

                // Cerrar otros submenús hermanos
                const siblings = parentLi.parentElement.querySelectorAll(':scope > .dropdown-submenu');
                siblings.forEach(sib => {
                    if (sib !== parentLi) {
                        sib.classList.remove('show');
                        const sibMenu = sib.querySelector('.dropdown-menu');
                        if (sibMenu) sibMenu.classList.remove('show');
                    }
                });

                // Toggle del submenú actual
                parentLi.classList.toggle('show');
                if (subMenu) subMenu.classList.toggle('show');
            }
        });
    });
}

/* ================================================================
   2. CERRAR MENÚ MOBILE AL HACER CLICK EN UN ENLACE
   ================================================================ */
function setupMobileAutoClose() {
    const navbarCollapse = document.getElementById('navbar');
    if (!navbarCollapse) return;

    navbarCollapse.querySelectorAll('a.dropdown-item:not(.dropdown-toggle)').forEach(link => {
        link.addEventListener('click', function () {
            if (window.innerWidth < 992 && navbarCollapse.classList.contains('show')) {
                const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                if (bsCollapse) bsCollapse.hide();
            }
        });
    });
}

/* ================================================================
   3. REINICIAR SUBMENÚS AL CERRAR EL NAVBAR MOBILE
   ================================================================ */
function setupNavbarReset() {
    const navbarCollapse = document.getElementById('navbar');
    if (!navbarCollapse) return;

    navbarCollapse.addEventListener('hidden.bs.collapse', function () {
        // Cerrar todos los dropdowns y submenús al cerrar el navbar
        navbarCollapse.querySelectorAll('.show').forEach(el => {
            el.classList.remove('show');
        });
    });
}

/* ================================================================
   4. LOADER GLOBAL (para navegación y formularios)
   ================================================================ */
function mostrarLoader() {
    const loader = document.getElementById("loader");
    if (loader) loader.style.display = "flex";
}

function ocultarLoader() {
    const loader = document.getElementById("loader");
    if (loader) loader.style.display = "none";
}

function setupLoader() {
    // Mostrar loader en clicks de enlaces internos
    document.querySelectorAll("a[href]").forEach(link => {
        link.addEventListener("click", function (e) {
            const href = link.getAttribute("href");
            if (href &&
                !href.startsWith("http") &&
                !href.startsWith("#") &&
                !href.startsWith("javascript") &&
                !link.target &&
                !link.hasAttribute('data-no-loader')) {
                mostrarLoader();
            }
        });
    });

    // Mostrar loader en submit de formularios
    document.querySelectorAll("form:not(.no-loader)").forEach(form => {
        form.addEventListener("submit", function () {
            mostrarLoader();
        });
    });

    // Ocultar al cargar la página
    window.addEventListener("load", ocultarLoader);
    window.addEventListener("pageshow", ocultarLoader);
}

/* ================================================================
   5. SELECT2 — INICIALIZACIÓN GLOBAL
   ================================================================ */
function setupSelect2() {
    if (typeof $.fn.select2 !== 'undefined') {
        $('select.select2').select2({
            theme: 'default',
            width: '100%',
            dropdownAutoWidth: false
        });
    }
}

/* ================================================================
   6. INICIALIZACIÓN GENERAL AL CARGAR EL DOM
   ================================================================ */
document.addEventListener('DOMContentLoaded', function () {
    setupSubmenus();
    setupMobileAutoClose();
    setupNavbarReset();
    setupLoader();
    setupSelect2();

    // Reconfigurar submenús si cambia el tamaño de la ventana
    let resizeTimer;
    window.addEventListener('resize', function () {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () {
            setupSubmenus();
        }, 250);
    });
});