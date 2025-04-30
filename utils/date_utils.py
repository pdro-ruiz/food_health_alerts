"""
Utilidades para manejo de fechas.
"""
from datetime import datetime, timedelta
import re

def parse_date(date_str, formats=None):
    """
    Parsea una cadena de fecha a un objeto datetime.
    
    Args:
        date_str (str): Cadena de fecha a parsear.
        formats (list, optional): Lista de formatos a probar. Si es None, se usan formatos comunes.
        
    Returns:
        datetime: Objeto datetime si se pudo parsear, None en caso contrario.
    """
    if not date_str:
        return None
    
    # Si no se proporcionan formatos, usar estos por defecto
    if formats is None:
        formats = [
            '%m/%d/%Y',          # MM/DD/YYYY (FDA)
            '%d-%m-%Y %H:%M:%S',  # DD-MM-YYYY HH:MM:SS (RASFF)
            '%d-%m-%Y',           # DD-MM-YYYY (RASFF sin hora)
            '%Y-%m-%d',           # YYYY-MM-DD (ISO)
            '%Y/%m/%d',           # YYYY/MM/DD
            '%d/%m/%Y',           # DD/MM/YYYY
            '%b %d, %Y',          # Mmm DD, YYYY (e.g., Jan 01, 2023)
            '%B %d, %Y',          # Month DD, YYYY (e.g., January 01, 2023)
            '%d %b %Y',           # DD Mmm YYYY (e.g., 01 Jan 2023)
            '%d %B %Y'            # DD Month YYYY (e.g., 01 January 2023)
        ]
    
    # Intentar parsear con cada formato
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    
    # Si ningún formato funciona, intentar con expresiones regulares para casos especiales
    # Ejemplo: "4 days ago", "last week", etc.
    relative_date = parse_relative_date(date_str)
    if relative_date:
        return relative_date
    
    return None

def parse_relative_date(date_str):
    """
    Parsea fechas relativas como "1 day ago", "last week", etc.
    
    Args:
        date_str (str): Cadena de fecha relativa.
        
    Returns:
        datetime: Objeto datetime correspondiente, o None si no se puede parsear.
    """
    date_str = date_str.lower().strip()
    now = datetime.now()
    
    # Patrones para fechas relativas comunes
    patterns = [
        # "X days/weeks/months/years ago"
        (r'(\d+)\s+day[s]?\s+ago', lambda m: now - timedelta(days=int(m.group(1)))),
        (r'(\d+)\s+week[s]?\s+ago', lambda m: now - timedelta(weeks=int(m.group(1)))),
        (r'(\d+)\s+month[s]?\s+ago', lambda m: now - timedelta(days=int(m.group(1))*30)),
        (r'(\d+)\s+year[s]?\s+ago', lambda m: now - timedelta(days=int(m.group(1))*365)),
        
        # "yesterday", "last week", etc.
        (r'yesterday', lambda m: now - timedelta(days=1)),
        (r'last\s+week', lambda m: now - timedelta(weeks=1)),
        (r'last\s+month', lambda m: now - timedelta(days=30)),
        (r'last\s+year', lambda m: now - timedelta(days=365))
    ]
    
    # Probar cada patrón
    for pattern, date_func in patterns:
        match = re.search(pattern, date_str)
        if match:
            return date_func(match)
    
    return None

def format_date(date_obj, format_str='%m/%d/%Y'):
    """
    Formatea un objeto datetime como cadena.
    
    Args:
        date_obj (datetime): Objeto datetime a formatear.
        format_str (str, optional): Formato de salida. Por defecto, MM/DD/YYYY.
        
    Returns:
        str: Fecha formateada como cadena.
    """
    if not date_obj:
        return None
    
    return date_obj.strftime(format_str)

def get_date_range(start_date, end_date=None, days=None):
    """
    Obtiene un rango de fechas.
    
    Args:
        start_date (datetime): Fecha de inicio.
        end_date (datetime, optional): Fecha de fin.
        days (int, optional): Número de días a incluir desde start_date.
        
    Returns:
        list: Lista de objetos datetime en el rango.
    """
    if not start_date:
        return []
    
    if not end_date and days:
        end_date = start_date + timedelta(days=days)
    elif not end_date:
        end_date = datetime.now()
    
    # Asegurar que start_date sea anterior a end_date
    if start_date > end_date:
        start_date, end_date = end_date, start_date
    
    # Generar rango de fechas
    date_range = []
    current_date = start_date
    while current_date <= end_date:
        date_range.append(current_date)
        current_date += timedelta(days=1)
    
    return date_range

def convert_rasff_date(date_str):
    """
    Convierte formato de fecha de RASFF a formato estándar MM/DD/YYYY.
    
    Args:
        date_str (str): Fecha en formato RASFF (DD-MM-YYYY HH:MM:SS).
        
    Returns:
        str: Fecha en formato MM/DD/YYYY.
    """
    try:
        # Formato típico RASFF: "DD-MM-YYYY HH:MM:SS"
        parts = date_str.split(' ')[0].split('-')
        if len(parts) != 3:
            return date_str
        
        day = int(parts[0])
        month = int(parts[1])
        year = int(parts[2])
        
        # Formatear como MM/DD/YYYY
        return f"{month:02d}/{day:02d}/{year}"
    except Exception:
        return date_str