#!/usr/bin/env python3
"""
exportar_proyecto.py

Genera un archivo "Proyecto_Completo.txt" que contiene:
  1. La estructura completa de directorios y archivos del proyecto.
  2. El contenido completo de cada archivo de código encontrado.

Uso:
    python exportar_proyecto.py
    python exportar_proyecto.py --raiz "C:/ruta/a/mi/proyecto"
    python exportar_proyecto.py --salida "MiExport.txt"
    python exportar_proyecto.py --extensiones .py .txt .json .md
"""

import os
import argparse
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuración por defecto
# ---------------------------------------------------------------------------

# Carpetas que se ignoran siempre (entornos virtuales, control de versiones, etc.)
CARPETAS_EXCLUIDAS = {
    "__pycache__", ".git", ".svn", ".hg", ".idea", ".vscode",
    "venv", "env", ".venv", ".env", "node_modules",
    "build", "dist", "*.egg-info", ".mypy_cache", ".pytest_cache",
    ".tox", "site-packages",
}

# Extensiones de archivo que se incluyen por defecto (código y texto plano)
EXTENSIONES_POR_DEFECTO = {
    ".py", ".txt", ".md", ".yaml", ".yml",
    ".cfg", ".ini", ".toml", ".html", ".css", ".js",
}

# Extensiones que NUNCA se exportan, aunque el usuario las pida explícitamente
# con --extensiones o --archivos (ej: bases de datos, archivos de config con
# datos sensibles, etc.)
EXTENSIONES_EXCLUIDAS_SIEMPRE = {".json"}

# Archivos concretos que se excluyen aunque coincidan con la extensión
ARCHIVOS_EXCLUIDOS = {"Proyecto_Completo.txt", "exportar_proyecto.py"}

# Codificaciones a probar, en orden, al leer un archivo de texto.
# utf-8-sig maneja BOM de UTF-8; utf-16 cubre archivos generados en Windows/PowerShell.
CODIFICACIONES = ["utf-8-sig", "utf-8", "utf-16", "cp1252", "latin-1"]


def generar_arbol(raiz, extensiones):
    """Genera una representación en texto tipo 'árbol' de la estructura del proyecto."""
    lineas = []
    raiz = os.path.abspath(raiz)
    nombre_raiz = os.path.basename(raiz.rstrip(os.sep)) or raiz
    lineas.append(f"{nombre_raiz}/")

    def recorrer(carpeta, prefijo=""):
        try:
            entradas = sorted(os.listdir(carpeta))
        except PermissionError:
            return

        # Filtrar carpetas excluidas y archivos ocultos
        entradas_validas = []
        for entrada in entradas:
            ruta_completa = os.path.join(carpeta, entrada)
            if os.path.isdir(ruta_completa):
                if entrada in CARPETAS_EXCLUIDAS or entrada.startswith("."):
                    continue
                entradas_validas.append((entrada, True))
            else:
                if entrada in ARCHIVOS_EXCLUIDOS:
                    continue
                _, ext = os.path.splitext(entrada)
                ext = ext.lower()
                if ext in EXTENSIONES_EXCLUIDAS_SIEMPRE:
                    continue
                if extensiones and ext not in extensiones:
                    continue
                entradas_validas.append((entrada, False))

        for i, (entrada, es_dir) in enumerate(entradas_validas):
            es_ultimo = i == len(entradas_validas) - 1
            conector = "└── " if es_ultimo else "├── "
            ruta_completa = os.path.join(carpeta, entrada)

            if es_dir:
                lineas.append(f"{prefijo}{conector}{entrada}/")
                extension_prefijo = "    " if es_ultimo else "│   "
                recorrer(ruta_completa, prefijo + extension_prefijo)
            else:
                lineas.append(f"{prefijo}{conector}{entrada}")

    recorrer(raiz)
    return "\n".join(lineas)


def recolectar_archivos(raiz, extensiones):
    """Recorre el proyecto y devuelve la lista de rutas de archivos a exportar."""
    archivos_encontrados = []
    for carpeta_actual, subcarpetas, archivos in os.walk(raiz):
        # Modificar subcarpetas in-place para que os.walk no entre en ellas
        subcarpetas[:] = [
            d for d in subcarpetas
            if d not in CARPETAS_EXCLUIDAS and not d.startswith(".")
        ]

        for archivo in sorted(archivos):
            if archivo in ARCHIVOS_EXCLUIDOS:
                continue
            _, ext = os.path.splitext(archivo)
            ext = ext.lower()
            if ext in EXTENSIONES_EXCLUIDAS_SIEMPRE:
                continue
            if extensiones and ext not in extensiones:
                continue
            ruta_completa = os.path.join(carpeta_actual, archivo)
            archivos_encontrados.append(ruta_completa)

    return archivos_encontrados


def leer_contenido(ruta_archivo):
    """
    Lee el contenido de un archivo de texto probando varias codificaciones.
    Nunca lanza una excepción: en el peor de los casos devuelve el contenido
    decodificado reemplazando los caracteres inválidos, junto con un aviso.
    """
    ultimo_error = None

    for codificacion in CODIFICACIONES:
        try:
            with open(ruta_archivo, "r", encoding=codificacion) as f:
                contenido = f.read()
            # Si el archivo era binario o venía en una codificación de 16 bits
            # mal detectada, pueden colarse bytes nulos que rompen la copia
            # del .txt final. Los quitamos.
            if "\x00" in contenido:
                contenido = contenido.replace("\x00", "")
            return contenido
        except (UnicodeDecodeError, LookupError) as e:
            ultimo_error = e
            continue
        except (PermissionError, OSError) as e:
            # Error de acceso al archivo: no tiene sentido probar otras
            # codificaciones, directamente lo reportamos.
            return f"[No se pudo leer el archivo (error de acceso): {e}]"

    # Si ninguna codificación funcionó "limpiamente", como último recurso
    # leemos en binario y reemplazamos los bytes problemáticos, para no
    # perder el archivo completo de la exportación.
    try:
        with open(ruta_archivo, "rb") as f:
            datos = f.read()
        contenido = datos.decode("utf-8", errors="replace").replace("\x00", "")
        return (
            f"[Aviso: no se detectó la codificación exacta del archivo "
            f"(último error: {ultimo_error}). Se muestra con caracteres "
            f"inválidos reemplazados por '�']\n\n{contenido}"
        )
    except Exception as e:
        return f"[No se pudo leer el archivo: {e}]"


def exportar_proyecto(raiz, salida, extensiones, archivos_especificos=None):
    raiz = os.path.abspath(raiz)
    extensiones = {e.lower() if e.startswith(".") else f".{e.lower()}" for e in extensiones}

    # Aunque el usuario pida .json explícitamente por --extensiones, la
    # sacamos igual: es una exclusión dura para no exportar bases de datos.
    if extensiones & EXTENSIONES_EXCLUIDAS_SIEMPRE:
        print(
            "⚠️  Se ignoran estas extensiones porque están excluidas siempre "
            f"(ej. bases de datos): {sorted(extensiones & EXTENSIONES_EXCLUIDAS_SIEMPRE)}"
        )
        extensiones -= EXTENSIONES_EXCLUIDAS_SIEMPRE

    print(f"Analizando proyecto en: {raiz}")
    arbol = generar_arbol(raiz, extensiones)

    if archivos_especificos:
        # Modo selectivo: se ignoran los filtros de extensión/exclusión y se
        # exporta exactamente la lista de rutas relativas que pidió el usuario,
        # salvo que sean .json (exclusión dura, igual se respeta).
        archivos = []
        faltantes = []
        omitidos_json = []
        for ruta_relativa in archivos_especificos:
            # Normalizamos separadores: aceptamos tanto "/" como "\" sin
            # importar el sistema operativo desde el que se escribió la ruta.
            ruta_normalizada = ruta_relativa.replace("\\", os.sep).replace("/", os.sep)
            _, ext = os.path.splitext(ruta_normalizada)
            if ext.lower() in EXTENSIONES_EXCLUIDAS_SIEMPRE:
                omitidos_json.append(ruta_relativa)
                continue
            ruta_absoluta = os.path.join(raiz, ruta_normalizada)
            if os.path.isfile(ruta_absoluta):
                archivos.append(ruta_absoluta)
            else:
                faltantes.append(ruta_relativa)
        if omitidos_json:
            print("⚠️  Se omiten estos archivos .json (excluidos siempre):")
            for f in omitidos_json:
                print(f"    - {f}")
        if faltantes:
            print("⚠️  No se encontraron estos archivos (revisá la ruta o el --raiz):")
            for f in faltantes:
                print(f"    - {f}")
    else:
        archivos = recolectar_archivos(raiz, extensiones)

    print(f"Se encontraron {len(archivos)} archivo(s) para exportar.")

    with open(salida, "w", encoding="utf-8") as f_salida:
        # Encabezado
        f_salida.write("=" * 80 + "\n")
        f_salida.write("EXPORTACIÓN COMPLETA DEL PROYECTO\n")
        f_salida.write(f"Ruta del proyecto: {raiz}\n")
        f_salida.write(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f_salida.write("=" * 80 + "\n\n")

        # Estructura de directorios
        f_salida.write("ESTRUCTURA DEL PROYECTO\n")
        f_salida.write("-" * 80 + "\n")
        f_salida.write(arbol + "\n\n")

        # Contenido de cada archivo
        f_salida.write("=" * 80 + "\n")
        f_salida.write("CONTENIDO DE LOS ARCHIVOS\n")
        f_salida.write("=" * 80 + "\n\n")

        for ruta_archivo in archivos:
            ruta_relativa = os.path.relpath(ruta_archivo, raiz)

            f_salida.write("-" * 80 + "\n")
            f_salida.write(f"ARCHIVO: {ruta_relativa}\n")
            f_salida.write("-" * 80 + "\n")

            # Si un archivo puntual falla por cualquier motivo no controlado,
            # no queremos que se corte toda la exportación: lo anotamos y
            # seguimos con el resto.
            try:
                contenido = leer_contenido(ruta_archivo)
            except Exception as e:
                contenido = f"[ERROR inesperado al procesar este archivo: {e}]"

            f_salida.write(contenido)
            if not contenido.endswith("\n"):
                f_salida.write("\n")
            f_salida.write("\n")

    print(f"✅ Exportación completada: {os.path.abspath(salida)}")


def main():
    parser = argparse.ArgumentParser(
        description="Exporta la estructura y el código completo de un proyecto Python a un único .txt"
    )
    parser.add_argument(
        "--raiz", "-r",
        default=".",
        help="Ruta raíz del proyecto a exportar (por defecto: directorio actual)."
    )
    parser.add_argument(
        "--salida", "-o",
        default="Proyecto_Completo.txt",
        help="Nombre del archivo de salida (por defecto: Proyecto_Completo.txt)."
    )
    parser.add_argument(
        "--extensiones", "-e",
        nargs="*",
        default=sorted(EXTENSIONES_POR_DEFECTO),
        help="Lista de extensiones a incluir, ej: .py .txt .md (por defecto incluye varias comunes; .json queda excluido siempre)."
    )
    parser.add_argument(
        "--archivos", "-a",
        nargs="*",
        default=None,
        help=(
            "Lista exacta de rutas relativas a exportar (ignora --extensiones y las "
            "exclusiones por carpeta/tipo, salvo .json que siempre se excluye). "
            "Ej: --archivos templates/layout.html static/js/apps/agenda.js"
        )
    )

    args = parser.parse_args()
    exportar_proyecto(args.raiz, args.salida, args.extensiones, args.archivos)


if __name__ == "__main__":
    main()