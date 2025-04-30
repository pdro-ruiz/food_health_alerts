"""
Módulo para unificar datasets de alertas alimentarias y actualizar el dataset consolidado.
"""
import os
import pandas as pd
import logging
from datetime import datetime

from config.settings import PROCESSED_DIR, FINAL_DIR, FINAL_DATASET_FILENAME

logger = logging.getLogger(__name__)

def update_consolidated_dataset(processed_file_path):
    """
    Actualiza el dataset consolidado con nuevos datos procesados.
    
    Si el dataset consolidado no existe, se crea uno nuevo.
    Si existe, se añaden únicamente los registros que no estén presentes.
    
    Args:
        processed_file_path (str): Ruta al archivo CSV de datos procesados.
        
    Returns:
        str: Ruta al dataset consolidado actualizado.
    """
    try:
        # Verificar si existe el archivo procesado
        if not os.path.exists(processed_file_path):
            logger.error(f"El archivo procesado no existe: {processed_file_path}")
            return None
        
        # Cargar datos procesados
        processed_df = pd.read_csv(processed_file_path)
        logger.info(f"Leyendo datos procesados desde {processed_file_path}: {len(processed_df)} filas")
        
        # Ruta al dataset consolidado
        consolidated_path = os.path.join(FINAL_DIR, FINAL_DATASET_FILENAME)
        
        # Verificar si existe el dataset consolidado
        if not os.path.exists(consolidated_path):
            logger.info(f"El dataset consolidado no existe. Creando uno nuevo: {consolidated_path}")
            processed_df.to_csv(consolidated_path, index=False)
            return consolidated_path
        
        # Cargar dataset consolidado existente
        consolidated_df = pd.read_csv(consolidated_path)
        logger.info(f"Leyendo dataset consolidado desde {consolidated_path}: {len(consolidated_df)} filas")
        
        # Identificar registros nuevos (no presentes en el dataset consolidado)
        # Asumimos que 'alert_id' es un identificador único
        existing_alerts = set(consolidated_df['alert_id'])
        new_records = processed_df[~processed_df['alert_id'].isin(existing_alerts)]
        
        if new_records.empty:
            logger.info("No hay nuevos registros para añadir al dataset consolidado")
            return consolidated_path
        
        # Añadir nuevos registros al dataset consolidado
        updated_df = pd.concat([consolidated_df, new_records], ignore_index=True)
        
        # Ordenar por fecha (de más reciente a más antiguo)
        if 'date' in updated_df.columns:
            try:
                # Intentar convertir a datetime para ordenar correctamente
                updated_df['date_temp'] = pd.to_datetime(updated_df['date'], errors='coerce')
                updated_df = updated_df.sort_values(by='date_temp', ascending=False)
                updated_df = updated_df.drop(columns=['date_temp'])
            except Exception as e:
                logger.warning(f"Error al ordenar por fecha: {e}")
        
        # Guardar dataset consolidado actualizado
        updated_df.to_csv(consolidated_path, index=False)
        logger.info(f"Dataset consolidado actualizado: {len(updated_df)} filas totales, {len(new_records)} registros nuevos")
        
        return consolidated_path
    
    except Exception as e:
        logger.error(f"Error al actualizar el dataset consolidado: {e}")
        return None

def get_dataset_statistics(file_path):
    """
    Obtiene estadísticas básicas del dataset.
    
    Args:
        file_path (str): Ruta al archivo CSV.
        
    Returns:
        dict: Diccionario con estadísticas.
    """
    try:
        if not os.path.exists(file_path):
            return {"error": "Archivo no encontrado"}
        
        df = pd.read_csv(file_path)
        
        stats = {
            "total_records": len(df),
            "sources": df['source_database'].value_counts().to_dict() if 'source_database' in df.columns else {},
            "categories": df['category'].value_counts().to_dict() if 'category' in df.columns else {},
            "countries": df['country_origin'].value_counts().to_dict() if 'country_origin' in df.columns else {},
            "date_range": {
                "min": df['date'].min() if 'date' in df.columns else None,
                "max": df['date'].max() if 'date' in df.columns else None
            }
        }
        
        return stats
    
    except Exception as e:
        logger.error(f"Error al obtener estadísticas del dataset: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Ejemplo de uso
    # Buscar el archivo procesado más reciente
    processed_files = [f for f in os.listdir(PROCESSED_DIR) if f.startswith('bakery_dairy_alerts_')]
    if processed_files:
        processed_files.sort(reverse=True)
        latest_processed = os.path.join(PROCESSED_DIR, processed_files[0])
        
        # Actualizar dataset consolidado
        result = update_consolidated_dataset(latest_processed)
        
        if result:
            # Mostrar estadísticas
            stats = get_dataset_statistics(result)
            print("Estadísticas del dataset consolidado:")
            print(f"Total de registros: {stats['total_records']}")
            print(f"Fuentes: {stats['sources']}")
            print(f"Categorías: {stats['categories']}")
        else:
            print("Error al actualizar el dataset consolidado")
    else:
        print("No se encontraron archivos procesados")