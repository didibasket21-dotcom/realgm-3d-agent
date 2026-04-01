import pandas as pd
import numpy as np

def main():
    df = pd.read_csv('data/lnb_advanced.csv', sep=';', skiprows=1)

    # Usuń pierwszą kolumnę
    df = df.iloc[:, 1:]
    
    # Nazwij kolumny
    df.columns
