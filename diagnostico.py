import os
import sys

def main():
    """Script de diagnóstico para verificar la estructura de archivos"""
    print("=== DIAGNÓSTICO DE ESTRUCTURA DE ARCHIVOS ===")
    
    # Obtener directorio raíz
    root_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Directorio raíz: {root_dir}")
    
    # Verificar estructura de directorios
    data_dir = os.path.join(root_dir, "data")
    print(f"\nVerificando directorio de datos: {data_dir}")
    if os.path.exists(data_dir):
        print("  [✓] Directorio 'data' encontrado")
        print(f"  Contenido de 'data':")
        for item in os.listdir(data_dir):
            item_path = os.path.join(data_dir, item)
            if os.path.isdir(item_path):
                print(f"    📁 {item}/")
            else:
                print(f"    📄 {item} ({os.path.getsize(item_path)} bytes)")
    else:
        print("  [✗] Directorio 'data' NO encontrado")
    
    # Verificar archivos CSV específicos
    fda_file = os.path.join(data_dir, "fda_alerts.csv")
    rasff_file = os.path.join(data_dir, "RASFF_window.csv")
    
    print("\nVerificando archivos CSV:")
    if os.path.exists(fda_file):
        print(f"  [✓] Archivo FDA encontrado: {fda_file}")
    else:
        print(f"  [✗] Archivo FDA NO encontrado en: {fda_file}")
    
    if os.path.exists(rasff_file):
        print(f"  [✓] Archivo RASFF encontrado: {rasff_file}")
    else:
        print(f"  [✗] Archivo RASFF NO encontrado en: {rasff_file}")
    
    # Buscar en todo el directorio data y subdirectorios
    print("\nBuscando archivos CSV en todo el directorio 'data' y subdirectorios:")
    found_files = []
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                found_files.append(file_path)
                print(f"  • {file_path}")
    
    if not found_files:
        print("  [✗] No se encontraron archivos CSV en ningún lugar")
    
    # Verificar módulos de Python
    print("\nVerificando módulos y paquetes Python:")
    for module_name in ["config", "processors", "scrapers", "utils"]:
        module_dir = os.path.join(root_dir, module_name)
        init_file = os.path.join(module_dir, "__init__.py")
        
        if os.path.exists(module_dir):
            print(f"  [✓] Directorio '{module_name}' encontrado")
            if os.path.exists(init_file):
                print(f"    [✓] Archivo '{module_name}/__init__.py' encontrado")
            else:
                print(f"    [✗] Archivo '{module_name}/__init__.py' NO encontrado")
        else:
            print(f"  [✗] Directorio '{module_name}' NO encontrado")
    
    # Consejos finales
    print("\n=== Consejos basados en el diagnóstico ===")
    if not os.path.exists(data_dir) or not found_files:
        print("1. Crea la estructura de directorios necesaria:")
        print("   mkdir -Force data, data\\scraps, data\\processed, data\\final")
        print("2. Asegúrate de que los archivos CSV estén en la ubicación correcta")
    else:
        print("1. Comprueba que los nombres de los archivos coinciden con lo esperado")
        print("2. Verifica que los archivos CSV tienen el formato correcto y no están dañados")
    
    print("\nEjecuta este diagnóstico después de realizar cambios para verificar.")

if __name__ == "__main__":
    main()