library(tidyverse); library(arrow); library(skimr); library(naniar)
library(rstatix); library(corrplot)

wine <- read_parquet("../data/processed/wine_clean.parquet")

skim(wine)                         # descriptivas generales
wine |> summarise(across(c(points, price),
        list(media=mean, mediana=median, sd=sd, asim=moments::skewness), na.rm=TRUE))

# Distribuciones
ggplot(wine, aes(points)) + geom_histogram(binwidth=1)
ggplot(wine, aes(price)) + geom_histogram(bins=60) + scale_x_log10()

# Precio vs. puntos
wine |> filter(!is.na(price)) |>
  ggplot(aes(points, price)) + geom_boxplot(aes(group=points)) + scale_y_log10()
wine |> cor_test(points, log_price, method="spearman")

# Top países y variedades
wine |> count(country, sort=TRUE) |> slice_head(n=10)
wine |> group_by(variety_top) |>
  summarise(n=n(), pts=mean(points), pr=median(price, na.rm=TRUE)) |> arrange(desc(pts))

# Longitud de descripción vs puntos
wine |> ggplot(aes(desc_len, points)) + geom_bin2d()

# ¿Difieren los puntos entre países (top 8)?
top8 <- wine |> count(country, sort=TRUE) |> slice_head(n=8) |> pull(country)
d <- wine |> filter(country %in% top8)
d |> kruskal_test(points ~ country)
d |> kruskal_effsize(points ~ country)          # tamaño de efecto
d |> dunn_test(points ~ country, p.adjust.method="bonferroni")

# Chi-cuadrado: segmento de precio vs banda de puntos
chisq.test(table(wine$price_segment, wine$points_band))

# Regresión lineal simple como análisis inferencial (no predictivo)
lm(points ~ log_price, data = wine) |> summary()