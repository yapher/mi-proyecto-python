const canvas = new fabric.Canvas('canvas');
let conexiones = [];
let estadoActual = 'ON';

canvas.on('object:moving', () => actualizarLineas());
canvas.on('object:modified', () => actualizarLineas());

function agregarComponente() {
    
 const tipo = document.getElementById("componentes").value;
 
    const rutas = {
        motor: ['MOTOR.jpg'],
        pulsador: ['pulsador_verde.jpg'],
        lampara: ['LAMPARA_7W.jpg']
    };

    const intentos = rutas[tipo];
    if (!intentos) {
        console.warn(`Tipo no soportado: ${tipoRaw}`);
        return alert("Tipo no soportado. Usa: 'motor', 'pulsador' o 'lampara'.");
    }

    const cargarImagen = (index = 0) => {
        if (index >= intentos.length) {
            console.error(`No se pudo cargar ninguna imagen válida para ${tipo}`);
            return alert(`No se pudo cargar imagen para '${tipo}'`);
        }

        const url = `/static/uploads/Imagenes/${intentos[index]}`;
        console.log(`Intentando cargar: ${url}`);

        fabric.Image.fromURL(url, function (img) {
            const maxDim = 200;
            const scaleX = maxDim / img.width;
            const scaleY = maxDim / img.height;
            const scale = Math.min(scaleX, scaleY, 1);

            img.set({
                left: 100 + Math.random() * 400,
                top: 100 + Math.random() * 300,
                scaleX: scale,
                scaleY: scale,
                hasControls: true,
                hasBorders: true,
                cornerColor: 'blue'
            });

            img.customType = tipo;
            img.__uid = `id_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;

            canvas.add(img);
            canvas.renderAll();
        }, {
            crossOrigin: 'anonymous',
            onError: () => cargarImagen(index + 1)
        });
    };

    cargarImagen();
}


function conectarSeleccionados() {
    const objs = canvas.getActiveObjects();
    if (objs.length !== 2) return alert("Selecciona 2 objetos para conectar.");

    const [from, to] = objs;
    canvas.discardActiveObject();

    const fromCenter = from.getCenterPoint();
    const toCenter = to.getCenterPoint();

    const arrow = new fabric.Line([fromCenter.x, fromCenter.y, toCenter.x, toCenter.y], {
        stroke: 'black',
        strokeWidth: 2,
        selectable: false,
        evented: false
    });

    const head = new fabric.Triangle({
        left: toCenter.x,
        top: toCenter.y,
        originX: 'center',
        originY: 'center',
        angle: calcAngle(fromCenter, toCenter),
        width: 10,
        height: 12,
        fill: 'black',
        selectable: false,
        evented: false
    });

    arrow.customType = 'conexion';
    arrow.__from = from.__uid;
    arrow.__to = to.__uid;
    arrow.__estado = 'ON';

    canvas.add(arrow, head);
    canvas.sendToBack(arrow);
    canvas.sendToBack(head);

    conexiones.push({ from: from.__uid, to: to.__uid, estado: 'ON', arrowId: arrow.__uid });
    canvas.renderAll();
}

function actualizarLineas() {
    const mapa = {};
    canvas.getObjects().forEach(obj => {
        if (obj.__uid) mapa[obj.__uid] = obj;
    });

    canvas.getObjects().forEach(obj => {
        if (obj.customType === 'conexion') {
            const from = mapa[obj.__from];
            const to = mapa[obj.__to];
            if (from && to) {
                const fc = from.getCenterPoint();
                const tc = to.getCenterPoint();
                obj.set({ x1: fc.x, y1: fc.y, x2: tc.x, y2: tc.y });

                const next = canvas.getObjects().find(o =>
                    o.type === 'triangle' && o.left === obj.x2 && o.top === obj.y2
                );
                if (next) {
                    next.set({
                        left: tc.x,
                        top: tc.y,
                        angle: calcAngle(fc, tc)
                    });
                }
            }
        }
    });

    canvas.renderAll();
}

function eliminarConexiones() {
    canvas.getObjects().forEach(obj => {
        if (obj.customType === 'conexion' || obj.type === 'triangle') {
            canvas.remove(obj);
        }
    });
    conexiones = [];
    canvas.renderAll();
}

function cambiarEstado() {
    estadoActual = estadoActual === 'ON' ? 'OFF' : 'ON';

    canvas.getObjects().forEach(obj => {
        if (obj.customType === 'conexion') {
            obj.set('stroke', estadoActual === 'ON' ? 'green' : 'red');
        }
        if (obj.type === 'triangle') {
            obj.set('fill', estadoActual === 'ON' ? 'green' : 'red');
        }
    });
    canvas.renderAll();
}

function guardarCroquis() {
    const data = {
        canvas: canvas.toDatalessJSON(['__uid', 'customType', '__from', '__to', '__estado']),
        conexiones
    };
    fetch('/guardar_plano', {
        method: 'POST',
        body: JSON.stringify({ nombre: 'mi_croquis', data }),
        headers: { 'Content-Type': 'application/json' }
    }).then(() => alert("Croquis guardado"));
}

function cargarCroquis() {
    fetch('/cargar_plano?nombre=mi_croquis')
        .then(res => res.json())
        .then(data => {
            canvas.loadFromJSON(data.canvas, () => {
                conexiones = data.conexiones || [];

                const mapa = {};
                canvas.getObjects().forEach(obj => {
                    if (obj.__uid) mapa[obj.__uid] = obj;
                });

                conexiones.forEach(cnx => {
                    const from = mapa[cnx.from];
                    const to = mapa[cnx.to];
                    if (from && to) {
                        const fc = from.getCenterPoint();
                        const tc = to.getCenterPoint();

                        const line = new fabric.Line([fc.x, fc.y, tc.x, tc.y], {
                            stroke: cnx.estado === 'ON' ? 'green' : 'red',
                            strokeWidth: 2,
                            selectable: false
                        });

                        line.customType = 'conexion';
                        line.__from = cnx.from;
                        line.__to = cnx.to;
                        line.__estado = cnx.estado;

                        const arrow = new fabric.Triangle({
                            left: tc.x,
                            top: tc.y,
                            originX: 'center',
                            originY: 'center',
                            angle: calcAngle(fc, tc),
                            width: 10,
                            height: 12,
                            fill: cnx.estado === 'ON' ? 'green' : 'red',
                            selectable: false
                        });

                        canvas.add(line, arrow);
                        canvas.sendToBack(line);
                        canvas.sendToBack(arrow);
                    }
                });

                canvas.renderAll();
            });
        });
}

function calcAngle(p1, p2) {
    return Math.atan2(p2.y - p1.y, p2.x - p1.x) * 180 / Math.PI;
}

canvas.on('mouse:dblclick', function(opt) {
    const target = opt.target;
    if (target && target.customType) {
        const nuevoNombre = prompt("Nombre del componente:", target.nombre || "");
        if (nuevoNombre !== null) {
            target.nombre = nuevoNombre;
        }

        const nuevoEstado = prompt("Estado (ON/OFF):", target.estado || "OFF");
        if (nuevoEstado !== null && (nuevoEstado.toUpperCase() === "ON" || nuevoEstado.toUpperCase() === "OFF")) {
            target.estado = nuevoEstado.toUpperCase();
        }

        canvas.renderAll();
    }
});

function eliminarSeleccionado() {
    const seleccionados = canvas.getActiveObjects();
    if (seleccionados.length === 0) return alert("Selecciona un componente para eliminar.");

    seleccionados.forEach(obj => {
        // Si es una conexión directa (línea o flecha), eliminarla sola
        if (obj.customType === 'conexion' || obj.type === 'triangle') {
            canvas.remove(obj);
            return;
        }

        // Si es un componente: eliminar sus conexiones
        if (obj.__uid) {
            // Eliminar líneas asociadas
            canvas.getObjects().forEach(o => {
                if (o.customType === 'conexion' && (o.__from === obj.__uid || o.__to === obj.__uid)) {
                    canvas.remove(o);

                    // Eliminar su flecha asociada
                    const flecha = canvas.getObjects().find(t =>
                        t.type === 'triangle' &&
                        Math.abs(t.left - o.x2) < 2 &&
                        Math.abs(t.top - o.y2) < 2
                    );
                    if (flecha) canvas.remove(flecha);
                }
            });

            // También actualizar el array de conexiones
            conexiones = conexiones.filter(c => c.from !== obj.__uid && c.to !== obj.__uid);
        }

        canvas.remove(obj);
    });

    canvas.discardActiveObject();
    canvas.renderAll();
}

function exportarComoImagen() {
    const dataURL = canvas.toDataURL({
        format: 'png',
        quality: 1.0
    });

    const link = document.createElement('a');
    link.href = dataURL;
    link.download = 'croquis.png';
    link.click();
}
