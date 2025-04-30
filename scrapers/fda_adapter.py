"""
Adaptador para el scraper de FDA existente para la nueva estructura.
"""
import os
import sys
import logging
import subprocess
from datetime import datetime

# Añadir el directorio raíz al path para importaciones cuando se ejecuta directamente
# Esto permite encontrar el módulo 'config'
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

# Ahora podemos importar desde config
try:
    from config.settings import SCRAPS_DIR, FDA_FILENAME
except ImportError:
    # Fallback en caso de que no se pueda importar (para mayor robustez)
    SCRAPS_DIR = os.path.join(root_dir, "data", "scraps")
    FDA_FILENAME = f"fda_alerts_{datetime.now().strftime('%Y%m%d')}.csv"

def adapt_fda_scraper():
    """
    Adapta el scraper de FDA existente para la nueva estructura.
    
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
    
    logger = logging.getLogger("scraper.fda_adapter")
    logger.info("Iniciando adaptador para scraper FDA")
    
    try:
        # Asegurar que el directorio de destino existe
        os.makedirs(SCRAPS_DIR, exist_ok=True)
        
        # Ruta al scraper original (buscar en varias ubicaciones posibles)
        scraper_path = None
        possible_paths = [
            os.path.join(root_dir, "scrapers", "fda_scraper.py"),
            os.path.join(root_dir, "fda_scraper.py")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                scraper_path = path
                break
        
        # Verificar que el scraper existe
        if not scraper_path:
            logger.error(f"No se encontró el scraper FDA en ninguna ubicación")
            return False
        
        # Ejecutar el scraper
        logger.info(f"Ejecutando scraper FDA: {scraper_path}")
        result = subprocess.run([sys.executable, scraper_path], check=True)
        
        # Ubicación esperada del archivo resultante
        data_dir = os.path.join(root_dir, "data")
        original_path = os.path.join(data_dir, "fda_alerts.csv")
        
        # Verificar que el archivo se generó
        if not os.path.exists(original_path):
            logger.error(f"No se encontró el archivo generado por el scraper: {original_path}")
            return False
        
        # Ruta en la nueva estructura
        new_path = os.path.join(SCRAPS_DIR, FDA_FILENAME)
        
        # Copiar el archivo a la nueva ubicación
        import shutil
        shutil.copy2(original_path, new_path)
        logger.info(f"Archivo copiado: {original_path} -> {new_path}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al ejecutar el scraper FDA: {e}")
        return False
    except Exception as e:
        logger.error(f"Error en el adaptador FDA: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    # Ejecutar adaptador
    success = adapt_fda_scraper()
    if success:
        print("Adaptador FDA ejecutado exitosamente")
    else:
        print("Error al ejecutar el adaptador FDA")
        sys.exit(1)