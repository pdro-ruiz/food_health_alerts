import os
import logging
from logging.handlers import RotatingFileHandler
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import shutil

# Obtener el directorio raíz del proyecto (donde está el script o un nivel arriba si está en scrapers/)
script_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(script_dir) == "scrapers":
    # El script está en la carpeta scrapers/
    root_dir = os.path.dirname(script_dir)
else:
    # El script está en la raíz
    root_dir = script_dir

# Crear carpetas "data", "data/scraps" y "logs" si no existen
data_dir = os.path.join(root_dir, "data")
scraps_dir = os.path.join(data_dir, "scraps")
logs_dir = os.path.join(root_dir, "logs")

os.makedirs(data_dir, exist_ok=True)
os.makedirs(scraps_dir, exist_ok=True)
os.makedirs(logs_dir, exist_ok=True)

# Configurar el sistema de logs
log_file = os.path.join(logs_dir, "rasff_downloader.log")
handler = RotatingFileHandler(log_file, maxBytes=1000000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Configurar el directorio de descarga (temporalmente usamos data_dir)
download_dir = os.path.abspath(data_dir)
chrome_prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}

# Configurar el driver de Selenium en modo headless
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Ejecuta sin abrir el navegador
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_experimental_option("prefs", chrome_prefs)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 30)

# URL de RASFF Window
url = "https://webgate.ec.europa.eu/rasff-window/screen/search?searchQueries=eyJkYXRlIjp7InN0YXJ0UmFuZ2UiOiIiLCJlbmRSYW5nZSI6IiJ9LCJjb3VudHJpZXMiOnt9LCJ0eXBlIjp7fSwibm90aWZpY2F0aW9uU3RhdHVzIjp7fSwicHJvZHVjdCI6eyJwcm9kdWN0Q2F0ZWdvcnkiOltbMTg0MjddLFsxODQzNCwxODQzNV0sWzE4NDQwXSxbMTg0NTRdXX0sInJpc2siOnt9LCJyZWZlcmVuY2UiOiIiLCJzdWJqZWN0IjoiIn0%3D"
driver.get(url)
logger.info("Accediendo a %s", url)

# Esperar a que el botón de exportación CSV esté disponible y sea clicable
csv_button = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//div[@id='export-list']/a[img[@alt='exportCsv']]")
))
logger.info("Botón de exportación CSV encontrado. Iniciando descarga...")

# Desplazar la vista hasta el botón para asegurarse de que esté visible
driver.execute_script("arguments[0].scrollIntoView(true);", csv_button)

# Usar click por JavaScript para evitar que otro elemento intercepte el click
driver.execute_script("arguments[0].click();", csv_button)

# Esperar a que se descargue el archivo CSV en el directorio de descarga
downloaded_file = None
timeout = 60  # segundos de espera máxima
start_time = time.time()

while time.time() - start_time < timeout:
    # Listar archivos en el directorio de descarga
    files = os.listdir(download_dir)
    # Buscar archivos con extensión .csv y descartar los temporales (crdownload)
    csv_files = [f for f in files if f.endswith(".csv") and ".crdownload" not in f]
    if csv_files:
        downloaded_file = csv_files[0]
        break
    time.sleep(1)

if downloaded_file:
    original_file_path = os.path.join(download_dir, downloaded_file)
    logger.info("Archivo descargado: %s", downloaded_file)

    
    # Guardar también en data/scraps/ con formato de nombre que incluye fecha
    timestamp = datetime.now().strftime("%Y%m%d")
    scraps_file_path = os.path.join(scraps_dir, f"rasff_alerts_{timestamp}.csv")
    shutil.copy2(original_file_path, scraps_file_path)
    
    # Si el archivo descargado no tenía un nombre estándar, podemos eliminar el original
    if downloaded_file != "rasff_alerts.csv":
        os.remove(original_file_path)
    
    print(f"Archivo guardado como: {main_file_path}")
    print(f"Archivo también guardado como: {scraps_file_path}")
    logger.info("Archivos guardados en %s y %s", main_file_path, scraps_file_path)
else:
    logger.error("El archivo CSV no se descargó en el tiempo esperado.")
    print("El archivo CSV no se descargó en el tiempo esperado.")

driver.quit()
logger.info("Navegador cerrado.")