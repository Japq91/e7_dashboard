"""
html_loader.py - Cargador de archivos HTML para infografías
"""

import os
from pathlib import Path

def obtener_lista_html(carpeta_html="data/html"):
    """
    Obtiene la lista de archivos HTML disponibles en la carpeta
    
    Args:
        carpeta_html (str): Ruta a la carpeta con archivos HTML
    
    Returns:
        list: Lista de nombres de archivos HTML encontrados
    """
    try:
        # Verificar si la carpeta existe
        ruta_carpeta = Path(carpeta_html)
        if not ruta_carpeta.exists():
            raise FileNotFoundError(f"No se encontró la carpeta: {carpeta_html}")
        
        # Listar archivos HTML
        archivos_html = [f for f in os.listdir(ruta_carpeta) if f.endswith('.html')]
        
        # Ordenar alfabéticamente
        archivos_html.sort()
        
        return archivos_html
    
    except Exception as e:
        print(f"Error al listar archivos HTML: {e}")
        return []

def cargar_html(nombre_archivo, carpeta_html="data/html"):
    """
    Carga el contenido de un archivo HTML específico
    
    Args:
        nombre_archivo (str): Nombre del archivo HTML
        carpeta_html (str): Ruta a la carpeta con archivos HTML
    
    Returns:
        str: Contenido del archivo HTML
    """
    try:
        ruta_archivo = Path(carpeta_html) / nombre_archivo
        
        if not ruta_archivo.exists():
            raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo}")
        
        # Leer contenido con codificación UTF-8
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        return contenido
    
    except Exception as e:
        print(f"Error al cargar archivo HTML {nombre_archivo}: {e}")
        return f"<html><body><h1>Error al cargar {nombre_archivo}</h1><p>{str(e)}</p></body></html>"

def obtener_nombres_amigables():
    """
    Devuelve un diccionario con nombres amigables para los archivos HTML    
    Returns:
        dict: {nombre_archivo: nombre_amigable}
    """
    # Puedes personalizar estos nombres según tus archivos
    mapeo_nombres = {
        "infografia1.html": "📊 Infografía 1 - Resumen General",
        "infografia2.html": "📈 Infografía 2 - Análisis Detallado",
        # Agrega más mapeos según necesites
    }
    return mapeo_nombres