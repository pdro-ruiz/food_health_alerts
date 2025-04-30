# Sistema de Alertas Alimentarias

Este proyecto automatiza la recopilación, procesamiento, análisis y reporte de alertas alimentarias a partir de múltiples fuentes internacionales. Está especialmente orientado al seguimiento de productos de panadería, lácteos, cereales y otras categorías clave de la industria alimentaria.

## Características

- **Scraping Automatizado**: Obtención de alertas desde fuentes como FDA y RASFF.
- **Procesamiento de Datos**: Limpieza, normalización y clasificación del riesgo.
- **Dataset Consolidado**: Generación y mantenimiento de un dataset estructurado.
- **Generación de Informes**:
  - **Excel** con estadísticas y hojas por categoría de producto.
  - **Presentación Ejecutiva (PDF)** con hallazgos clave y visualizaciones.
  - **Exportación del Notebook (PDF)** para trazabilidad y análisis reproducible.
- **Diseño Escalable**: Preparado para incorporar nuevas fuentes y ampliar análisis.

## Estructura del Proyecto

```
food_alerts/
│
├── config/                      
│   ├── settings.py
│   ├── logging_config.py
│   └── product_categories.py
│
├── data/                        
│   ├── raw/
│   ├── scraps/
│   ├── processed/
│   └── final/
│
├── logs/                        
│
├── scrapers/                    
│   ├── fda_scraper.py
│   ├── rasff_scraper.py
│   └── base_scraper.py
│
├── processors/                  
│   ├── data_cleaner.py
│   ├── data_filter.py
│   └── data_merger.py
│
├── utils/                       
│   ├── date_utils.py
│   └── file_utils.py
│
├── reports/                     # Informes generados
│   ├── excel/
│   ├── pdf/
│   └── executive/
│
├── notebooks/                   # Jupyter notebooks de análisis
│
├── main.py                      # Orquestador principal del pipeline
├── report_generator.py          # Generación automática de informes
├── requirements.txt             
└── README.md                    
```

## Instalación

```bash
git clone https://github.com/pdro-ruiz/food_health_alerts.git
cd food_health_alerts

python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Uso

### Pipeline completo (scraping + procesamiento)

```bash
python main.py --scrape
```

### Solo procesamiento (si ya tienes datos en `data/scraps/`)

```bash
python main.py
```

### Ejecutar scrapers específicos

```bash
python main.py --scrape --scraper fda
python main.py --scrape --scraper rasff
```

### Generar informes

```bash
python report_generator.py                     # Genera todos los informes
python report_generator.py --type excel        # Solo Excel
python report_generator.py --type pdf          # Solo notebook como PDF
python report_generator.py --type executive    # Solo presentación ejecutiva
```

También puedes usar los argumentos `--data`, `--output` y `--notebook` para personalizar rutas.

## Informes Generados

- 📊 **Excel** con resumen general, gráficas y hojas por categoría (`/reports/excel`)
- 🧾 **PDF del Notebook** con todo el análisis técnico reproducible (`/reports/pdf`)
- 🧠 **Resumen Ejecutivo en PDF** con insights clave para directivos (`/reports/executive`)

## Categorías Analizadas

- Productos de panadería y cereales
- Productos lácteos
- Huevos y derivados
- Chocolate y cacao
- Azúcares y edulcorantes
- Granos y semillas
