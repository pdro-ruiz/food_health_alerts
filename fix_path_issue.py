"""
Script de corrección para resolver problemas de path de Python.

Este script crea un archivo .pth en el directorio site-packages 
de Python para añadir el directorio del proyecto al path de búsqueda.
"""
import os
import sys
import site

def main():
    """
    Añade el directorio del proyecto al path de Python.
    """
    print("=== Corrigiendo problemas de path de Python ===")
    
    # Obtener directorio raíz del proyecto
    root_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Directorio del proyecto: {root_dir}")
    
    # Obtener directorio site-packages de Python
    site_packages_dir = site.getsitepackages()[0]
    print(f"Directorio site-packages: {site_packages_dir}")
    
    # Nombre del archivo .pth
    pth_filename = "food_alerts.pth"
    pth_path = os.path.join(site_packages_dir, pth_filename)
    
    try:
        # Crear archivo .pth
        with open(pth_path, 'w') as f:
            f.write(root_dir)
        
        print(f"Archivo creado: {pth_path}")
        print("El directorio del proyecto ha sido añadido al path de Python.")
        print("Ahora los módulos 'config', 'processors', etc. deberían ser encontrados.")
        
        # Verificar que el path se ha añadido correctamente
        sys.path.append(root_dir)
        print("\nVerificando importaciones:")
        
        try:
            import config
            print("✓ El módulo 'config' puede ser importado.")
        except ImportError as e:
            print(f"✗ Error al importar 'config': {e}")
        
        # Instrucciones finales
        print("\n=== Instrucciones finales ===")
        print("1. Reinicia tu consola de Python.")
        print("2. Ejecuta el script principal:")
        print("   python main.py")
        
    except PermissionError:
        print("\n¡ERROR DE PERMISOS!")
        print("No tienes permisos para escribir en el directorio site-packages.")
        print("\nAlternativa: Ejecuta Python con permisos de administrador:")
        print("1. Abre PowerShell como administrador")
        print("2. Navega a tu proyecto y ejecuta:")
        print("   python fix_path_issue.py")
        
        print("\nO usa esta alternativa sin privilegios de administrador:")
        print("Antes de ejecutar tu script, añade esta línea al principio de main.py:")
        print('import sys; sys.path.append(r"' + root_dir + '")')

if __name__ == "__main__":
    main()