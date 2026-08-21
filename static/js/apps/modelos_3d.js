// static/js/apps/modelos_3d.js - Versión completa con Bootstrap Modal integrado (sin romper funcionalidades)

const container = document.getElementById('container');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x222222);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
camera.position.set(0, 50, 40);

const renderer = new THREE.WebGLRenderer({antialias: true});
renderer.setSize(window.innerWidth, window.innerHeight);
container.appendChild(renderer.domElement);

// Mover la referencia del domElement acá para que esté disponible desde el principio
const rendererDomElement = renderer.domElement;

const controls = new THREE.OrbitControls(camera, renderer.domElement);

scene.add(new THREE.AmbientLight(0xffffff, 1));
const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444444, 1);
hemiLight.position.set(0, 20, 0);
scene.add(hemiLight);

const loader = new THREE.GLTFLoader();
let currentModel = null;
let sensores = [];
let modeloActual = null;
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let sensorSeleccionado = null;
let arrastrando = false;

// Crear sensor con etiqueta flotante 3D - TAMAÑO MÁS GRANDE
function crearSensor(x, y, z, nombre="Sensor", color=0xff0000, forma="sphere", size=2.0){
    let geometry;
    if(forma==="sphere") geometry = new THREE.SphereGeometry(size, 16, 16);
    else if(forma==="cube") geometry = new THREE.BoxGeometry(size, size, size);
    else if(forma==="cone") geometry = new THREE.ConeGeometry(size, size*1.5, 16);

    const material = new THREE.MeshBasicMaterial({
        color: color, 
        transparent: true, 
        opacity: 0.8,
        side: THREE.DoubleSide // Asegurar que sea visible desde todos los ángulos
    });
    const sensor = new THREE.Mesh(geometry, material);
    sensor.position.set(x, y, z);
    sensor.userData = {nombre, color, forma, size, isSensor: true}; // Marcar como sensor

    const label = document.createElement("div");
    label.className = "sensorLabel";
    label.innerText = nombre;
    label.style.background = "green";
    label.style.color = "black";
    document.body.appendChild(label);

    sensor.userData.label = label;
    sensores.push(sensor);
    
    console.log("✅ Sensor creado:", nombre, "Posición:", {x, y, z}, "Total sensores:", sensores.length);
    
    return sensor;
}

// Guardar sensores
async function guardarSensores(){
    if(!modeloActual) return;
    const datos = sensores.map(s=>({
        nombre: s.userData.nombre,
        color: s.userData.color,
        forma: s.userData.forma,
        size: s.userData.size,
        pos: {x: s.position.x, y: s.position.y, z: s.position.z}
    }));
    await fetch(`/modelos_3d/guardar_sensores/${modeloActual}`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(datos)
    });
}

// Cargar sensores guardados
async function cargarSensoresGuardados(){
    if(!modeloActual) return;
    const res = await fetch(`/modelos_3d/cargar_sensores/${modeloActual}`);
    const datos = await res.json();
    datos.forEach(d=>{
        const sensor = crearSensor(d.pos.x, d.pos.y, d.pos.z, d.nombre, d.color, d.forma, d.size);
        currentModel.add(sensor);
    });
}

// Cargar modelo
function cargarModelo(ruta, archivo, escala=0.2){
    const loaderDiv = document.getElementById('loader');
    const loaderText = document.getElementById('loaderText');
    const progressBar = document.getElementById('progressBar');
    loaderDiv.style.display = 'block';
    progressBar.style.width = '0%';
    loaderText.innerText = 'Cargando modelo 3D... 0%';

    loader.load(ruta,
        function(gltf){
            if(currentModel){ 
                scene.remove(currentModel); 
                sensores.forEach(s=>document.body.removeChild(s.userData.label)); 
                sensores=[]; 
            }
            const model = gltf.scene;
            model.scale.set(escala, escala, escala);
            const box = new THREE.Box3().setFromObject(model);
            const center = box.getCenter(new THREE.Vector3());
            model.position.sub(center);
            scene.add(model);
            currentModel = model;
            loaderDiv.style.display = 'none';
            modeloActual = archivo;
            cargarSensoresGuardados();
        },
        function(xhr){
            if(xhr.lengthComputable){
                const percent = Math.round((xhr.loaded/xhr.total)*100);
                loaderText.innerText = `Cargando modelo 3D... ${percent}%`;
                progressBar.style.width = `${percent}%`;
            }
        },
        function(error){ 
            console.error("Error cargando modelo:", ruta, error); 
            loaderText.innerText = 'Error cargando el modelo'; 
        }
    );
}

// Select modelo
const modeloSelectEl = document.getElementById("modeloSelect");
if(modeloSelectEl){
    modeloSelectEl.addEventListener("change", function(){
        const archivo = this.value;
        if(archivo){
            const ruta = `/modelos_3d/model/${archivo}`;
            cargarModelo(ruta, archivo, 0.2);
        }
    });
}

// Vistas
function vistaFrontal(){ camera.position.set(0, 10, 40); camera.lookAt(0, 0, 0); controls.update(); }
function vistaLateral(){ camera.position.set(40, 10, 0); camera.lookAt(0, 0, 0); controls.update(); }
function vistaSuperior(){ camera.position.set(0, 50, 20); camera.lookAt(0, 0, 0); controls.update(); }
function vistaDiagonal(){ camera.position.set(30, 30, 30); camera.lookAt(0, 0, 0); controls.update(); }

// Doble clic -> agregar sensor con detección mejorada
window.addEventListener('dblclick', (event)=>{
    if(!currentModel) return;
    
    // Obtener coordenadas relativas al canvas
    const rect = rendererDomElement.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    mouse.x = (x / rect.width) * 2 - 1;
    mouse.y = -(y / rect.height) * 2 + 1;
    
    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObject(currentModel, true);
    
    console.log("🖱️ Doble clic - Intersecciones:", intersects.length);
    
    if(intersects.length>0){
        const point = intersects[0].point;
        console.log("📍 Creando sensor en:", point);
        
        const sensor = crearSensor(0, 0, 0);
        currentModel.add(sensor);
        sensor.position.copy(currentModel.worldToLocal(point.clone()));
        guardarSensores();
    }
});

// -------------------------------
// Menú contextual con Bootstrap
// -------------------------------
const colorPicker = document.getElementById("colorPicker");
const sizeInput = document.getElementById("sizeInput");
const sensorMenuElement = document.getElementById("sensorMenu");
// crear instancia de modal (asegurarse de que bootstrap esté cargado en la página)
let sensorMenuModal = null;
if(sensorMenuElement && window.bootstrap && typeof window.bootstrap.Modal === 'function'){
    sensorMenuModal = new bootstrap.Modal(sensorMenuElement);
} else {
    // fallback: si no hay bootstrap, dejamos sensorMenuModal null y evitamos errores
    console.warn("Bootstrap Modal no disponible. El menú contextual no se mostrará como modal.");
}

window.addEventListener('contextmenu', (event)=>{
    event.preventDefault();
    event.stopPropagation();
    
    console.log("🖱️ Clic derecho detectado en:", event.clientX, event.clientY);
    console.log("📊 Sensores disponibles:", sensores.length);
    console.log("📦 Modelo actual:", currentModel ? "Sí" : "No");
    
    if(!currentModel || sensores.length === 0){
        console.log("⚠️ No hay modelo o sensores");
        if(sensorMenuModal) sensorMenuModal.hide();
        return;
    }
    
    // Obtener coordenadas relativas al canvas
    const rect = rendererDomElement.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    // Convertir a coordenadas normalizadas (-1 a +1)
    mouse.x = (x / rect.width) * 2 - 1;
    mouse.y = -(y / rect.height) * 2 + 1;
    
    console.log("🎯 Mouse normalizado:", mouse.x.toFixed(2), mouse.y.toFixed(2));
    
    raycaster.setFromCamera(mouse, camera);
    
    // Aumentar el umbral de detección del raycaster (si aplica)
    if(raycaster.params && raycaster.params.Points) raycaster.params.Points.threshold = 1;
    if(raycaster.params && raycaster.params.Line) raycaster.params.Line.threshold = 1;
    
    // Buscar primero solo en los sensores
    let sensorIntersects = raycaster.intersectObjects(sensores, false);
    console.log("🎯 Intersecciones directas con sensores:", sensorIntersects.length);
    
    // Si no encontró nada, buscar en toda la escena y filtrar
    if(sensorIntersects.length === 0){
        const allIntersects = raycaster.intersectObjects(scene.children, true);
        console.log("🔍 Total intersecciones en escena:", allIntersects.length);
        
        // Filtrar solo objetos que sean sensores
        sensorIntersects = allIntersects.filter(intersect => {
            const isSensor = sensores.includes(intersect.object);
            const hasFlag = intersect.object.userData && intersect.object.userData.isSensor;
            console.log("  Objeto:", intersect.object.type, "Es sensor?", isSensor || hasFlag);
            return isSensor || hasFlag;
        });
        
        console.log("🎯 Sensores filtrados:", sensorIntersects.length);
    }
    
    if(sensorIntersects.length > 0){
        sensorSeleccionado = sensorIntersects[0].object;
        console.log("✅ Sensor seleccionado:", sensorSeleccionado.userData.nombre);
        console.log("📍 Posición del sensor:", sensorSeleccionado.position);
        
        // Prellenar controles del modal si existen
        if(colorPicker && sensorSeleccionado.userData.color !== undefined){
            colorPicker.value = "#" + sensorSeleccionado.userData.color.toString(16).padStart(6, "0");
        }
        if(sizeInput && sensorSeleccionado.userData.size !== undefined){
            sizeInput.value = sensorSeleccionado.userData.size;
        }

        // Actualizar título del modal (si existe)
        if(sensorMenuElement){
            const titleEl = sensorMenuElement.querySelector('.modal-title');
            if(titleEl) titleEl.innerText = `Opciones del Sensor — ${sensorSeleccionado.userData.nombre}`;
        }

        // Mostrar modal Bootstrap (centrado)
        if(sensorMenuModal){
            sensorMenuModal.show();
        } else {
            // Fallback: si no hay bootstrap, tratamos de mostrar el elemento como antes
            sensorMenuElement.style.left = event.clientX + "px";
            sensorMenuElement.style.top = event.clientY + "px";
            sensorMenuElement.style.display = "block";
        }
        
        console.log("📋 Menú mostrado (modal) para:", sensorSeleccionado.userData.nombre);
    } else {
        console.log("❌ No se detectó ningún sensor");
        sensorSeleccionado = null;
        if(sensorMenuModal) sensorMenuModal.hide();
        else if(sensorMenuElement) sensorMenuElement.style.display = "none";
    }
});

// Cerrar modal/claro fallback al hacer clic fuera (solo si el modal está abierto)
window.addEventListener('click', (event)=>{
    if(sensorMenuElement){
        try {
            const modalOpen = sensorMenuElement.classList.contains('show');
            if(modalOpen && !event.target.closest('.modal-content')){
                if(sensorMenuModal) sensorMenuModal.hide();
            }
        } catch(e){
            // ignore
        }
    }
});

// Menú funciones
function renombrarSensor(){
    if(sensorSeleccionado){
        const nuevo = prompt("Nuevo nombre:", sensorSeleccionado.userData.nombre);
        if(nuevo){
            sensorSeleccionado.userData.nombre = nuevo;
            sensorSeleccionado.userData.label.innerText = nuevo;
            guardarSensores();
        }
    }
    if(sensorMenuModal) sensorMenuModal.hide();
    else if(sensorMenuElement) sensorMenuElement.style.display = "none";
}

function eliminarSensor(){
    if(sensorSeleccionado){
        currentModel.remove(sensorSeleccionado);
        try { document.body.removeChild(sensorSeleccionado.userData.label); } catch(e){}
        sensores = sensores.filter(s=>s!==sensorSeleccionado);
        guardarSensores();
    }
    if(sensorMenuModal) sensorMenuModal.hide();
    else if(sensorMenuElement) sensorMenuElement.style.display = "none";
}

function cambiarColorDesdePicker(){
    if(sensorSeleccionado && colorPicker){
        const color = parseInt(colorPicker.value.substring(1), 16);
        sensorSeleccionado.userData.color = color;
        sensorSeleccionado.material.color.setHex(color);
        guardarSensores();
    }
    // No cerramos el modal para permitir más cambios si se quiere
}

function cambiarForma(){
    if(sensorSeleccionado){
        const forma = prompt("Forma: sphere, cube, cone", sensorSeleccionado.userData.forma);
        if(forma && ["sphere", "cube", "cone"].includes(forma)){
            const pos = sensorSeleccionado.position.clone();
            const color = sensorSeleccionado.userData.color;
            const nombre = sensorSeleccionado.userData.nombre;
            const size = sensorSeleccionado.userData.size;
            currentModel.remove(sensorSeleccionado);
            try { document.body.removeChild(sensorSeleccionado.userData.label); } catch(e){}
            sensores = sensores.filter(s=>s!==sensorSeleccionado);
            const nuevo = crearSensor(pos.x, pos.y, pos.z, nombre, color, forma, size);
            currentModel.add(nuevo);
            guardarSensores();
        }
    }
    if(sensorMenuModal) sensorMenuModal.hide();
    else if(sensorMenuElement) sensorMenuElement.style.display = "none";
}

function cambiarTamañoSensor(){
    if(sensorSeleccionado && sizeInput){
        const size = parseFloat(sizeInput.value);
        if(isNaN(size)) return;
        sensorSeleccionado.userData.size = size;
        const forma = sensorSeleccionado.userData.forma;
        const pos = sensorSeleccionado.position.clone();
        const color = sensorSeleccionado.userData.color;
        const nombre = sensorSeleccionado.userData.nombre;
        currentModel.remove(sensorSeleccionado);
        try { document.body.removeChild(sensorSeleccionado.userData.label); } catch(e){}
        sensores = sensores.filter(s=>s!==sensorSeleccionado);
        const nuevo = crearSensor(pos.x, pos.y, pos.z, nombre, color, forma, size);
        currentModel.add(nuevo);
        guardarSensores();
    }
    // No cerramos necesariamente el modal al cambiar tamaño
}

// Arrastrar sensores
let isDragging = false;

window.addEventListener("mousedown", (event)=>{
    if(event.button === 0 && !arrastrando){
        // Detectar si se hizo clic en un sensor
        mouse.x = (event.clientX/window.innerWidth)*2-1;
        mouse.y = -(event.clientY/window.innerHeight)*2+1;
        raycaster.setFromCamera(mouse, camera);
        
        const allIntersects = raycaster.intersectObjects(scene.children, true);
        const sensorIntersects = allIntersects.filter(intersect => sensores.includes(intersect.object));
        
        if(sensorIntersects.length > 0){
            sensorSeleccionado = sensorIntersects[0].object;
            arrastrando = true;
            controls.enabled = false;
            console.log("🖱️ Arrastrando sensor:", sensorSeleccionado.userData.nombre);
        }
    }
});

window.addEventListener("mouseup", (event)=>{
    if(arrastrando){
        arrastrando = false;
        controls.enabled = true;
        guardarSensores();
        console.log("✅ Sensor soltado");
    }
});

window.addEventListener("mousemove", (event)=>{
    if(arrastrando && sensorSeleccionado && currentModel){
        mouse.x = (event.clientX/window.innerWidth)*2-1;
        mouse.y = -(event.clientY/window.innerHeight)*2+1;
        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObject(currentModel, true);
        if(intersects.length>0){
            const point = intersects[0].point;
            sensorSeleccionado.position.copy(currentModel.worldToLocal(point.clone()));
        }
    }
});

// Animación
function animate(){
    requestAnimationFrame(animate);

    const width = window.innerWidth;
    const height = window.innerHeight;

    sensores.forEach(sensor=>{
        // Hacer que el sensor parpadee suavemente
        const pulseSpeed = 0.003;
        const pulseMin = 0.6;
        const pulseMax = 1.0;
        sensor.material.opacity = (Math.sin(Date.now() * pulseSpeed) * 0.5 + 0.5) * (pulseMax - pulseMin) + pulseMin;

        // Obtener posición mundial del sensor
        const pos = new THREE.Vector3();
        sensor.getWorldPosition(pos);

        // Proyectar a coordenadas de pantalla
        pos.project(camera);
        const x = (pos.x * 0.5 + 0.5) * width;
        const y = (-pos.y * 0.5 + 0.5) * height;

        // Aplicar posición de etiqueta con offset mejorado
        const label = sensor.userData.label;
        
        // Verificar si el sensor está visible (delante de la cámara)
        if(pos.z > 1) {
            label.style.display = 'none';
        } else {
            label.style.display = 'block';
            label.style.left = `${x}px`;
            label.style.top = `${y - 30}px`; // Justo arriba del sensor
            label.style.position = 'fixed';
            label.style.transform = 'translate(-50%, 0)';
            label.style.background = 'rgba(0, 255, 0, 0.9)';
            label.style.color = 'black';
            label.style.fontSize = '13px';
            label.style.fontWeight = 'bold';
            label.style.padding = '4px 8px';
            label.style.borderRadius = '4px';
            label.style.pointerEvents = 'none';
            label.style.zIndex = '4000';
        }
    });

    controls.update();
    renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', ()=>{
    camera.aspect = window.innerWidth/window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});
