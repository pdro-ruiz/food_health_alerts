import os
import logging
from logging.handlers import RotatingFileHandler
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

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
log_file = os.path.join(logs_dir, "fda_scraper.log")
handler = RotatingFileHandler(log_file, maxBytes=1000000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Setup driver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Opcional: ejecuta el navegador en modo sin interfaz gráfica
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 30)

# Cargar la página inicial
url = "https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts"
driver.get(url)
print(f"Scraping page 1: {url}")
logger.info("Scraping page 1: %s", url)

# Esperar a que la tabla inicial se cargue
wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".dataTables_processing")))
table = wait.until(EC.presence_of_element_located((By.ID, "datatable")))
rows = table.find_elements(By.CSS_SELECTOR, "tr[role='row']")[1:]
print(f"Extracting {len(rows)} rows from page 1...")
logger.info("Extracting %d rows from page 1", len(rows))

# Lista para almacenar todos los datos scrapeados
all_data = []

# Procesar las filas de la página 1
for row in rows:
    cols = row.find_elements(By.TAG_NAME, "td")
    if len(cols) >= 8:  # Asegurarse de que la fila tiene suficientes columnas
        all_data.append({
            "Date": cols[0].text.strip(),
            "Brand Name(s)": cols[1].text.strip(),
            "Product Description": cols[2].text.strip(),
            "Product Type": cols[3].text.strip(),
            "Recall Reason Description": cols[4].text.strip(),
            "Company Name": cols[5].text.strip(),
            "Terminated Recall": cols[6].text.strip(),
            "Excerpt": cols[7].text.strip()
        })

# Bucle de paginación para las siguientes páginas
page_number = 2
while True:
    try:
        next_button = driver.find_element(By.ID, "datatable_next")
        if "disabled" in next_button.get_attribute("class"):
            print("No more pages to scrape.")
            logger.info("No more pages to scrape.")
            break
        print(f"Scraping page {page_number}...")
        logger.info("Scraping page %d...", page_number)
        driver.execute_script("arguments[0].click();", next_button)
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".dataTables_processing")))
        rows = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr[role='row']")))[1:]
        print(f"Extracting {len(rows)} rows from page {page_number}...")
        logger.info("Extracting %d rows from page %d", len(rows), page_number)
        # Procesar las filas de la página actual
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 8:
                all_data.append({
                    "Date": cols[0].text.strip(),
                    "Brand Name(s)": cols[1].text.strip(),
                    "Product Description": cols[2].text.strip(),
                    "Product Type": cols[3].text.strip(),
                    "Recall Reason Description": cols[4].text.strip(),
                    "Company Name": cols[5].text.strip(),
                    "Terminated Recall": cols[6].text.strip(),
                    "Excerpt": cols[7].text.strip()
                })
        page_number += 1
    except Exception as e:
        print(f"Error navigating to page {page_number}: {e}")
        logger.error("Error navigating to page %d: %s", page_number, e)
        break

# Guardar los datos en archivos CSV
if all_data:
    df = pd.DataFrame(all_data)
    
    # Guardar en la raíz de data/ para compatibilidad con código existente
    root_csv_path = os.path.join(data_dir, "fda_alerts.csv")
    df.to_csv(root_csv_path, index=False)
    print(f"Data saved to {root_csv_path}")
    logger.info("Data saved to %s with %d records.", root_csv_path, len(all_data))
    
    # Guardar también en data/scraps/ con formato de nombre que incluye fecha
    timestamp = datetime.now().strftime("%Y%m%d")
    scraps_csv_path = os.path.join(scraps_dir, f"fda_alerts_{timestamp}.csv")
    df.to_csv(scraps_csv_path, index=False)
    print(f"Data also saved to {scraps_csv_path}")
    logger.info("Data also saved to %s", scraps_csv_path)
else:
    print("No data found to save.")
    logger.warning("No data found to save.")

# Cerrar el navegador
driver.quit()
print("Browser closed.")
logger.info("Browser closed.")