# Reseñas de vinos: calidad, precio y descriptores de sabor

Proyecto final individual (R + Python + Quarto + Power BI).

**Autor:** _tu nombre_ — responsable de todas las tareas (datos, análisis, informe, dashboard, presentación).

## Fuente de datos
Wine Reviews (WineEnthusiast), Kaggle: https://www.kaggle.com/datasets/zynicide/wine-reviews
Archivo `winemag-data_first150k.csv` incluido en `data/raw/`. Licencia: verificar en Kaggle (CC BY-NC-SA 4.0); uso académico.

## Estructura
```
data/raw/            dato original
data/processed/      salidas de limpieza (CSV para Power BI)
scripts/             01_ingesta_limpieza.py, 00_instalar_r.R
report/informe.qmd   informe reproducible (R + Python)
dashboard/           guía y archivo .pbix
```

## Reproducción
1. Python 3.10+: `python -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
2. R 4.3+: `Rscript scripts/00_instalar_r.R`
3. Instalar Quarto: https://quarto.org
4. Limpieza: `python scripts/01_ingesta_limpieza.py`
5. Informe: `cd report && quarto render informe.qmd`
   (si usas el entorno virtual, descomenta `use_virtualenv("venv")` en el chunk `setup-r`)
6. Dashboard: seguir `dashboard/GUIA_POWER_BI.md`

## División de tareas
Trabajo individual: el autor realizó todas las etapas.
