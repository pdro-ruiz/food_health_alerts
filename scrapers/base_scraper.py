"""
Clase base para los scrapers de alertas alimentarias.
"""
import os
import logging
from abc import ABC, abstractmethod
from datetime import datetime

from config.settings import SCRAPS_DIR

class BaseScraper(ABC):
    """
    Clase base abstracta para todos los scrapers de alertas alimentarias.
    
    Proporciona funcionalidad común y define interfaz para clases derivadas.
    """
    
    def __init__(self, name, output_dir=None):
        """
        Inicializa el scraper.
        
        Args:
            name (str): Nombre del scraper para identificación y logging.
            output_dir (str): Directorio de salida para los datos scrapeados.
        """
        self.name = name
        self.output_dir = output_dir or SCRAPS_DIR
        
        # Asegurar que el directorio de salida existe
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Configurar logger
        self.logger = logging.getLogger(f"scraper.{name}")
    
    @abstractmethod
    def initialize(self):
        """
        Inicializa recursos necesarios para el scraping.
        
        Por ejemplo, configura el driver de Selenium, establece conexiones, etc.
        """
        pass
    
    @abstractmethod
    def scrape(self):
        """
        Realiza el scraping principal.
        
        Esta función debe ser implementada por cada scraper específico.
        """
        pass
    
    @abstractmethod
    def save_data(self, data):
        """
        Guarda los datos obtenidos en el formato adecuado.
        
        Args:
            data: Datos a guardar (formato depende de la implementación).
            
        Returns:
            str: Ruta al archivo guardado.
        """
        pass
    
    @abstractmethod
    def cleanup(self):
        """
        Limpia recursos utilizados (por ejemplo, cierra conexiones).
        """
        pass
    
    def run(self):
        """
        Ejecuta el proceso completo de scraping.
        
        Returns:
            bool: True si el proceso fue exitoso, False en caso de error.
        """
        self.logger.info(f"Iniciando scraper: {self.name}")
        try:
            # Inicializar recursos
            self.initialize()
            self.logger.info("Recursos inicializados")
            
            # Ejecutar scraping
            data = self.scrape()
            self.logger.info("Scraping completado")
            
            # Guardar datos
            result_path = self.save_data(data)
            self.logger.info(f"Datos guardados en: {result_path}")
            
            # Cleanup
            self.cleanup()
            self.logger.info("Recursos liberados")
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error en scraper {self.name}: {e}", exc_info=True)
            # Intentar limpiar recursos en caso de error
            try:
                self.cleanup()
                self.logger.info("Recursos liberados después de error")
            except Exception as cleanup_error:
                self.logger.error(f"Error al liberar recursos: {cleanup_error}")
            
            return False