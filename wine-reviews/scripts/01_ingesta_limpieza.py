import pandas as pd, numpy as np

#wine-reviews/data/raw/winemag-data_first150k.csv
df = pd.read_csv('data/raw/winemag-data_first150k.csv')
n0 = len(df)

# Elimincar columna índice
df = df.drop(columns=['Unnamed: 0'])

# 2. Control de duplicados
print(f"Número de duplicados: {df.duplicated().sum()}")
df = df.drop_duplicates().reset_index(drop=True)

print("Duplicados por descripción:", df.duplicated(subset=['description']).sum())
df.drop_duplicates(subset=['description'])

# 3. Normalizar texto
for c in ["country","province","region_1","region_2","variety","winery","designation"]:
    df[c] = df[c].str.strip()

# 4. Faltanates
df["has_prices"] = df["price"].notna()
df["designation"] = df["designation"].fillna("Sin designación")
df["region_1"] = df["region_1"].fillna("Desconocida")
df = df.drop(columns=["region_2"])

# 5. Outliers de precio (Método IQR sobre log)
df["log_price"] = np.log(df["price"])
q1, q3 = df["log_price"].quantile([.25, .75]); iqr = q3-q1
df["price_outlier"] = (df["log_price"] < q1-1.5*iqr) | (df["log_price"] > q3+1.5*iqr)


# 6. Variables derivadas
df["prices_segment"] = pd.cut(df["price"], [0,15,30,60,np.inf],
                              labels=["Económico","Medio","Premium","Lujo" ])
df["points_band"] = pd.cut(df["points"], [79,84,89,94,100],
                           labels=["80-84","85-89","90-94","95-100"])
df["desc_len"] = df["description"].str.split().str.len()
df["pts_per_usd"] = df["points"]/df["price"]
df["value_idx"] = df["points"] - df.groupby("country")["points"].transform("mean") \
                  - 0*df["price"]

# 7. Agrupar categorías raras (para gráficos y dashboard)
top = df["variety"].value_counts().nlargest(20).index
df["variety_top"] = np.where(df["variety"].isin(top), df["variety"], "Otras")

assert df["points"].between(80,100).all()
assert (df["price"].dropna() > 0).all()
print(f"Filas: {n0} -> {len(df)} ({n0-len(df)} eliminadas)")
df.to_parquet("data/processed/wine_clean.parquet")
df.to_csv("data/processed/wine_clean.csv", index=False)  # para Power BI