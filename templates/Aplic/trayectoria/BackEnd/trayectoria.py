from flask_login import login_required, current_user
from menu import cargar_menu
from login import roles_required
from flask import Blueprint, jsonify, request, render_template
import numpy as np
from templates.Aplic.trayectoria.BackEnd.rbf_model import RBFRegressor

trayectoria_bp = Blueprint('indextrayectoria', __name__)

modelo_rbf = None
X_train, y_train = None, None

@trayectoria_bp.route('/trayectoria', methods=['GET', 'POST'])
@login_required
@roles_required('viewer')
def indextrayectoria():
    global modelo_rbf, X_train, y_train
    nemu = cargar_menu()

    if request.method == 'POST':
        puntos_raw = request.form.get("points")
        if not puntos_raw:
            return render_template("Aplic/trayectoria/FrontEnd/trayectoria.html",
                                   nemu=nemu,
                                   roles=current_user.roles,
                                   error="Debes ingresar puntos.")

        data = []
        for p in puntos_raw.split(";"):
            try:
                vals = [float(v) for v in p.strip().split(",")]
                data.append(vals)
            except:
                pass
        data = np.array(data)

        if data.shape[1] < 2:
            return render_template("Aplic/trayectoria/FrontEnd/trayectoria.html",
                                   nemu=nemu,
                                   roles=current_user.roles,
                                   error="Cada punto debe tener al menos X,Y.")

        # Si no hay columna f, generamos f lineal 0→1
        if data.shape[1] == 2 or data.shape[1] == 3:
            f_col = np.linspace(0, 1, len(data)).reshape(-1,1)
            data = np.hstack([data, f_col])

        X_train, y_train = data[:, :-1], data[:, -1]

        if len(X_train) == 2:
            modelo_rbf = "lineal"
        else:
            from scipy.spatial.distance import pdist
            dists = pdist(X_train)
            eps = np.mean(dists) if len(dists) > 0 else 1.0
            modelo_rbf = RBFRegressor(eps=eps, kind="gaussian", lam=0.0)
            modelo_rbf.fit(X_train, y_train)

        return render_template("Aplic/trayectoria/FrontEnd/trayectoria.html",
                               nemu=nemu,
                               roles=current_user.roles,
                               entrenado=True)
    return render_template("Aplic/trayectoria/FrontEnd/trayectoria.html",
                           nemu=nemu,
                           roles=current_user.roles)


@trayectoria_bp.route('/trayectoria/predict', methods=['POST'])
@login_required
@roles_required('viewer')
def predecir_trayectoria():
    global modelo_rbf, X_train, y_train
    if modelo_rbf is None:
        return jsonify({"error": "Primero entrena el modelo."}), 400
    try:
        coords = [float(v) for v in request.form.get("coords").split(",")]
        Xnew = np.array([coords])
    except:
        return jsonify({"error": "Entrada inválida."}), 400

    t_val = None
    if modelo_rbf == "lineal":
        v0, v1 = X_train[0], X_train[1]
        f0, f1 = y_train[0], y_train[1]
        dist_total = np.linalg.norm(v1 - v0)
        dist_new = np.linalg.norm(Xnew - v0)
        t_val = dist_new / dist_total if dist_total > 0 else 0.0
        t_val = float(np.clip(t_val, 0.0, 1.0))
        y_pred = f0 + t_val*(f1-f0)
    else:
        # Interpolación para cualquier dimensión
        # Calculamos la proyección de Xnew sobre la línea poligonal
        diffs = X_train[1:] - X_train[:-1]
        seg_lengths = np.linalg.norm(diffs, axis=1)
        cum_lengths = np.concatenate([[0], np.cumsum(seg_lengths)])
        total_length = cum_lengths[-1]

        # proyectamos Xnew sobre cada segmento y buscamos el más cercano
        t_val = 0.0
        for i, (p0, p1) in enumerate(zip(X_train[:-1], X_train[1:])):
            seg = p1 - p0
            if np.all(seg == 0):
                continue
            t_seg = np.dot((Xnew - p0), seg) / np.dot(seg, seg)
            t_seg_clipped = np.clip(t_seg, 0.0, 1.0)
            proj = p0 + t_seg_clipped*seg
            dist = np.linalg.norm(Xnew - proj)
            if i == 0 or dist < min_dist:
                min_dist = dist
                t_val = (cum_lengths[i] + t_seg_clipped*seg_lengths[i])/total_length
        y_pred = modelo_rbf.predict(Xnew)[0]

    return jsonify({"coords": coords, "y_pred": float(y_pred), "t": float(t_val)})


@trayectoria_bp.route('/trayectoria/plot', methods=['GET'])
@login_required
@roles_required('viewer')
def plot_trayectoria():
    global modelo_rbf, X_train, y_train
    if modelo_rbf is None:
        return jsonify({"error": "Primero entrena el modelo."}), 400

    dim = X_train.shape[1]

    # Línea que une los puntos
    linea3d = None
    if len(X_train) >= 2:
        linea3d = {"x": X_train[:,0].tolist(),
                   "y": X_train[:,1].tolist(),
                   "z": X_train[:,2].tolist() if dim==3 else y_train.tolist()}

    if dim==1:
        x_grid = np.linspace(X_train.min(), X_train.max(), 100).reshape(-1,1)
        y_grid = modelo_rbf.predict(x_grid) if modelo_rbf!="lineal" else np.interp(x_grid.ravel(), X_train.ravel(), y_train)
        return jsonify({"dim":1,"x":x_grid.ravel().tolist(),"y":y_grid.ravel().tolist(),"px":X_train.ravel().tolist(),"py":y_train.ravel().tolist()})
    elif dim==2:
        x_lin = np.linspace(X_train[:,0].min(), X_train[:,0].max(), 30)
        y_lin = np.linspace(X_train[:,1].min(), X_train[:,1].max(), 30)
        Xg, Yg = np.meshgrid(x_lin, y_lin)
        grid = np.c_[Xg.ravel(), Yg.ravel()]
        Zg = modelo_rbf.predict(grid).reshape(Xg.shape) if modelo_rbf!="lineal" else np.interp(Xg.ravel(), X_train[:,0], y_train).reshape(Xg.shape)
        return jsonify({"dim":2,"x":Xg.tolist(),"y":Yg.tolist(),"z":Zg.tolist(),"px":X_train[:,0].tolist(),"py":X_train[:,1].tolist(),"pz":y_train.tolist(),"linea":linea3d})
    elif dim==3:
        x_lin = np.linspace(X_train[:,0].min(), X_train[:,0].max(), 20)
        y_lin = np.linspace(X_train[:,1].min(), X_train[:,1].max(), 20)
        z_lin = np.linspace(X_train[:,2].min(), X_train[:,2].max(), 3)
        slices=[]
        for z0 in z_lin:
            Xg, Yg = np.meshgrid(x_lin, y_lin)
            grid = np.c_[Xg.ravel(), Yg.ravel(), np.full(Xg.size, z0)]
            Fg = modelo_rbf.predict(grid).reshape(Xg.shape) if modelo_rbf!="lineal" else np.interp(Xg.ravel(), X_train[:,0], y_train).reshape(Xg.shape)
            slices.append({"z0":float(z0),"x":Xg.tolist(),"y":Yg.tolist(),"f":Fg.tolist()})
        return jsonify({"dim":3,"px":X_train[:,0].tolist(),"py":X_train[:,1].tolist(),"pz":X_train[:,2].tolist(),"pf":y_train.tolist(),"slices":slices,"linea":linea3d})
    else:
        return jsonify({"error":"Dimensión no soportada."}),400
@trayectoria_bp.route('/trayectoria/model', methods=['GET'])
@login_required
@roles_required('viewer')
def get_model_equation():
    global modelo_rbf, X_train, y_train
    if modelo_rbf is None or modelo_rbf == "lineal":
        return jsonify({"error": "Primero entrena el modelo no lineal RBF."}), 400
    eq = modelo_rbf.get_model_equation()
    return jsonify({"equation": eq})
@trayectoria_bp.route('/trayectoria/model', methods=['GET'])
@login_required
@roles_required('viewer')
def modelo_trayectoria():
    global modelo_rbf, X_train, y_train
    if modelo_rbf is None:
        return jsonify({"error": "Primero entrena el modelo."}), 400

    # Para el caso lineal simple de dos puntos
    if modelo_rbf == "lineal" and len(X_train) == 2:
        p0, p1 = X_train[0], X_train[1]
        f0, f1 = y_train[0], y_train[1]
        eq = f"f(t) = {f0} + t*({f1}-{f0}), t ∈ [0,1]; X(t) = {p0.tolist()} + t*({p1.tolist()} - {p0.tolist()})"
    else:
        # Para RBF, devolvemos forma general en t basado en interpolación de la línea poligonal
        pts_str = "[" + ", ".join([str(p.tolist()) for p in X_train]) + "]"
        f_str = "[" + ", ".join([str(f) for f in y_train]) + "]"
        eq = (
            "f(t) ≈ RBF( X(t) ); "
            "X(t) = punto a lo largo de la trayectoria definida por los puntos "
            f"{pts_str} con valores f = {f_str} "
            "proyectando t ∈ [0,1] a lo largo de la distancia acumulada entre puntos."
        )

    return jsonify({"equation": eq})

@trayectoria_bp.route('/trayectoria/model_param', methods=['GET'])
@login_required
@roles_required('viewer')
def modelo_trayectoria_param():
    """
    Devuelve la ecuación paramétrica en notación LaTeX para poder mostrarla en pantalla
    """
    global modelo_rbf, X_train, y_train
    if modelo_rbf is None:
        return jsonify({"error": "Primero entrena el modelo."}), 400

    N = len(X_train)
    dim = X_train.shape[1]

    # Caso lineal simple (dos puntos)
    if modelo_rbf == "lineal" and N == 2:
        p0, p1 = X_train[0], X_train[1]
        f0, f1 = y_train[0], y_train[1]
        eq = (
            f"x(t) = {p0[0]} + ({p1[0]-p0[0]})t, \\\\ "
            f"y(t) = {p0[1]} + ({p1[1]-p0[1]})t"
        )
        if dim == 3:
            eq += f", \\\\ z(t) = {p0[2]} + ({p1[2]-p0[2]})t"
        eq += f", \\\\ f(t) = {f0} + ({f1-f0})t, \\\\ t \\in [0,1]"
        return jsonify({"equation": eq})

    # Caso general (más puntos + RBF)
    pts = X_train.tolist()
    fs = y_train.tolist()
    eq = (
        "X(t) = trayectoria definida por interpolación de los puntos: \\\\ "
        f"{pts}, \\\\ con valores f = {fs}, \\\\ "
        "donde t \\in [0,1] recorre la distancia acumulada."
    )
    return jsonify({"equation": eq})

