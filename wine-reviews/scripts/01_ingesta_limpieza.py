"""
01_ingesta_limpieza.py
Ingesta, limpieza, ingeniería de variables y features de texto.
Ejecutar desde la raíz del proyecto:  python scripts/01_ingesta_limpieza.py
Salidas en data/processed/
"""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS

RAW = Path("data/raw/winemag-data_first150k.csv")
OUT = Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)

log = []  # bitácora de decisiones de limpieza


def registrar(paso, antes, despues, nota=""):
    log.append({"paso": paso, "filas_antes": antes, "filas_despues": despues,
                "afectadas": antes - despues, "nota": nota})


# ------------------------------------------------------------------ 1. Ingesta
df = pd.read_csv(RAW)
n0 = len(df)
assert n0 > 5000, "El dataset debe tener >= 5.000 registros"

# ------------------------------------------------------------ 2. Limpieza
df = df.drop(columns=["Unnamed: 0"])  # índice heredado del CSV
registrar("Eliminar columna índice", len(df), len(df), "Unnamed: 0 no aporta información")

n = len(df)
df = df.drop_duplicates()
registrar("Duplicados exactos", n, len(df), "Todas las columnas iguales (sin índice)")

n = len(df)
df = df.drop_duplicates(subset="description")
registrar("Duplicados por descripción", n, len(df),
          "Misma reseña repetida: no son vinos distintos")

# Normalizar texto
cols_txt = ["country", "province", "region_1", "region_2", "variety", "winery", "designation"]
for c in cols_txt:
    df[c] = df[c].astype("string").str.strip()

# Faltantes
df["has_price"] = df["price"].notna()
df["designation"] = df["designation"].fillna("Sin designación")
df["region_1"] = df["region_1"].fillna("Desconocida")
df = df.drop(columns=["region_2"])  # ~60 % nulos
df = df.reset_index(drop=True)
# price NO se imputa: imputar sesgaría la relación precio-puntos

# --------------------------------------------------- 3. Variables derivadas
df["log_price"] = np.log(df["price"])
q1, q3 = df["log_price"].quantile([.25, .75])
iqr = q3 - q1
df["price_outlier"] = (df["log_price"] < q1 - 1.5 * iqr) | (df["log_price"] > q3 + 1.5 * iqr)

df["price_segment"] = pd.cut(df["price"], [0, 15, 30, 60, np.inf],
                             labels=["Económico (<=15)", "Medio (15-30)", "Premium (30-60)", "Lujo (>60)"])
df["points_band"] = pd.cut(df["points"], [79, 84, 89, 94, 100],
                           labels=["80-84", "85-89", "90-94", "95-100"])
df["desc_len"] = df["description"].str.split().str.len()

# Índice de valor: puntos por encima/debajo de lo esperado para su precio
m = df["price"].notna()
b, a = np.polyfit(df.loc[m, "log_price"], df.loc[m, "points"], 1)
df["value_score"] = np.where(m, df["points"] - (a + b * df["log_price"]), np.nan)

top_var = df["variety"].value_counts().nlargest(20).index
df["variety_top"] = np.where(df["variety"].isin(top_var), df["variety"], "Otras")

# Comprobaciones
assert df["points"].between(80, 100).all()
assert (df["price"].dropna() > 0).all()
assert df["description"].is_unique
print(f"Filas: {n0} -> {len(df)} ({n0 - len(df)} eliminadas)")

# ---------------------------------------------------- 4. Features de texto
custom_sw = {"wine", "wines", "flavors", "flavor", "drink", "finish", "palate",
             "notes", "note", "aromas", "aroma", "nose", "shows", "offers", "made",
             "bottling", "blend", "tastes", "hint", "hints", "touch", "like"}
tfidf = TfidfVectorizer(stop_words=list(ENGLISH_STOP_WORDS | custom_sw),
                        max_features=3000, ngram_range=(1, 2), min_df=30,
                        token_pattern=r"(?u)\b[a-zA-Z]{3,}\b")
X = tfidf.fit_transform(df["description"])
terms = np.array(tfidf.get_feature_names_out())
overall = np.asarray(X.mean(axis=0)).ravel()

rows = []
for band in df["points_band"].cat.categories:
    mask = (df["points_band"] == band).to_numpy()
    mean_band = np.asarray(X[mask].mean(axis=0)).ravel()
    diff = mean_band - overall  # términos distintivos de la banda
    for i in diff.argsort()[::-1][:25]:
        rows.append({"points_band": band, "term": terms[i], "score": round(float(diff[i]), 5)})
pd.DataFrame(rows).to_csv(OUT / "terms_by_band.csv", index=False)

# ------------------------------------------------------ 5. Tablas resumen
by_country = (df.groupby("country")
              .agg(n=("points", "size"), avg_points=("points", "mean"),
                   median_price=("price", "median"), avg_value=("value_score", "mean"))
              .round(2).reset_index().sort_values("n", ascending=False))
by_country.to_csv(OUT / "country_summary.csv", index=False)

by_variety = (df.groupby("variety")
              .agg(n=("points", "size"), avg_points=("points", "mean"),
                   median_price=("price", "median"), avg_value=("value_score", "mean"))
              .round(2).reset_index().query("n >= 100").sort_values("avg_value", ascending=False))
by_variety.to_csv(OUT / "variety_summary.csv", index=False)

# ------------------------------------------------------------- 6. Salidas
df.to_csv(OUT / "wine_clean.csv", index=False)
pd.DataFrame(log).to_csv(OUT / "cleaning_log.csv", index=False)
print(pd.DataFrame(log).to_string(index=False))
