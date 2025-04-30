#!/usr/bin/env python3
"""
Script principal para la ejecución del pipeline de alertas alimentarias.

Este script coordina:
1. La obtención de datos mediante scraping (por defecto)
2. El procesamiento y filtrado de datos
3. La actualización del dataset consolidado
4. La generación de informes de análisis de riesgos
"""
import os
import sys
import argparse
import logging
import subprocess
from datetime import datetime

# Añadir directorio raíz al path para importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import (
    SCRAPS_DIR, PROCESSED_DIR, FINAL_DIR, 
    FDA_FILENAME, RASFF_FILENAME
)
from processors.data_filter import process_and_filter_data
from processors.data_merger import update_consolidated_dataset, get_dataset_statistics
from scripts.report_generator import AlertReportGenerator

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_scraper(scraper_name):
    """
    Ejecuta un scraper específico.
    
    Args:
        scraper_name (str): Nombre del scraper a ejecutar ('fda', 'rasff' o 'all').
        
    Returns:
        bool: True si la ejecución fue exitosa, False en caso contrario.
    """
    scrapers = []
    
    # Verificar si los scrapers están en la carpeta "scrapers" o en la raíz
    scrapers_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scrapers")
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    if scraper_name == 'fda' or scraper_name == 'all':
        # Primero verificar en la carpeta scrapers
        if os.path.exists(os.path.join(scrapers_dir, "fda_scraper.py")):
            scrapers.append(os.path.join(scrapers_dir, "fda_scraper.py"))
        # Si no existe, verificar en la carpeta scrapers/fda_adapter.py
        elif os.path.exists(os.path.join(scrapers_dir, "fda_adapter.py")):
            scrapers.append(os.path.join(scrapers_dir, "fda_adapter.py"))
        # Si no existe, verificar en la raíz
        elif os.path.exists(os.path.join(root_dir, "fda_scraper.py")):
            scrapers.append(os.path.join(root_dir, "fda_scraper.py"))
        else:
            logger.error("No se encontró el scraper de FDA")
    
    if scraper_name == 'rasff' or scraper_name == 'all':
        # Primero verificar en la carpeta scrapers
        if os.path.exists(os.path.join(scrapers_dir, "rasff_scraper.py")):
            scrapers.append(os.path.join(scrapers_dir, "rasff_scraper.py"))
        # Si no existe, verificar en la carpeta scrapers/rasff_adapter.py
        elif os.path.exists(os.path.join(scrapers_dir, "rasff_adapter.py")):
            scrapers.append(os.path.join(scrapers_dir, "rasff_adapter.py"))
        # Si no existe, verificar en la raíz
        elif os.path.exists(os.path.join(root_dir, "rasff_scraper.py")):
            scrapers.append(os.path.join(root_dir, "rasff_scraper.py"))
        else:
            logger.error("No se encontró el scraper de RASFF")
    
    success = True
    for scraper in scrapers:
        logger.info(f"Ejecutando scraper: {scraper}")
        try:
            result = subprocess.run([sys.executable, scraper], check=True)
            logger.info(f"Scraper ejecutado exitosamente: {scraper}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error al ejecutar scraper {scraper}: {e}")
            success = False
        except Exception as e:
            logger.error(f"Excepción al ejecutar scraper {scraper}: {e}")
            success = False
    
    return success

def move_files_to_scraps_dir():
    """
    Mueve los archivos descargados por los scrapers a la carpeta de scraps.
    
    Returns:
        bool: True si la operación fue exitosa, False en caso contrario.
    """
    try:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        
        # Buscar archivos en data/
        files_to_move = []
        for file in os.listdir(data_dir):
            file_path = os.path.join(data_dir, file)
            # Solo procesar archivos, no directorios
            if os.path.isfile(file_path) and (file.startswith("fda_alerts") or file.startswith("RASFF_window")):
                files_to_move.append(file)
        
        # Mover archivos a data/scraps/
        for file in files_to_move:
            source_path = os.path.join(data_dir, file)
            
            # Renombrar según convención
            if file.startswith("fda_alerts"):
                dest_filename = FDA_FILENAME
            elif file.startswith("RASFF_window"):
                dest_filename = RASFF_FILENAME
            else:
                dest_filename = file
            
            dest_path = os.path.join(SCRAPS_DIR, dest_filename)
            
            # Mover archivo
            os.rename(source_path, dest_path)
            logger.info(f"Archivo movido: {source_path} -> {dest_path}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error al mover archivos a la carpeta de scraps: {e}")
        return False

def are_recent_files_available():
    """
    Verifica si hay archivos recientes disponibles en la carpeta scraps.
    
    Returns:
        bool: True si hay archivos CSV recientes, False en caso contrario.
    """
    # Verificar si existen archivos en la carpeta scraps
    if not os.path.exists(SCRAPS_DIR):
        return False
    
    # Buscar archivos CSV
    csv_files = [f for f in os.listdir(SCRAPS_DIR) if f.endswith('.csv')]
    if not csv_files:
        return False
    
    # Verificar si alguno es reciente (última hora)
    current_time = datetime.now().timestamp()
    one_hour_ago = current_time - 3600  # 1 hora en segundos
    
    for file in csv_files:
        file_path = os.path.join(SCRAPS_DIR, file)
        file_time = os.path.getmtime(file_path)
        if file_time > one_hour_ago:
            # Hay al menos un archivo reciente
            return True
    
    # Ningún archivo es reciente
    return False

def run_pipeline(force_scrape=False, scraper='all', process_only=False, report=True, report_type='all'):
    """
    Ejecuta el pipeline completo de procesamiento de alertas alimentarias.
    
    Args:
        force_scrape (bool): Si es True, fuerza la ejecución de los scrapers incluso si hay datos recientes.
        scraper (str): Especifica qué scraper ejecutar ('fda', 'rasff', 'all').
        process_only (bool): Si es True, solo procesa los datos existentes sin hacer scraping.
        report (bool): Si es True, genera informes al final del proceso.
        report_type (str): Tipo de informe a generar ('all', 'excel', 'pdf', 'executive').
        
    Returns:
        dict: Estadísticas del dataset consolidado y rutas a los informes generados.
    """
    logger.info("Iniciando pipeline de alertas alimentarias")
    
    # Crear directorios si no existen
    os.makedirs(SCRAPS_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(FINAL_DIR, exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # 1. Ejecutar scrapers (a menos que se indique lo contrario)
    if not process_only:
        # Verificar si necesitamos ejecutar los scrapers
        need_scraping = force_scrape or not are_recent_files_available()
        
        if need_scraping:
            logger.info(f"Ejecutando scrapers: {scraper}")
            scraping_success = run_scraper(scraper)
            
            if not scraping_success:
                logger.warning("El proceso de scraping no se completó correctamente")
            
            # Mover archivos descargados a la carpeta de scraps
            move_files_to_scraps_dir()
        else:
            logger.info("Se encontraron archivos recientes. Omitiendo el scraping.")
    else:
        logger.info("Modo de solo procesamiento. Omitiendo el scraping.")
    
    # 2. Procesar y filtrar datos
    logger.info("Procesando y filtrando datos")
    processed_file_path = process_and_filter_data()
    
    if not processed_file_path:
        logger.error("Error al procesar y filtrar datos")
        return None
    
    # 3. Actualizar dataset consolidado
    logger.info("Actualizando dataset consolidado")
    consolidated_path = update_consolidated_dataset(processed_file_path)
    
    if not consolidated_path:
        logger.error("Error al actualizar el dataset consolidado")
        return None
    
    # 4. Obtener estadísticas
    logger.info("Calculando estadísticas del dataset consolidado")
    stats = get_dataset_statistics(consolidated_path)
    
    logger.info("Pipeline completado exitosamente")
    logger.info(f"Total de registros en dataset consolidado: {stats['total_records']}")
    
    # 5. Generar informes (opcional)
    report_paths = None
    if report:
        logger.info(f"Generando informes ({report_type})")
        report_generator = AlertReportGenerator()
        report_paths = report_generator.generate_report(report_type=report_type)
        
        if report_paths:
            if isinstance(report_paths, dict):
                for rep_type, path in report_paths.items():
                    if path:
                        logger.info(f"Informe {rep_type} generado en: {path}")
            else:
                logger.info(f"Informe {report_type} generado en: {report_paths}")
        else:
            logger.error("Error al generar los informes")
    
    # Añadir rutas de informes a las estadísticas para devolver
    result = stats.copy()
    if report_paths:
        result['reports'] = report_paths
    
    return result

def main():
    """Función principal."""
    # Verificar que existan las carpetas necesarias
    os.makedirs("logs", exist_ok=True)
    
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Pipeline de alertas alimentarias')
    parser.add_argument('--scrape', action='store_true', 
                        help='Forzar la ejecución de scrapers incluso si hay datos recientes')
    parser.add_argument('--scraper', choices=['fda', 'rasff', 'all'], default='all',
                        help='Especificar qué scraper ejecutar')
    parser.add_argument('--process-only', action='store_true',
                        help='Solo procesar datos existentes, no hacer scraping')
    parser.add_argument('--no-report', dest='report', action='store_false',
                        help='No generar informes al final del proceso')
    parser.add_argument('--report-type', choices=['all', 'excel', 'pdf', 'executive'], default='all',
                        help='Tipo de informe a generar')
    
    parser.set_defaults(report=True)
    
    args = parser.parse_args()
    
    # Ejecutar pipeline
    result = run_pipeline(
        force_scrape=args.scrape, 
        scraper=args.scraper,
        process_only=args.process_only,
        report=args.report,
        report_type=args.report_type
    )
    
    if result:
        print("\n=== Estadísticas del Dataset Consolidado ===")
        print(f"Total de registros: {result['total_records']}")
        
        print("\nDistribución por fuente:")
        for source, count in result['sources'].items():
            print(f"  - {source}: {count}")
        
        print("\nDistribución por categoría:")
        for category, count in result['categories'].items():
            print(f"  - {category}: {count}")
        
        print("\nRango de fechas:")
        print(f"  - Primera alerta: {result['date_range']['min']}")
        print(f"  - Última alerta: {result['date_range']['max']}")
        
        # Mostrar información sobre informes generados
        if 'reports' in result:
            print("\n=== Informes Generados ===")
            reports = result['reports']
            if isinstance(reports, dict):
                for rep_type, path in reports.items():
                    if path:
                        print(f"  - {rep_type}: {path}")
            else:
                print(f"  - Informe: {reports}")
    else:
        print("\nError al ejecutar el pipeline. Revise los logs para más detalles.")

if __name__ == "__main__":
    main()