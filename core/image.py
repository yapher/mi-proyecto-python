"""
core/image.py
=============
Módulo reutilizable para procesamiento y subida de imágenes.
Unifica la lógica de:
  - estadosderepuestos/BackEnd/services.py (versión simple)
  - instalaciones/BackEnd/instalaciones.py (versión con hash MD5)

Características:
  ✅ Hash MD5 para evitar duplicados (mismo archivo = mismo nombre)
  ✅ Si existe archivo diferente con mismo nombre → agrega timestamp
  ✅ Configuración flexible de carpeta destino
  ✅ Validación de extensiones permitidas
  ✅ Manejo seguro de archivos (seek/rewind)

Uso:
    from core.image import procesar_imagen, allowed_file

    # Caso 1: carpeta por defecto (static/uploads/Imagenes)
    filename, error = procesar_imagen(request.files['imagen'])

    # Caso 2: carpeta específica de una app
    filename, error = procesar_imagen(
        request.files['imagen'],
        destino='templates/Aplic/instalaciones/static/img'
    )

    # Caso 3: sin hash (comportamiento legacy)
    filename, error = procesar_imagen(
        request.files['imagen'],
        usar_hash=False
    )
"""
import os
import time
import hashlib
from flask import current_app
from werkzeug.utils import secure_filename


# ============================================================
# CONSTANTES GLOBALES
# ============================================================
DEFAULT_UPLOAD_FOLDER = os.path.join('static', 'uploads', 'Imagenes')
DEFAULT_ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
DEFAULT_MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


# ============================================================
# VALIDACIÓN DE EXTENSIONES
# ============================================================
def allowed_file(filename, extensions=None):
    """
    Verifica si la extensión del archivo está permitida.

    Args:
        filename: Nombre del archivo
        extensions: Set de extensiones permitidas (default: PNG/JPG/GIF/WEBP)

    Returns:
        bool: True si la extensión es válida
    """
    if extensions is None:
        extensions = DEFAULT_ALLOWED_EXTENSIONS
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions


# ============================================================
# CÁLCULO DE HASH MD5
# ============================================================
def calcular_hash_archivo(ruta_archivo):
    """
    Calcula el hash MD5 de un archivo existente en disco.

    Args:
        ruta_archivo: Ruta absoluta al archivo

    Returns:
        str: Hash MD5 en hex, o None si hay error
    """
    hash_md5 = hashlib.md5()
    try:
        with open(ruta_archivo, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except (OSError, IOError):
        return None


def calcular_hash_bytes(data_bytes):
    """
    Calcula el hash MD5 de datos en memoria (bytes).

    Args:
        data_bytes: Bytes del archivo

    Returns:
        str: Hash MD5 en hex
    """
    return hashlib.md5(data_bytes).hexdigest()


# ============================================================
# PROCESAMIENTO DE IMAGEN (función principal)
# ============================================================
def procesar_imagen(archivo, destino=None, usar_hash=True):
    """
    Procesa y guarda una imagen con reutilización inteligente.

    Lógica:
      1. Si usar_hash=True y existe archivo con mismo hash → NO duplica (reutiliza)
      2. Si existe con hash diferente → agrega timestamp al nombre
      3. Si no existe → guarda normalmente

    Args:
        archivo: Archivo subido (request.files['campo'])
        destino: Ruta de carpeta destino (relativa a current_app.root_path).
                 Si es None, usa DEFAULT_UPLOAD_FOLDER.
        usar_hash: Si True, calcula hash MD5 para evitar duplicados.

    Returns:
        tuple: (nombre_archivo, error)
            - (filename, None) si fue exitoso
            - (None, None) si no hay archivo
            - (None, "mensaje de error") si falló
    """
    # Validación inicial
    if not archivo or archivo.filename == '':
        return None, None

    if not allowed_file(archivo.filename):
        return None, (
            f"Formato no permitido. Use: {', '.join(DEFAULT_ALLOWED_EXTENSIONS)}"
        )

    # Determinar carpeta destino
    if destino is None:
        destino = DEFAULT_UPLOAD_FOLDER

    # Construir ruta completa
    directorio = os.path.join(current_app.root_path, destino)
    os.makedirs(directorio, exist_ok=True)

    filename = secure_filename(archivo.filename)
    ruta_completa = os.path.join(directorio, filename)

    # Leer contenido del archivo (sin perder el stream)
    try:
        archivo.seek(0)
        contenido_nuevo = archivo.read()
        archivo.seek(0)
    except Exception as e:
        return None, f"Error al leer el archivo: {str(e)}"

    # Validar tamaño
    if len(contenido_nuevo) > DEFAULT_MAX_FILE_SIZE:
        mb = DEFAULT_MAX_FILE_SIZE / (1024 * 1024)
        return None, f"Archivo demasiado grande. Máximo {mb:.0f}MB"

    # Si usar_hash=True, aplicar lógica de reutilización
    if usar_hash and os.path.exists(ruta_completa):
        hash_existente = calcular_hash_archivo(ruta_completa)
        hash_nuevo = calcular_hash_bytes(contenido_nuevo)

        if hash_existente == hash_nuevo:
            # ✅ Mismo archivo: NO duplicar, reutilizar nombre
            return filename, None
        else:
            # ⚠️ Mismo nombre pero diferente contenido: agregar timestamp
            nombre, extension = os.path.splitext(filename)
            filename = f"{nombre}_{int(time.time())}{extension}"
            ruta_completa = os.path.join(directorio, filename)

    # Guardar archivo
    try:
        with open(ruta_completa, "wb") as f:
            f.write(contenido_nuevo)
        return filename, None
    except Exception as e:
        return None, f"Error al guardar imagen: {str(e)}"


# ============================================================
# UTILIDADES ADICIONALES
# ============================================================
def obtener_ruta_absoluta(destino=None):
    """
    Retorna la ruta absoluta de la carpeta de uploads.

    Args:
        destino: Ruta relativa (default: DEFAULT_UPLOAD_FOLDER)

    Returns:
        str: Ruta absoluta
    """
    if destino is None:
        destino = DEFAULT_UPLOAD_FOLDER
    return os.path.join(current_app.root_path, destino)


def url_para_imagen(filename, destino=None):
    """
    Genera la URL pública para una imagen guardada.

    Args:
        filename: Nombre del archivo
        destino: Ruta relativa (default: DEFAULT_UPLOAD_FOLDER)

    Returns:
        str: URL accesible desde el navegador
    """
    if destino is None or destino == DEFAULT_UPLOAD_FOLDER:
        return f"/static/uploads/Imagenes/{filename}"
    # Para carpetas específicas de apps, usar static de blueprint
    return f"/{destino}/{filename}"