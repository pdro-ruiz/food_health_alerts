"""
Script para corregir la ubicación de los archivos CSV y configurar
correctamente la estructura de directorios del proyecto.
"""
import os
import shutil
import sys
from datetime import datetime

def main():
    """Corrige la estructura de directorios y la ubicación de los archivos CSV."""
    print("=== CORRECCIÓN DE ESTRUCTURA DE DIRECTORIOS ===")
    
    # Obtener directorio raíz
    root_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Directorio raíz: {root_dir}")
    
    # Crear estructura de directorios
    directories = [
        os.path.join(root_dir, "data"),
        os.path.join(root_dir, "data", "scraps"),
        os.path.join(root_dir, "data", "processed"),
        os.path.join(root_dir, "data", "final"),
        os.path.join(root_dir, "logs"),
        os.path.join(root_dir, "config"),
        os.path.join(root_dir, "processors"),
        os.path.join(root_dir, "scrapers"),
        os.path.join(root_dir, "utils")
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Directorio creado/verificado: {directory}")
    
    # Verificar archivos __init__.py en paquetes Python
    for module_name in ["config", "processors", "scrapers", "utils"]:
        init_file = os.path.join(root_dir, module_name, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write(f'"""\nMódulo {module_name} para proyecto de Alertas Alimentarias.\n"""\n')
            print(f"Archivo creado: {init_file}")
    
    # Buscar archivos CSV en el directorio data
    data_dir = os.path.join(root_dir, "data")
    scraps_dir = os.path.join(data_dir, "scraps")
    
    fda_source = os.path.join(data_dir, "fda_alerts.csv")
    rasff_source = os.path.join(data_dir, "RASFF_window.csv")
    
    # Timestamp para nombres de archivo
    timestamp = datetime.now().strftime("%Y%m%d")
    
    # Mover/copiar archivo FDA
    if os.path.exists(fda_source):
        fda_dest = os.path.join(scraps_dir, f"fda_alerts_{timestamp}.csv")
        if not os.path.exists(fda_dest):
            shutil.copy2(fda_source, fda_dest)
            print(f"Archivo copiado: {fda_source} -> {fda_dest}")
    else:
        print(f"No se encontró el archivo FDA en: {fda_source}")
    
    # Mover/copiar archivo RASFF
    if os.path.exists(rasff_source):
        rasff_dest = os.path.join(scraps_dir, f"rasff_window_{timestamp}.csv")
        if not os.path.exists(rasff_dest):
            shutil.copy2(rasff_source, rasff_dest)
            print(f"Archivo copiado: {rasff_source} -> {rasff_dest}")
    else:
        print(f"No se encontró el archivo RASFF en: {rasff_source}")
    
    # Verificar resultado final
    print("\n=== VERIFICACIÓN FINAL ===")
    for root, dirs, files in os.walk(scraps_dir):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                print(f"Archivo en scraps/: {file} ({file_size} bytes)")
    
    print("\n=== INSTRUCCIONES FINALES ===")
    print("1. Ahora puedes ejecutar el pipeline:")
    print("   python main.py")
    print("2. Si encuentras más problemas, ejecuta el script de diagnóstico:")
    print("   python diagnostico.py")

if __name__ == "__main__":
    main()