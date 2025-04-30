"""
Configuraciones generales del proyecto de alertas alimentarias.
"""
import os
from datetime import datetime

# Rutas de directorios
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
SCRAPS_DIR = os.path.join(DATA_DIR, "scraps")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
FINAL_DIR = os.path.join(DATA_DIR, "final")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Crear directorios si no existen
for directory in [DATA_DIR, RAW_DATA_DIR, SCRAPS_DIR, PROCESSED_DIR, FINAL_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Configuración de scraping
SCRAPING_FREQUENCY = "weekly"  # diaria, semanal, mensual
MAX_RETRIES = 3
TIMEOUT = 30  # segundos

# Nombres de archivos
TIMESTAMP_FORMAT = "%Y%m%d"
FDA_FILENAME = f"fda_alerts_{datetime.now().strftime(TIMESTAMP_FORMAT)}.csv"
RASFF_FILENAME = f"rasff_window_{datetime.now().strftime(TIMESTAMP_FORMAT)}.csv"
PROCESSED_BAKERY_FILENAME = f"bakery_dairy_alerts_{datetime.now().strftime(TIMESTAMP_FORMAT)}.csv"
FINAL_DATASET_FILENAME = "consolidated_bakery_dairy_alerts.csv"

# URLs de fuentes de datos
FDA_URL = "https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts"
RASFF_URL = "https://webgate.ec.europa.eu/rasff-window/screen/search?searchQueries=eyJkYXRlIjp7InN0YXJ0UmFuZ2UiOiIiLCJlbmRSYW5nZSI6IiJ9LCJjb3VudHJpZXMiOnt9LCJ0eXBlIjp7fSwibm90aWZpY2F0aW9uU3RhdHVzIjp7fSwicHJvZHVjdCI6eyJwcm9kdWN0Q2F0ZWdvcnkiOltbMTg0MjddLFsxODQzNCwxODQzNV0sWzE4NDQwXSxbMTg0NTRdXX0sInJpc2siOnt9LCJyZWZlcmVuY2UiOiIiLCJzdWJqZWN0IjoiIn0%3D"

# Añadir el directorio del proyecto al path de Python
# Esto ayuda a resolver problemas de importación de módulos
import sys
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)