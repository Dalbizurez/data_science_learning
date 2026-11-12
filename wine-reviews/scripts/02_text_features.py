from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd, numpy as np

df = pd.read_csv('data/raw/winemag-data_first150k.csv')

tfidf = TfidfVectorizer(stop_words="english", max_features=3000, ngram_range=(1,2), min_df=20)
X = tfidf.fit_transform(df["description"])
terms = np.array(tfidf.get_feature_names_out())

def top_terms(mask, n=15):
    mask = mask.to_numpy()

    m = np.asarray(X[mask].mean(axis=0)).ravel()
    return terms[m.argsort()[::-1][:n]]
print(top_terms(df.points >= 95)); print(top_terms(df.points <= 83))