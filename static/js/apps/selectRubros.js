let arbolMenus = [];

function cargarArbolMenus(cb) {
    console.log('Iniciando carga de rubros desde /api/rubro_arbol...');
    fetch('/api/rubro_arbol', {
        credentials: 'include'
    })
    .then(res => {
        console.log('Respuesta del servidor:', res.status);
        if (res.status === 401) {
            console.error('Usuario no autenticado.');
            alert('Por favor, inicia sesión para cargar los rubros.');
            return;
        }
        return res.json();
    })
    .then(data => {
        console.log('Datos cargados desde /api/rubro_arbol:', data);
        if (!data || data.length === 0) {
            console.warn('La API devolvió una lista vacía de rubros.');
            arbolMenus = [];
            if (cb) cb();
            return;
        }
        arbolMenus = data;
        console.log('Estructura de datos procesada:', arbolMenus);
        if (cb) cb();
    })
    .catch(err => {
        console.error('Error al cargar rubros:', err);
        alert('Hubo un error al cargar los rubros. Verifica la consola para más detalles.');
    });
}

function buscarNodoPorRuta(data, ruta) {
    if (!ruta) return data;
    const partes = ruta.split('.');
    let nodo = data;
    for (const parte of partes) {
        if (Array.isArray(nodo)) {
            nodo = nodo.find(item => item.nombre === parte);
        } else if (nodo.submenues) {
            nodo = nodo.submenues.find(item => item.nombre === parte);
        } else {
            return null;
        }
        if (!nodo) return null;
    }
    return nodo;
}

function crearSelect(opciones, nivel, valorSeleccionado = "") {
    const select = document.createElement('select');
    select.className = 'form-control nivel-select mb-2';
    select.setAttribute('data-nivel', nivel);
    select.innerHTML = `<option value="">Sin seleccionar</option>`;
    opciones.forEach(item => {
        const seleccionado = item.ruta_jerarquia === valorSeleccionado ? 'selected' : '';
        select.innerHTML += `<option value="${item.ruta_jerarquia}" ${seleccionado}>${item.emoji} ${item.nombre}</option>`;
    });
    select.onchange = function () {
        let next = this.nextElementSibling;
        while (next) {
            next.remove();
            next = this.nextElementSibling;
        }
        if (this.value) {
            const seleccionado = buscarNodoPorRuta(arbolMenus, this.value);
            if (seleccionado && seleccionado.submenues && seleccionado.submenues.length > 0) {
                const nuevoSelect = crearSelect(seleccionado.submenues, nivel + 1);
                document.getElementById('nivelesContainer').appendChild(nuevoSelect);
            }
        }
    };
    return select;
}

function renderSelectoresNiveles(valorPorDefecto = "") {
    console.log('Renderizando selectores con valor por defecto:', valorPorDefecto);
    const cont = document.getElementById('nivelesContainer');
    if (!cont) {
        console.error('El contenedor nivelesContainer no está presente en el DOM.');
        return;
    }
    cont.innerHTML = '';
    if (!valorPorDefecto) {
        const select = crearSelect(arbolMenus, 0);
        cont.appendChild(select);
        return;
    }
    
    const partes = valorPorDefecto.split('.');
    let actual = arbolMenus;
    let rutaAcumulada = "";
    partes.forEach((parte, nivel) => {
        const rutaActual = rutaAcumulada + (nivel > 0 ? '.' : '') + parte;
        const select = crearSelect(actual, nivel, rutaActual);
        cont.appendChild(select);
        const nodo = actual.find(item => item.nombre === parte);
        if (nodo && nodo.submenues) {
            actual = nodo.submenues;
        } else {
            actual = [];
        }
        rutaAcumulada = rutaActual;
    });
}

// ✅ NO ejecutar cargarTodo aquí, se hace desde crear_rubros.js