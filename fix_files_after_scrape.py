"""
Script para mover correctamente los archivos después del scraping.

Este script debe ejecutarse después de que los scrapers hayan completado su trabajo
y antes de ejecutar el procesamiento de datos.
"""
import os
import shutil
import sys
from datetime import datetime

def main():
    """
    Encuentra y mueve los archivos CSV generados por los scrapers a la ubicación correcta.
    """
    print("=== Moviendo archivos después del scraping ===")
    
    # Obtener directorio raíz del proyecto
    root_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Directorio del proyecto: {root_dir}")
    
    # Definir directorios
    data_dir = os.path.join(root_dir, "data")
    parent_data_dir = os.path.join(root_dir, "..", "data")  # Directorio ../data/
    scraps_dir = os.path.join(data_dir, "scraps")
    
    # Crear directorio de scraps si no existe
    os.makedirs(scraps_dir, exist_ok=True)
    
    # Timestamp para nombres de archivo
    timestamp = datetime.now().strftime("%Y%m%d")
    
    # Lista de posibles ubicaciones y patrones de archivos
    locations_to_check = [
        data_dir,
        parent_data_dir,
        root_dir,
        os.path.join(root_dir, ".."),
    ]
    
    # Patrones de archivos a buscar
    file_patterns = [
        {"pattern": "fda_alerts", "dest_name": f"fda_alerts_{timestamp}.csv"},
        {"pattern": "RASFF_window", "dest_name": f"rasff_window_{timestamp}.csv"},
        {"pattern": "rasff_window", "dest_name": f"rasff_window_{timestamp}.csv"},
    ]
    
    # Buscar y mover archivos
    found_files = False
    
    for location in locations_to_check:
        if not os.path.exists(location):
            continue
        
        print(f"Revisando directorio: {location}")
        
        for filename in os.listdir(location):
            file_path = os.path.join(location, filename)
            
            if not os.path.isfile(file_path) or not filename.endswith('.csv'):
                continue
            
            for pattern in file_patterns:
                if pattern["pattern"] in filename.lower():
                    dest_path = os.path.join(scraps_dir, pattern["dest_name"])
                    print(f"Encontrado: {file_path}")
                    
                    # Copiar archivo a la ubicación correcta
                    shutil.copy2(file_path, dest_path)
                    print(f"Copiado a: {dest_path}")
                    found_files = True
                    break
    
    if not found_files:
        print("¡ADVERTENCIA! No se encontraron archivos CSV generados por los scrapers.")
        print("Asegúrate de que los scrapers se ejecutaron correctamente.")
        return False
    
    # Verificar que los archivos se hayan copiado correctamente
    print("\nVerificando archivos en la ubicación correcta:")
    for file in os.listdir(scraps_dir):
        if file.endswith('.csv'):
            print(f"  - {os.path.join(scraps_dir, file)}")
    
    print("\n=== Instrucciones ===")
    print("1. Ahora puedes ejecutar el procesamiento de datos:")
    print("   python main.py --process-only")
    print("2. O ejecutar el pipeline completo de nuevo:")
    print("   python main.py")
    
    return True

if __name__ == "__main__":
    main()