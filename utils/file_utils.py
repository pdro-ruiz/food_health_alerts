"""
Utilidades para manejo de archivos.
"""
import os
import csv
import json
import shutil
import pandas as pd
from datetime import datetime

def get_latest_file(directory, prefix=None, suffix=None):
    """
    Obtiene el archivo más reciente en un directorio.
    
    Args:
        directory (str): Ruta al directorio.
        prefix (str, optional): Prefijo que debe tener el archivo.
        suffix (str, optional): Sufijo que debe tener el archivo (por ejemplo, ".csv").
        
    Returns:
        str: Ruta completa al archivo más reciente, o None si no se encuentra.
    """
    try:
        files = os.listdir(directory)
        
        # Filtrar por prefijo y sufijo si se especifican
        if prefix:
            files = [f for f in files if f.startswith(prefix)]
        if suffix:
            files = [f for f in files if f.endswith(suffix)]
        
        if not files:
            return None
        
        # Ordenar por fecha de modificación (más reciente primero)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)
        
        return os.path.join(directory, files[0])
    
    except Exception as e:
        print(f"Error al buscar el archivo más reciente: {e}")
        return None

def ensure_directory(path):
    """
    Asegura que un directorio existe, creándolo si es necesario.
    
    Args:
        path (str): Ruta al directorio.
        
    Returns:
        bool: True si el directorio existe o se creó exitosamente.
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error al crear directorio {path}: {e}")
        return False

def copy_with_timestamp(source, dest_dir, prefix="", suffix=""):
    """
    Copia un archivo añadiendo un timestamp al nombre.
    
    Args:
        source (str): Ruta al archivo de origen.
        dest_dir (str): Directorio de destino.
        prefix (str, optional): Prefijo para el nombre del archivo.
        suffix (str, optional): Sufijo para el nombre del archivo.
        
    Returns:
        str: Ruta al archivo copiado, o None si ocurre un error.
    """
    try:
        # Asegurar que el directorio de destino existe
        ensure_directory(dest_dir)
        
        # Obtener timestamp actual
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Extraer nombre base y extensión
        base_name = os.path.basename(source)
        name, ext = os.path.splitext(base_name)
        
        # Crear nuevo nombre
        new_name = f"{prefix}{name}_{timestamp}{suffix}{ext}"
        dest_path = os.path.join(dest_dir, new_name)
        
        # Copiar archivo
        shutil.copy2(source, dest_path)
        
        return dest_path
    
    except Exception as e:
        print(f"Error al copiar archivo: {e}")
        return None

def csv_to_json(csv_path, json_path, encoding='utf-8'):
    """
    Convierte un archivo CSV a JSON.
    
    Args:
        csv_path (str): Ruta al archivo CSV.
        json_path (str): Ruta de salida para el archivo JSON.
        encoding (str, optional): Codificación del archivo CSV.
        
    Returns:
        bool: True si la conversión fue exitosa.
    """
    try:
        # Leer CSV con pandas
        df = pd.read_csv(csv_path, encoding=encoding)
        
        # Convertir a JSON
        with open(json_path, 'w', encoding=encoding) as f:
            f.write(df.to_json(orient='records', force_ascii=False))
        
        return True
    
    except Exception as e:
        print(f"Error al convertir CSV a JSON: {e}")
        return False

def is_csv_modified(file_path, last_modified_time):
    """
    Verifica si un archivo CSV ha sido modificado desde la última vez.
    
    Args:
        file_path (str): Ruta al archivo CSV.
        last_modified_time (float): Timestamp de la última modificación conocida.
        
    Returns:
        bool: True si el archivo ha sido modificado.
    """
    try:
        current_modified_time = os.path.getmtime(file_path)
        return current_modified_time > last_modified_time
    except Exception:
        # Si hay algún error, asumimos que el archivo ha cambiado
        return True