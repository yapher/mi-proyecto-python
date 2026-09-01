/**
 * Selectores multinivel reutilizables
 * Carga un árbol jerárquico y renderiza selects encadenados
 * Usa Logger reutilizable
 */
var arbolMenus = [];

function cargarArbolMenus(callback) {
    Logger.info('Cargando árbol de rubros desde API');
    
    fetch('/api/rubro_arbol', { credentials: 'include' })
        .then(function (res) {
            Logger.apiResponse('GET', '/api/rubro_arbol', res.status);
            return res.json();
        })
        .then(function (data) {
            arbolMenus = data || [];
            Logger.success('Árbol de rubros cargado', { totalNodos: arbolMenus.length });
            if (callback) callback();
        })
        .catch(function (err) {
            Logger.error('Error al cargar árbol de rubros', { error: err.message });
            arbolMenus = [];
            if (callback) callback();
        });
}

function buscarNodoPorRuta(data, ruta) {
    if (!ruta) return data;
    var partes = ruta.split('.');
    var nodo = data;
    for (var i = 0; i < partes.length; i++) {
        if (Array.isArray(nodo)) {
            nodo = nodo.find(function (item) { return item.nombre === partes[i]; });
        } else if (nodo && nodo.submenues) {
            nodo = nodo.submenues.find(function (item) { return item.nombre === partes[i]; });
        } else {
            return null;
        }
        if (!nodo) return null;
    }
    return nodo;
}

function crearSelect(opciones, nivel, valorSeleccionado) {
    valorSeleccionado = valorSeleccionado || '';
    var select = document.createElement('select');
    select.className = 'form-control nivel-select mb-2';
    select.setAttribute('data-nivel', nivel);
    
    var html = '<option value="">Sin seleccionar</option>';
    (opciones || []).forEach(function (item) {
        var sel = item.ruta_jerarquia === valorSeleccionado ? ' selected' : '';
        html += '<option value="' + item.ruta_jerarquia + '"' + sel + '>' +
                item.emoji + ' ' + item.nombre + '</option>';
    });
    select.innerHTML = html;
    
    select.addEventListener('change', function () {
        Logger.info('Cambio en selector de nivel', { nivel, valor: this.value });
        
        // Eliminar selects siguientes
        var next = this.nextElementSibling;
        while (next) {
            var tmp = next.nextElementSibling;
            next.remove();
            next = tmp;
        }
        
        // Crear siguiente nivel si hay hijos
        if (this.value) {
            var nodo = buscarNodoPorRuta(arbolMenus, this.value);
            if (nodo && nodo.submenues && nodo.submenues.length > 0) {
                Logger.info('Creando selector de nivel superior', { nivel: nivel + 1 });
                var nuevo = crearSelect(nodo.submenues, nivel + 1);
                document.getElementById('nivelesContainer').appendChild(nuevo);
            }
        }
    });
    
    return select;
}

function renderSelectoresNiveles(valorPorDefecto) {
    valorPorDefecto = valorPorDefecto || '';
    Logger.info('Renderizando selectores de niveles', { valorPorDefecto });
    
    var cont = document.getElementById('nivelesContainer');
    if (!cont) {
        Logger.error('Contenedor nivelesContainer no encontrado en el DOM');
        return;
    }
    
    cont.innerHTML = '';
    
    if (!valorPorDefecto) {
        Logger.info('Renderizando selector raíz');
        cont.appendChild(crearSelect(arbolMenus, 0));
        return;
    }
    
    var partes = valorPorDefecto.split('.');
    var actual = arbolMenus;
    var rutaAcum = '';
    
    partes.forEach(function (parte, nivel) {
        rutaAcum += (nivel > 0 ? '.' : '') + parte;
        cont.appendChild(crearSelect(actual, nivel, rutaAcum));
        var nodo = actual.find(function (item) { return item.nombre === parte; });
        actual = (nodo && nodo.submenues) ? nodo.submenues : [];
    });
    
    Logger.success('Selectores renderizados correctamente', { niveles: partes.length });
}

function obtenerRutaPadre() {
    var selects = document.querySelectorAll('#nivelesContainer .nivel-select');
    var ruta = '';
    selects.forEach(function (sel) {
        if (sel.value) ruta = sel.value;
    });
    Logger.info('Ruta padre obtenida', { ruta });
    return ruta;
}