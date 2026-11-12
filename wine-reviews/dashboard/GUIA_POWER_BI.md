# Guía completa: dashboard de vinos en Power BI Desktop

No puedo generar un archivo `.pbix` desde aquí (es un formato binario propio de Power BI Desktop), así que esta guía te lleva paso a paso. Tiempo estimado: 1,5 a 2 horas.

Archivos a usar (carpeta `data/processed/`): `wine_clean.csv` (tabla principal), `terms_by_band.csv`, `country_summary.csv`, `variety_summary.csv`.

---

## 1. Importar los datos

1. **Inicio > Obtener datos > Texto o CSV** y elige `wine_clean.csv` > **Transformar datos**.
2. En Power Query, verifica los tipos:
   - Texto: `country, province, region_1, variety, winery, designation, description, price_segment, points_band, variety_top`
   - Número entero: `points, desc_len`
   - Número decimal: `price, log_price, value_score`
   - Verdadero/Falso: `has_price, price_outlier`
3. Quita la columna `description` del modelo si Power BI va lento (pesa mucho y no la usarás en visuales). Si quieres una tabla de detalle, déjala.
4. Renombra la consulta a `Vinos`. **Cerrar y aplicar**.
5. Repite con `terms_by_band.csv` (consulta `Terminos`). Las otras dos tablas son opcionales; puedes calcular todo con DAX desde `Vinos`.

**Comprobación:** en la vista de tabla, `Vinos` debe tener **97.821 filas**. `price` debe tener unos 89.108 valores no vacíos.

---

## 2. Modelo de datos

- Ve a la **Vista de modelo**. `Terminos` no se relaciona con `Vinos` por clave directa: crea una tabla de bandas para poder filtrar ambas.
- **Modelado > Nueva tabla**:

```DAX
Bandas = DISTINCT(SELECTCOLUMNS(Vinos, "points_band", Vinos[points_band]))
```
- Crea relaciones **Bandas[points_band] 1 → * Vinos[points_band]** y **Bandas[points_band] 1 → * Terminos[points_band]** (dirección de filtro: una sola).

**Ordenar categorías correctamente** (por defecto Power BI ordena alfabéticamente):

1. En `Vinos`, **Nueva columna**:
```DAX
Orden Segmento =
SWITCH(Vinos[price_segment],
    "Económico (<=15)", 1,
    "Medio (15-30)", 2,
    "Premium (30-60)", 3,
    "Lujo (>60)", 4)
```
2. Selecciona `price_segment` > **Herramientas de columna > Ordenar por columna > Orden Segmento**.
3. `points_band` ya ordena bien alfabéticamente (80-84, 85-89, 90-94, 95-100).

Establece **categorías de datos**: `country` > Herramientas de columna > Categoría de datos > **País o región** (para el mapa).

---

## 3. Medidas DAX

**Modelado > Nueva medida** (crea una tabla vacía `_Medidas` para guardarlas: *Introducir datos*, una columna vacía).

```DAX
N Reseñas = COUNTROWS(Vinos)

Puntos Promedio = AVERAGE(Vinos[points])

Precio Mediano = MEDIAN(Vinos[price])

Precio Promedio = AVERAGE(Vinos[price])

Valor Promedio = AVERAGE(Vinos[value_score])

% Con Precio = DIVIDE(CALCULATE([N Reseñas], Vinos[has_price] = TRUE()), [N Reseñas])

N Países = DISTINCTCOUNT(Vinos[country])

N Variedades = DISTINCTCOUNT(Vinos[variety])

% Reseñas 90+ =
DIVIDE(CALCULATE([N Reseñas], Vinos[points] >= 90), [N Reseñas])

Puntos vs Global =
[Puntos Promedio] - CALCULATE(AVERAGE(Vinos[points]), ALL(Vinos))

Ranking Valor =
RANKX(ALL(Vinos[variety]), [Valor Promedio], , DESC, Dense)

Titulo Dinamico =
"Reseñas: " & FORMAT([N Reseñas], "#,0") &
" | Puntos prom.: " & FORMAT([Puntos Promedio], "0.0") &
" | Precio mediano: " & FORMAT([Precio Mediano], "$#,0")
```

**Comprobación:** con todos los filtros limpios, `N Reseñas` = 97.821, `Puntos Promedio` ≈ 87,96 y `Precio Mediano` = 25. Compáralos con el informe Quarto (deben coincidir).

---

## 4. Páginas del dashboard

Diseño general: lienzo 16:9. Paleta sugerida: vino `#722F37`, dorado `#C9A227`, crema `#F5EFE6`, gris `#4A4A4A`. Fuente Segoe UI. Fondo crema en **Formato de página > Fondo de lienzo**.

### Página 1: Resumen

| Elemento | Configuración |
|---|---|
| 4 tarjetas (KPI) | `N Reseñas`, `Puntos Promedio`, `Precio Mediano`, `N Países` |
| Mapa de relleno (*Filled map*) | Ubicación: `country`; Saturación de color: `Puntos Promedio`; Tooltip: `N Reseñas`, `Precio Mediano` |
| Gráfico de barras (top 10 países) | Eje: `country`; Valor: `N Reseñas`. Filtro visual: **N superior 10 por `N Reseñas`** |
| Columnas agrupadas | Eje: `points_band`; Valor: `N Reseñas` (distribución de calidad) |
| Título | Usa `Titulo Dinamico` (Formato > Título > fx) |

Respondes: preguntas 1 y contexto general.

### Página 2: Precio vs. puntuación

| Elemento | Configuración |
|---|---|
| Dispersión | Eje X: `Precio Mediano`; Eje Y: `Puntos Promedio`; Detalles: `country`; Tamaño: `N Reseñas`. Filtro visual: `N Reseñas` ≥ 500. Eje X en escala **logarítmica** (Formato > Eje X > Escala > Log) |
| Barras apiladas 100 % | Eje: `price_segment`; Leyenda: `points_band`; Valor: `N Reseñas` |
| Línea | Eje: `points` (como categoría); Valor: `Precio Mediano`. Muestra el crecimiento exponencial del precio |
| Tarjeta | `% Reseñas 90+` |

Responde la pregunta 2. Añade un cuadro de texto: "La relación es positiva pero con rendimientos decrecientes".

### Página 3: Calidad-precio por variedad

| Elemento | Configuración |
|---|---|
| Barras horizontales | Eje: `variety`; Valor: `Valor Promedio`. Filtros visuales: `N Reseñas` ≥ 100, **N superior 15 por `Valor Promedio`**. Ordena descendente |
| Tabla | Columnas: `variety`, `N Reseñas`, `Puntos Promedio`, `Precio Mediano`, `Valor Promedio`. Formato condicional (barras de datos) en `Valor Promedio` |
| Árbol de descomposición (opcional) | Analizar: `Valor Promedio`; Explicar por: `country`, `province`, `variety` |

Responde la pregunta 3. `Valor Promedio` > 0 significa más puntos de los esperados para su precio.

### Página 4: Descriptores de sabor

| Elemento | Configuración |
|---|---|
| Barras horizontales | Eje: `Terminos[term]`; Valor: suma de `Terminos[score]`; filtro visual: N superior 10 por `score` |
| Segmentador | Campo `Bandas[points_band]`, estilo **botones** (mosaico) |
| Nube de palabras (opcional) | Visual de AppSource "Word Cloud": Categoría `term`, Valores `score` |

Al elegir una banda, el gráfico muestra los términos distintivos de esa banda. Responde la pregunta 4.

### Página 5: Explorador (detalle)

Tabla con `winery`, `designation`, `country`, `variety`, `points`, `price`, `description`. Ordena por `points` descendente. Útil para buscar un vino concreto.

---

## 5. Filtros y segmentaciones

Crea los segmentadores en la Página 1 y **sincronízalos** en todas las páginas: **Vista > Sincronizar segmentaciones** > marca las páginas donde deben verse y aplicarse.

| Segmentador | Campo | Estilo |
|---|---|---|
| País | `country` | Lista desplegable con búsqueda |
| Variedad | `variety_top` | Lista desplegable |
| Segmento de precio | `price_segment` | Botones |
| Banda de puntos | `points_band` | Botones |
| Rango de precio | `price` | Entre (control deslizante) |
| Solo con precio | `has_price` | Lista |

**Interacciones:** selecciona un visual > **Formato > Editar interacciones** para evitar que algunos visuales (p. ej. las tarjetas globales) se filtren si no corresponde.

---

## 6. Elementos de usabilidad (puntúan en la rúbrica)

1. **Navegador de páginas:** Insertar > Botones > Navegador > Navegador de páginas.
2. **Botón "Restablecer filtros":** crea un marcador con todos los filtros limpios (Vista > Marcadores) y asígnalo como acción de un botón.
3. **Información sobre herramientas personalizada:** crea una página "Tooltip" (Formato > Tamaño de página > Información sobre herramientas) con `N Reseñas`, `Puntos Promedio` y `Precio Mediano`, y úsala en el mapa y la dispersión.
4. **Drill-through:** en una página "Detalle país" arrastra `country` a **Pasar a través**; clic derecho en un país > *Obtener detalles*.
5. **Títulos descriptivos** en cada visual y una **nota de fuente** al pie: "Fuente: WineEnthusiast vía Kaggle. Solo vinos con 80+ puntos".
6. **Texto alternativo** en los visuales principales (accesibilidad).

---

## 7. Comprobaciones antes de entregar

- [ ] `N Reseñas` total = 97.821 y coincide con el informe.
- [ ] Los segmentadores sincronizados afectan a todas las páginas.
- [ ] El mapa reconoce todos los países (revisa "United Kingdom", "US" puede aparecer como no reconocido: si falla, crea una columna `country_map` con `SWITCH(Vinos[country], "US", "United States", Vinos[country])`).
- [ ] El orden de `price_segment` es Económico → Lujo.
- [ ] Sin visuales con advertencias o filas "(En blanco)" inesperadas (los vinos sin precio aparecen como en blanco en visuales de precio: es normal; filtra `has_price` si molesta).
- [ ] Guarda como `dashboard/vinos.pbix` con los datos incluidos (no uses "Guardar sin datos").

## 8. Alternativa sin Power BI Desktop

Si no tienes Windows/Power BI Desktop: **Looker Studio** (gratis, web) acepta los mismos CSV (súbelos a Google Sheets o usa el conector de archivos). Las medidas se reemplazan por campos calculados (`AVG(points)`, `MEDIAN` no existe: usa `PERCENTILE`/aproxima con promedio). También sirve **Shiny** o **Dash** si prefieres código.
