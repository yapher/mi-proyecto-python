from flask import Flask, render_template, jsonify, request, redirect, url_for, abort
import os, json, re, threading, webbrowser
from flask_login import login_required, current_user
from templates.Aplic.GestionAplic.BackEnd.backMenu import menu_api
from datetime import datetime
from menu import cargar_menu, guardar_menu
from login import init_routes_login, roles_required

from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from functools import partial


# Importa tus funciones del manager
from templates.Aplic.agenda.BackEnd.db_manager import (
    cargar_eventos, agregar_evento, editar_evento,
    eliminar_evento,enviar_recordatorios
)

from templates.Aplic.crearubicaciontecnica.BackEnd.crear_ubicacion_tecnica import ubicacion_bp
from templates.Aplic.estadosderepuestos.BackEnd.estados_de_repuestos import estadoRep_bp
from templates.Aplic.crearlistadoderepuestoporlinea.BackEnd.crear_listado_de_repuesto_por_linea import crear_listado_bp
from templates.Aplic.crearprocedimiento.BackEnd.crearprocedimiento import procedim_bp
from templates.Aplic.gestiondebloqueos.BackEnd.gestion_de_bloqueos import gestion_de_bloqueos_bp
from templates.Aplic.gestiondeherramientas.BackEnd.gestion_de_herramientas import gestion_de_herramientas_bp
from templates.Aplic.cargarprocedimiento.BackEnd.cargar_procedimiento import cargar_procedimiento_bp
from templates.Aplic.crearalmacenes.BackEnd.crear_almacenes import crear_almacenes_bp
from templates.Aplic.inventario.BackEnd.inventario import inventario_bp
from templates.Aplic.listarepuestos.BackEnd.lista_repuestos import lista_repuestos_bp
from templates.Aplic.graficosrepuestos.BackEnd.graficos_repuestos import graficos_repuestos_bp
from templates.Aplic.spotify.BackEnd.spotify import spotify_bp
from templates.Aplic.pagos.BackEnd.pagos import pagos_bp
from templates.Aplic.crearrubros.BackEnd.crear_rubros import crear_rubros_bp
from templates.Aplic.estadisticas.BackEnd.estadisticas import estadisticas_bp
from templates.Aplic.tareas.BackEnd.tareas import tareas_bp
from templates.Aplic.generarprocedimiento.BackEnd.generar_procedimiento import generar_procedimiento_bp
from templates.Aplic.agenda.BackEnd.agenda import agenda_bp
from templates.Aplic.detectorderostros.BackEnd.detector_de_rostros import detector_de_rostros_bp
from templates.Aplic.listarot.BackEnd.listar_ot import listar_ot_bp
from templates.Aplic.bajadadeot.BackEnd.bajada_de_ot import bajada_de_ot_bp
from templates.Aplic.instalaciones.BackEnd.instalaciones import instalaciones_bp
from templates.Aplic.trayectoria.BackEnd.trayectoria import trayectoria_bp


app = Flask(__name__)
app.secret_key = '221d18b67f2d4705a132d532b1d12ab2'  # Cambia esto por una clave segura
init_routes_login(app)
# Registro blueprint
app.register_blueprint(menu_api)
app.register_blueprint(crear_listado_bp)
app.register_blueprint(estadoRep_bp)
app.register_blueprint(procedim_bp)
app.register_blueprint(gestion_de_bloqueos_bp)
app.register_blueprint(gestion_de_herramientas_bp)
app.register_blueprint(cargar_procedimiento_bp)
app.register_blueprint(crear_almacenes_bp)
app.register_blueprint(inventario_bp)
app.register_blueprint(lista_repuestos_bp)
app.register_blueprint(ubicacion_bp)
app.register_blueprint(graficos_repuestos_bp)
app.register_blueprint(spotify_bp)
app.register_blueprint(pagos_bp)
app.register_blueprint(crear_rubros_bp)
app.register_blueprint(estadisticas_bp)
app.register_blueprint(tareas_bp)
app.register_blueprint(generar_procedimiento_bp)
app.register_blueprint(detector_de_rostros_bp)
app.register_blueprint(listar_ot_bp)
app.register_blueprint(bajada_de_ot_bp)
app.register_blueprint(instalaciones_bp)
app.register_blueprint(trayectoria_bp)



# ========= Config de correo =========
# --- Si usas GMAIL con clave de aplicación ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'oherasimovich730@alumnos.iua.edu.ar'
app.config['MAIL_PASSWORD'] = 'cvoe jyvn psqp tgjl'
app.config['MAIL_DEFAULT_SENDER'] = 'oherasimovich730@alumnos.iua.edu.ar'

mail = Mail(app)
app.register_blueprint(agenda_bp)
# Scheduler (solo en app principal)
scheduler = BackgroundScheduler(timezone="America/Argentina/Buenos_Aires")
job_func = partial(enviar_recordatorios, app=app, mail=mail, cargar_eventos_func=cargar_eventos)
scheduler.add_job(job_func, 'cron', hour=12, minute=30)


@app.context_processor
def inject_menu():
    menu = cargar_menu()
    # Podés ajustar los roles según el usuario logueado
    roles = ['admin', 'editor', 'viewer']
    return dict(menu=menu, roles=roles)

# Rutas protegidas con roles y paso de roles a la plantilla
@app.route('/')
@login_required
def index():
    menu = cargar_menu()
    return render_template('index.html', menu=menu, roles=current_user.roles)

@app.route('/gestion_menu')
@login_required
@roles_required('admin', 'editor')
def gestion_menu():
    menu = cargar_menu()
    return render_template('Aplic/GestionAplic/FrontEnd/gestion_menu.html', menu=menu, roles=current_user.roles)

@app.route('/gestion_aplicaciones')
@login_required
@roles_required('admin', 'editor')
def gestion_aplicaciones():
    menu = cargar_menu()
    return render_template('Aplic/GestionAplic/FrontEnd/gestion_aplicaciones.html', menu=menu, roles=current_user.roles)

# Manejo errores
@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

# Abrir navegador automáticamente
def abrir_navegador():
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == '__main__':
    scheduler.start()
    threading.Timer(1.0, abrir_navegador).start()
    os.makedirs('DataBase/Config', exist_ok=True)
    #app.run(debug=False)
    port = int(os.environ.get("PORT", 5000))  # Render asigna el puerto en la variable de entorno PORT
    app.run(host="0.0.0.0", port=port, debug=False)
