#!/usr/bin/env python3
"""
Script para probar el generador de informes de manera independiente.

Este script permite verificar que el generador de informes funciona correctamente
sin necesidad de ejecutar todo el pipeline de procesamiento.
"""

import os
import sys
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/report_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Función principal para probar el generador de informes."""
    # Añadir directorio raíz al path para importaciones
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.append(project_root)
    
    try:
        # Importar AlertReportGenerator
        from scripts.report_generator import AlertReportGenerator
        
        # Verificar que existe el directorio de logs
        os.makedirs("logs", exist_ok=True)
        
        # Crear una instancia del generador de informes
        report_generator = AlertReportGenerator()
        
        # Generar todos los informes
        reports = report_generator.generate_report()
        
        if reports:
            print("\n=== Informes Generados Exitosamente ===")
            for report_type, path in reports.items():
                print(f"  - {report_type}: {path}")
            print("\nPrueba completada con éxito.")
            return 0
        else:
            print("\n❌ Error al generar informes. Revise los logs para más detalles.")
            return 1
    
    except ImportError as e:
        print(f"\n❌ Error de importación: {e}")
        print("Verifique que el script report_generator.py esté en la carpeta 'scripts'")
        return 1
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())