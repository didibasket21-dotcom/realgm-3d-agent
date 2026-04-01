import pandas as pd

data_path = "data/Arkusz-2-Tabela 1.csv"

df = pd.read_csv(data_path, sep=";", header=1)
print("KOLUMNY:", list(df.columns))
print("PIERWSZE 3 WIERSZE:")
print(df.head(3).to_string())
print("KSZTAT:", df.shape)
