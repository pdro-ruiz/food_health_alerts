"""
Módulo para filtrar datos de alertas alimentarias según categorías específicas.
"""
import os
import pandas as pd
import logging
from datetime import datetime
import sys

# Añadir el directorio raíz al path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from config.settings import SCRAPS_DIR, PROCESSED_DIR, PROCESSED_BAKERY_FILENAME
from config.product_categories import is_target_product, TARGET_CATEGORIES, FDA_CATEGORY_MAPPING, RASFF_CATEGORY_MAPPING

logger = logging.getLogger(__name__)

def filter_fda_alerts(file_path):
    """
    Filtra alertas de la FDA relacionadas con las categorías objetivo.
    
    Args:
        file_path (str): Ruta al archivo CSV de alertas de la FDA.
        
    Returns:
        pandas.DataFrame: DataFrame con las alertas filtradas.
    """
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Leyendo datos de FDA desde {file_path}: {len(df)} filas")
        
        # Filtrar por categorías objetivo
        filtered_df = df[df.apply(lambda row: is_target_product(
            product_type=str(row.get('Product Type', '')),
            product_description=str(row.get('Product Description', '')),
            source="FDA"
        ), axis=1)]
        
        logger.info(f"Datos de FDA filtrados: {len(filtered_df)} filas")
        
        # Crear una copia para evitar SettingWithCopyWarning
        filtered_df = filtered_df.copy()
        
        # Añadir columna de fuente
        filtered_df['Source'] = 'FDA'
        
        return filtered_df
    
    except Exception as e:
        logger.error(f"Error al filtrar datos de FDA: {e}")
        return pd.DataFrame()

def filter_rasff_alerts(file_path):
    """
    Filtra alertas de RASFF relacionadas con las categorías objetivo.
    
    Args:
        file_path (str): Ruta al archivo CSV de alertas de RASFF.
        
    Returns:
        pandas.DataFrame: DataFrame con las alertas filtradas.
    """
    try:
        # Usar error_bad_lines=False (pandas < 1.3.0) o on_bad_lines='skip' (pandas >= 1.3.0)
        try:
            # Para pandas >= 1.3.0
            df = pd.read_csv(file_path, on_bad_lines='skip')
        except TypeError:
            # Para pandas < 1.3.0
            df = pd.read_csv(file_path, error_bad_lines=False)
            
        logger.info(f"Leyendo datos de RASFF desde {file_path}: {len(df)} filas")
        
        # Filtrar por categorías objetivo
        filtered_df = df[df.apply(lambda row: is_target_product(
            product_type=str(row.get('category', '')),
            product_description=str(row.get('subject', '')),
            source="RASFF"
        ), axis=1)]
        
        logger.info(f"Datos de RASFF filtrados: {len(filtered_df)} filas")
        
        # Crear una copia para evitar SettingWithCopyWarning
        filtered_df = filtered_df.copy()
        
        # Añadir columna de fuente
        filtered_df['Source'] = 'RASFF'
        
        return filtered_df
    
    except Exception as e:
        logger.error(f"Error al filtrar datos de RASFF: {e}")
        return pd.DataFrame()

def map_to_unified_schema(fda_df, rasff_df):
    """
    Mapea los DataFrames a un esquema unificado.
    
    Args:
        fda_df (pandas.DataFrame): DataFrame con datos de FDA.
        rasff_df (pandas.DataFrame): DataFrame con datos de RASFF.
        
    Returns:
        pandas.DataFrame: DataFrame con esquema unificado.
    """
    # Crear esquema unificado para FDA
    if not fda_df.empty:
        unified_fda = pd.DataFrame({
            'alert_id': fda_df.apply(lambda row: f"FDA-{row.name}", axis=1),
            'date': fda_df['Date'],
            'product_name': fda_df.apply(lambda row: f"{row['Brand Name(s)']} - {row['Product Description']}" 
                                       if pd.notna(row['Brand Name(s)']) and row['Brand Name(s)'] else row['Product Description'], axis=1),
            'product_type': fda_df['Product Type'],
            'hazard_type': fda_df['Recall Reason Description'],
            'company': fda_df['Company Name'],
            'country_origin': 'United States',
            'country_notification': 'United States',
            'source_database': 'FDA',
            'source_id': fda_df.apply(lambda row: f"FDA-{row.name}", axis=1),
            'details': fda_df['Excerpt'],
            'original_data': fda_df.apply(lambda x: x.to_json(), axis=1)
        })
    else:
        unified_fda = pd.DataFrame()
    
    # Crear esquema unificado para RASFF
    if not rasff_df.empty:
        # Verificar que todas las columnas necesarias existen
        required_cols = ['reference', 'date', 'subject', 'category', 'hazards', 
                        'operator', 'origin', 'notifying_country', 
                        'classification', 'forAttention', 'forFollowUp']
        
        # Crear columnas faltantes con valores vacíos
        for col in required_cols:
            if col not in rasff_df.columns:
                rasff_df[col] = ""
        
        unified_rasff = pd.DataFrame({
            'alert_id': rasff_df['reference'].apply(lambda x: f"RASFF-{x}"),
            'date': rasff_df['date'].apply(lambda x: convert_rasff_date(x) if pd.notna(x) else x),
            'product_name': rasff_df['subject'],
            'product_type': rasff_df['category'],
            'hazard_type': rasff_df['hazards'],
            'company': rasff_df['operator'],
            'country_origin': rasff_df['origin'],
            'country_notification': rasff_df['notifying_country'],
            'source_database': 'RASFF',
            'source_id': rasff_df['reference'],
            'details': rasff_df.apply(lambda row: f"Classification: {row['classification']} | For Attention: {row['forAttention']} | For Follow-Up: {row['forFollowUp']}", axis=1),
            'original_data': rasff_df.apply(lambda x: {col: x[col] for col in rasff_df.columns if pd.notna(x[col])}, axis=1).apply(lambda x: str(x))
        })
    else:
        unified_rasff = pd.DataFrame()
    
    # Combinar los DataFrames
    unified_df = pd.concat([unified_fda, unified_rasff], ignore_index=True)
    
    if unified_df.empty:
        return unified_df
    
    # Clasificar en categorías objetivo
    def categorize_product(row):
        product_type = str(row['product_type']).lower() if pd.notna(row['product_type']) else ""
        product_name = str(row['product_name']).lower() if pd.notna(row['product_name']) else ""
        
        for category_id, category_info in TARGET_CATEGORIES.items():
            for keyword in category_info['keywords']:
                if keyword.lower() in product_type or keyword.lower() in product_name:
                    return category_id
        
        # Mapeos específicos para FDA y RASFF
        if row['source_database'] == 'FDA' and row['product_type'] in FDA_CATEGORY_MAPPING:
            return FDA_CATEGORY_MAPPING[row['product_type']]
        
        if row['source_database'] == 'RASFF' and row['product_type'] in RASFF_CATEGORY_MAPPING:
            return RASFF_CATEGORY_MAPPING[row['product_type']]
        
        return 'other'
    
    unified_df['category'] = unified_df.apply(categorize_product, axis=1)
    
    return unified_df

def convert_rasff_date(date_str):
    """
    Convierte formato de fecha de RASFF a formato estándar.
    
    Args:
        date_str (str): Fecha en formato RASFF (DD-MM-YYYY HH:MM:SS).
        
    Returns:
        str: Fecha en formato MM/DD/YYYY.
    """
    try:
        # Verificar si date_str es un valor válido
        if not date_str or not isinstance(date_str, str):
            return ""
            
        # Formato típico RASFF: "DD-MM-YYYY HH:MM:SS"
        parts = date_str.split(' ')[0].split('-')
        if len(parts) != 3:
            return date_str
        
        try:
            day = int(parts[0])
            month = int(parts[1])
            year = int(parts[2])
        except ValueError:
            return date_str
        
        # Formatear como MM/DD/YYYY
        return f"{month:02d}/{day:02d}/{year}"
    except Exception as e:
        logger.error(f"Error al convertir fecha RASFF: {e}")
        return date_str

def process_and_filter_data():
    """
    Procesa y filtra los datos de alertas alimentarias más recientes.
    
    Returns:
        str: Ruta al archivo procesado.
    """
    # Buscar en múltiples ubicaciones posibles
    data_locations = [
        SCRAPS_DIR,  # Buscar primero en data/scraps/
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"),  # Buscar en data/
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "data"),  # Buscar en ../data/
    ]
    
    fda_file_path = None
    rasff_file_path = None
    
    # Buscar archivos en las ubicaciones
    for location in data_locations:
        if not os.path.exists(location):
            continue
            
        logger.info(f"Buscando archivos en: {location}")
        
        # Buscar archivos FDA
        fda_files = []
        for f in os.listdir(location):
            if "fda_alerts" in f.lower() and f.endswith('.csv'):
                fda_files.append(os.path.join(location, f))
        
        if fda_files and not fda_file_path:
            fda_files.sort(key=os.path.getmtime, reverse=True)
            fda_file_path = fda_files[0]
            logger.info(f"Encontrado archivo FDA en: {fda_file_path}")
        
        # Buscar archivos RASFF
        rasff_files = []
        for f in os.listdir(location):
            if ("rasff_window" in f.lower() or "RASFF_window" in f.lower()) and f.endswith('.csv'):
                rasff_files.append(os.path.join(location, f))
        
        if rasff_files and not rasff_file_path:
            rasff_files.sort(key=os.path.getmtime, reverse=True)
            rasff_file_path = rasff_files[0]
            logger.info(f"Encontrado archivo RASFF en: {rasff_file_path}")
    
    if not fda_file_path and not rasff_file_path:
        logger.warning("No se encontraron archivos para procesar")
        return None
    
    # Filtrar datos
    fda_df = pd.DataFrame()
    rasff_df = pd.DataFrame()
    
    if fda_file_path:
        fda_df = filter_fda_alerts(fda_file_path)
    
    if rasff_file_path:
        rasff_df = filter_rasff_alerts(rasff_file_path)
    
    # Unificar datos
    unified_df = map_to_unified_schema(fda_df, rasff_df)
    
    if unified_df.empty:
        logger.warning("No se encontraron datos que cumplan con los criterios de filtrado")
        return None
    
    # Asegurarse de que el directorio de procesados existe
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    # Guardar datos procesados
    output_path = os.path.join(PROCESSED_DIR, PROCESSED_BAKERY_FILENAME)
    unified_df.to_csv(output_path, index=False)
    logger.info(f"Datos procesados guardados en {output_path}: {len(unified_df)} filas")
    
    return output_path

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Procesar datos
    process_and_filter_data()