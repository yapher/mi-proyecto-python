#!/usr/bin/env python3
"""
exportar_proyecto.py

Genera un archivo "Proyecto_Completo.txt" que contiene:
  1. La estructura completa de directorios y archivos del proyecto.
  2. El contenido completo de cada archivo de código encontrado
     (los archivos de test se muestran en la estructura pero no se
     exporta su contenido, para que el archivo final sea más liviano).

Uso:
    python exportar_proyecto.py
    python exportar_proyecto.py --raiz "C:/ruta/a/mi/proyecto"
    python exportar_proyecto.py --salida "MiExport.txt"
    python exportar_proyecto.py --extensiones .py .txt .json .md
"""

import os
import fnmatch
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

# Extensiones que NUNCA se exportan (ni estructura ni contenido), aunque el
# usuario las pida explícitamente con --extensiones o --archivos
# (ej: bases de datos, archivos de config con datos sensibles, etc.)
EXTENSIONES_EXCLUIDAS_SIEMPRE = {".json"}

# Patrones de nombre de archivo que se consideran "tests". Estos archivos
# SÍ aparecen en la estructura del árbol, pero su contenido NO se exporta
# (para aligerar el .txt final).
PATRONES_TEST_EXCLUIDOS = [
    "test_*.py", "*_test.py", "tests.py", "conftest.py",
    "test_*.js", "*_test.js", "*.test.js",
]

# Carpetas cuyo contenido de archivos no se exporta (pero sí se listan en
# el árbol), por considerarse carpetas de tests.
CARPETAS_TEST = {"tests", "test", "__tests__"}

# Archivos concretos que se excluyen aunque coincidan con la extensión
ARCHIVOS_EXCLUIDOS = {"Proyecto_Completo.txt", "exportar_proyecto.py"}

# Codificaciones a probar, en orden, al leer un archivo de texto.
# utf-8-sig maneja BOM de UTF-8; utf-16 cubre archivos generados en Windows/PowerShell.
CODIFICACIONES = ["utf-8-sig", "utf-8", "utf-16", "cp1252", "latin-1"]


def es_archivo_test(nombre_archivo):
    """Devuelve True si el nombre del archivo coincide con algún patrón de test."""
    return any(fnmatch.fnmatch(nombre_archivo, patron) for patron in PATRONES_TEST_EXCLUIDOS)


def esta_en_carpeta_test(ruta_relativa):
    """Devuelve True si alguna carpeta del path relativo es una carpeta de tests."""
    partes = ruta_relativa.split(os.sep)
    return any(parte in CARPETAS_TEST for parte in partes[:-1])


def generar_arbol(raiz, extensiones):
    """
    Genera una representación en texto tipo 'árbol' de la estructura del proyecto.
    Incluye los archivos de test (para que se vea la estructura completa),
    solo se excluyen carpetas de entornos/control de versiones y extensiones
    excluidas siempre (ej. .json).
    """
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
    """
    Recorre el proyecto y devuelve la lista de rutas de archivos cuyo
    CONTENIDO se va a exportar. Acá sí se excluyen los archivos y carpetas
    de tests (aunque aparezcan en el árbol de estructura).
    """
    archivos_encontrados = []
    for carpeta_actual, subcarpetas, archivos in os.walk(raiz):
        # Modificar subcarpetas in-place para que os.walk no entre en ellas
        subcarpetas[:] = [
            d for d in subcarpetas
            if d not in CARPETAS_EXCLUIDAS and not d.startswith(".")
        ]

        ruta_relativa_carpeta = os.path.relpath(carpeta_actual, raiz)
        dentro_de_carpeta_test = any(
            parte in CARPETAS_TEST for parte in ruta_relativa_carpeta.split(os.sep)
        )

        for archivo in sorted(archivos):
            if archivo in ARCHIVOS_EXCLUIDOS:
                continue
            if dentro_de_carpeta_test or es_archivo_test(archivo):
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
        # salvo .json (exclusión dura) y archivos/carpetas de test (se omite
        # su contenido, aunque igual quedan reflejados en el árbol general).
        archivos = []
        faltantes = []
        omitidos = []
        for ruta_relativa in archivos_especificos:
            # Normalizamos separadores: aceptamos tanto "/" como "\" sin
            # importar el sistema operativo desde el que se escribió la ruta.
            ruta_normalizada = ruta_relativa.replace("\\", os.sep).replace("/", os.sep)
            nombre_archivo = os.path.basename(ruta_normalizada)
            _, ext = os.path.splitext(ruta_normalizada)
            es_test = es_archivo_test(nombre_archivo) or esta_en_carpeta_test(ruta_normalizada)
            if ext.lower() in EXTENSIONES_EXCLUIDAS_SIEMPRE or es_test:
                omitidos.append(ruta_relativa)
                continue
            ruta_absoluta = os.path.join(raiz, ruta_normalizada)
            if os.path.isfile(ruta_absoluta):
                archivos.append(ruta_absoluta)
            else:
                faltantes.append(ruta_relativa)
        if omitidos:
            print("⚠️  Se omite el contenido de estos archivos (.json o tests):")
            for f in omitidos:
                print(f"    - {f}")
        if faltantes:
            print("⚠️  No se encontraron estos archivos (revisá la ruta o el --raiz):")
            for f in faltantes:
                print(f"    - {f}")
    else:
        archivos = recolectar_archivos(raiz, extensiones)

    print(f"Se encontraron {len(archivos)} archivo(s) para exportar contenido.")

    with open(salida, "w", encoding="utf-8") as f_salida:
        # Encabezado
        f_salida.write("=" * 80 + "\n")
        f_salida.write("EXPORTACIÓN COMPLETA DEL PROYECTO\n")
        f_salida.write(f"Ruta del proyecto: {raiz}\n")
        f_salida.write(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f_salida.write("=" * 80 + "\n\n")

        # Estructura de directorios (incluye archivos de test)
        f_salida.write("ESTRUCTURA DEL PROYECTO\n")
        f_salida.write("-" * 80 + "\n")
        f_salida.write(arbol + "\n\n")

        # Contenido de cada archivo (sin tests)
        f_salida.write("=" * 80 + "\n")
        f_salida.write("CONTENIDO DE LOS ARCHIVOS\n")
        f_salida.write("(No se incluye el contenido de archivos de test)\n")
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
            "exclusiones por carpeta/tipo, salvo .json y contenido de tests que "
            "siempre se excluyen). Ej: --archivos templates/layout.html static/js/apps/agenda.js"
        )
    )

    args = parser.parse_args()
    exportar_proyecto(args.raiz, args.salida, args.extensiones, args.archivos)


if __name__ == "__main__":
    main()