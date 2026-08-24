"""
Lógica de negocio: validaciones y manejo de archivos.
"""
import os
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = os.path.join('static', 'uploads', 'Imagenes')

def allowed_file(filename):
    """Verifica si la extensión del archivo es permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def procesar_imagen(archivo):
    """Procesa y guarda una imagen. Retorna (filename, error)."""
    if not archivo or archivo.filename == '':
        return None, None
    if not allowed_file(archivo.filename):
        return None, "Formato de imagen no permitido."
    
    filename = secure_filename(archivo.filename)
    save_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    archivo.save(save_path)
    return filename, None