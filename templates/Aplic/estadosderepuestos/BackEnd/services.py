"""
COMPATIBILIDAD: Este archivo mantiene las importaciones para otras aplicaciones.
La lógica real ahora está en: core/image.py

Las funciones se re-exportan desde core para no romper imports existentes.
"""
# Re-exportar TODO desde core.image para compatibilidad
from core.image import (  # noqa: F401
    procesar_imagen,
    allowed_file,
    calcular_hash_archivo,
    calcular_hash_bytes,
    DEFAULT_UPLOAD_FOLDER,
    DEFAULT_ALLOWED_EXTENSIONS,
)

# Alias legacy: algunas partes del código usaban UPLOAD_FOLDER y ALLOWED_EXTENSIONS
UPLOAD_FOLDER = DEFAULT_UPLOAD_FOLDER
ALLOWED_EXTENSIONS = DEFAULT_ALLOWED_EXTENSIONS