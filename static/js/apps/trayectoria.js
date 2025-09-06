// trayectoria.js

function verEcuacion(){
    fetch("/trayectoria/model_param")
    .then(r => r.json())
    .then(d => {
        const cont = document.getElementById("ecuacion");
        if(d.error){
            cont.innerHTML = "<b style='color:red'>"+d.error+"</b>";
        } else {
            // Mostramos en LaTeX
            cont.innerHTML = `\\[ ${d.equation} \\]`;
            MathJax.typesetPromise([cont]); // Renderiza
        }
    });
}

function predecir(){
    let formData = new FormData();
    formData.append("coords", document.getElementById("coords").value);
    fetch("/trayectoria/predict", { method: "POST", body: formData })
    .then(r=>r.json())
    .then(d=>{
        if(d.error){ document.getElementById("resultado").innerHTML="<b style='color:red'>"+d.error+"</b>"; }
        else{
            let t_msg = d.t!==null ? " (t="+d.t.toFixed(2)+")":""; 
            document.getElementById("resultado").innerHTML="Coords=["+d.coords+"] → f ≈ "+d.y_pred.toFixed(3)+t_msg;
        }
    });
}

function graficar(){
    fetch("/trayectoria/plot")
    .then(r=>r.json())
    .then(d=>{
        if(d.error){ document.getElementById("grafico").innerHTML="<b style='color:red'>"+d.error+"</b>"; return; }
        let data_plot=[];
        if(d.dim==1){
            data_plot.push({x:d.px, y:d.py, mode:'markers', name:'Puntos'});
            data_plot.push({x:d.x, y:d.y, mode:'lines', name:'Curva'});
        } else if(d.dim==2){
            data_plot.push({x:d.px, y:d.py, z:d.pz, mode:'markers', type:'scatter3d', name:'Puntos'});
            data_plot.push({x:d.x[0], y:d.y.map(r=>r[0]), z:d.z, type:'surface', opacity:0.5, name:'Superficie'});
            if(d.linea) data_plot.push({x:d.linea.x, y:d.linea.y, z:d.linea.z, mode:'lines', type:'scatter3d', line:{color:'red', width:4}, name:'Linea paramétrica'});
        } else if(d.dim==3){
            data_plot.push({x:d.px, y:d.py, z:d.pz, mode:'markers', marker:{size:5, color:d.pf, colorscale:'Viridis'}, type:'scatter3d', name:'Puntos'});
            d.slices.forEach(s=>{ data_plot.push({x:s.x[0], y:s.y.map(r=>r[0]), z:s.f, type:'surface', opacity:0.5, name:'z='+s.z0}); });
            if(d.linea) data_plot.push({x:d.linea.x, y:d.linea.y, z:d.linea.z, mode:'lines', type:'scatter3d', line:{color:'red', width:5}, name:'Linea paramétrica'});
        }
        Plotly.newPlot('grafico', data_plot);
    });
}

function verModelo(){
    fetch("/trayectoria/model")
    .then(r=>r.json())
    .then(d=>{
        if(d.error){ document.getElementById("modelo_eq").innerHTML="<b style='color:red'>"+d.error+"</b>"; }
        else{ document.getElementById("modelo_eq").innerHTML="<b>Ecuación del modelo RBF:</b> "+d.equation; }
    });
}
