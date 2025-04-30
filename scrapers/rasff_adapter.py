"""
Adaptador para el scraper de RASFF existente para la nueva estructura.
"""
import os
import sys
import logging
import subprocess
import glob
from datetime import datetime

# Añadir el directorio raíz al path para importaciones cuando se ejecuta directamente
# Esto permite encontrar el módulo 'config'
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

# Ahora podemos importar desde config
try:
    from config.settings import SCRAPS_DIR, RASFF_FILENAME
except ImportError:
    # Fallback en caso de que no se pueda importar (para mayor robustez)
    SCRAPS_DIR = os.path.join(root_dir, "data", "scraps")
    RASFF_FILENAME = f"rasff_window_{datetime.now().strftime('%Y%m%d')}.csv"

def adapt_rasff_scraper():
    """
    Adapta el scraper de RASFF existente para la nueva estructura.
    
    En lugar de reimplementar el scraper desde cero, este adaptador:
    1. Ejecuta el scraper existente
    2. Mueve y renombra el archivo resultante a la estructura nueva
    
    Returns:
        bool: True si el proceso fue exitoso, False en caso de error.
    """
    # Configurar logging básico si no se ha configurado
    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO, 
                           format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    logger = logging.getLogger("scraper.rasff_adapter")
    logger.info("Iniciando adaptador para scraper RASFF")
    
    try:
        # Asegurar que el directorio de destino existe
        os.makedirs(SCRAPS_DIR, exist_ok=True)
        
        # Ruta al scraper original (buscar en varias ubicaciones posibles)
        scraper_path = None
        possible_paths = [
            os.path.join(root_dir, "scrapers", "rasff_scraper.py"),
            os.path.join(root_dir, "rasff_scraper.py")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                scraper_path = path
                break
        
        # Verificar que el scraper existe
        if not scraper_path:
            logger.error(f"No se encontró el scraper RASFF en ninguna ubicación")
            return False
        
        # Directorio de datos original
        original_data_dir = os.path.join(root_dir, "data")
        
        # Guardar lista de archivos CSV antes del scraping
        csv_files_before = set(glob.glob(os.path.join(original_data_dir, "*.csv")))
        
        # Ejecutar el scraper
        logger.info(f"Ejecutando scraper RASFF: {scraper_path}")
        result = subprocess.run([sys.executable, scraper_path], check=True)
        
        # Esperar un momento para que se complete la descarga
        import time
        time.sleep(5)
        
        # Listar archivos CSV después del scraping
        csv_files_after = set(glob.glob(os.path.join(original_data_dir, "*.csv")))
        
        # Identificar archivos nuevos
        new_files = csv_files_after - csv_files_before
        
        if not new_files:
            # Buscar cualquier archivo CSV que pueda ser de RASFF
            possible_rasff_files = [f for f in csv_files_after if "rasff" in f.lower() or "window" in f.lower()]
            if possible_rasff_files:
                new_files = [possible_rasff_files[0]]
            else:
                logger.error("No se encontraron archivos CSV nuevos después del scraping")
                return False
        
        # Usar el primer archivo nuevo encontrado
        original_path = list(new_files)[0]
        
        # Verificar que el archivo existe
        if not os.path.exists(original_path):
            logger.error(f"No se encontró el archivo generado por el scraper: {original_path}")
            return False
        
        # Ruta en la nueva estructura
        new_path = os.path.join(SCRAPS_DIR, RASFF_FILENAME)
        
        # Copiar el archivo a la nueva ubicación
        import shutil
        shutil.copy2(original_path, new_path)
        logger.info(f"Archivo copiado: {original_path} -> {new_path}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al ejecutar el scraper RASFF: {e}")
        return False
    except Exception as e:
        logger.error(f"Error en el adaptador RASFF: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    # Ejecutar adaptador
    success = adapt_rasff_scraper()
    if success:
        print("Adaptador RASFF ejecutado exitosamente")
    else:
        print("Error al ejecutar el adaptador RASFF")
        sys.exit(1)