"""
Definición de categorías de productos para filtrado.
"""

# Categorías objetivo para el filtrado
TARGET_CATEGORIES = {
    "bakery": {
        "name": "Productos de panadería y cereales",
        "keywords": [
            "bakery", "panadería", "bread", "pan", "pastry", "pastel", "cake", 
            "cookie", "galleta", "flour", "harina", "wheat", "trigo", "cereal",
            "snack", "biscuit", "pasta", "macaroni", "noodle", "fideo", "pizza",
            "dough", "masa", "toast", "tostada", "croissant", "bagel", "muffin",
            "roll", "bun", "bollos", "brioche"
        ]
    },
    "dairy": {
        "name": "Productos lácteos",
        "keywords": [
            "dairy", "lácteo", "milk", "leche", "cheese", "queso", "yogurt", "yoghourt",
            "cream", "crema", "butter", "mantequilla", "margarine", "whey", "suero",
            "lactose", "lactosa", "curd", "cuajada", "kefir", "ghee"
        ]
    },
    "eggs": {
        "name": "Huevos y derivados",
        "keywords": [
            "egg", "huevo", "albumin", "albúmina", "yolk", "yema"
        ]
    },
    "chocolate": {
        "name": "Chocolate y cacao",
        "keywords": [
            "chocolate", "cocoa", "cacao", "praline", "truffle", "trufa", "brownie",
            "fudge", "confectionery", "confitería"
        ]
    },
    "sugar": {
        "name": "Azúcares y edulcorantes",
        "keywords": [
            "sugar", "azúcar", "sweetener", "edulcorante", "honey", "miel", "syrup", 
            "sirope", "molasses", "melaza", "saccharin", "sacarina", "maltose", "maltosa",
            "fructose", "fructosa", "glucose", "glucosa", "dextrose", "dextrosa"
        ]
    },
    "grains": {
        "name": "Granos y semillas",
        "keywords": [
            "grain", "grano", "seed", "semilla", "corn", "maíz", "rice", "arroz", 
            "oat", "avena", "barley", "cebada", "rye", "centeno", "millet", "mijo",
            "quinoa", "amaranth", "amaranto", "buckwheat", "alforfón", "spelt", "espelta"
        ]
    }
}

# Mapeo de categorías de FDA a categorías objetivo
FDA_CATEGORY_MAPPING = {
    "Food & Beverages, Allergens, Bakery": "bakery",
    "Food & Beverages, Allergens, Cereal": "bakery",
    "Food & Beverages, Allergens, Confectionery": "chocolate",
    "Food & Beverages, Allergens, Dairy": "dairy",
    "Food & Beverages, Allergens, Snack Food": "bakery",
    "Food & Beverages, Grain Based Products": "bakery"
}

# Mapeo de categorías de RASFF a categorías objetivo
RASFF_CATEGORY_MAPPING = {
    "cereals and bakery products": "bakery",
    "milk and milk products": "dairy",
    "eggs and egg products": "eggs",
    "cocoa and cocoa preparations, coffee and tea": "chocolate",
    "nuts, nut products and seeds": "grains",
    "confectionery": "chocolate"
}

def is_target_product(product_type="", product_description="", source=""):
    """
    Evalúa si un producto pertenece a las categorías objetivo basándose en su tipo y descripción.
    
    Args:
        product_type (str): Tipo o categoría del producto.
        product_description (str): Descripción del producto.
        source (str): Fuente de datos (FDA o RASFF).
        
    Returns:
        bool: True si el producto pertenece a las categorías objetivo, False en caso contrario.
    """
    # Normalizar texto a minúsculas
    product_type_lower = product_type.lower() if product_type else ""
    product_description_lower = product_description.lower() if product_description else ""
    
    # Verificar mapeos directos según la fuente
    if source == "FDA" and product_type in FDA_CATEGORY_MAPPING:
        return True
    
    if source == "RASFF" and product_type in RASFF_CATEGORY_MAPPING:
        return True
    
    # Buscar palabras clave en el tipo y descripción del producto
    for category in TARGET_CATEGORIES.values():
        for keyword in category["keywords"]:
            if (keyword.lower() in product_type_lower or 
                keyword.lower() in product_description_lower):
                return True
    
    return False