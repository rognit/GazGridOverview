import pandas as pd
from pyproj import CRS, Transformer
import re

# Définir les systèmes de coordonnées
crs3035 = CRS('EPSG:3035')
wgs84 = CRS('EPSG:4326')

# Créer un transformateur de coordonnées
transformer = Transformer.from_crs(crs3035, wgs84)

# Fonction pour convertir les coordonnées
def convert(N, E):
    return transformer.transform(N, E)

# Fonction pour extraire les coordonnées de la chaîne idcar
def make_square(idcar):
    match = re.search(r'N(\d+)E(\d+)', idcar)
    return int(match.group(1)), int(match.group(2))

# Spécifier les types de données pour chaque colonne
dtype_dict = {
    'idcar_200m': str,
    'idcar_1km': str,
    'idcar_nat': str,
    'i_est_200': int,
    'i_est_1km': int,
    'lcog_geo': str,
    'ind': float,
    'men': float,
    'men_pauv': float,
    'men_1ind': float,
    'men_5ind': float,
    'men_prop': float,
    'men_fmp': float,
    'ind_snv': float,
    'men_surf': float,
    'men_coll': float,
    'men_mais': float,
    'log_av45': float,
    'log_45_70': float,
    'log_70_90': float,
    'log_ap90': float,
    'log_inc': float,
    'log_soc': float,
    'ind_0_3': float,
    'ind_4_5': float,
    'ind_6_10': float,
    'ind_11_17': float,
    'ind_18_24': float,
    'ind_25_39': float,
    'ind_40_54': float,
    'ind_55_64': float,
    'ind_65_79': float,
    'ind_80p': float,
    'ind_inc': float
}

# Lire le fichier CSV avec les types de données spécifiés
init_df = pd.read_csv('../resources/raw/carreaux_200m_met2019.csv', dtype=dtype_dict).copy()

# Créer une copie du dataframe avec seulement les colonnes nécessaires
df = init_df[['idcar_200m', 'ind']].copy()

# Appliquer la fonction make_square pour extraire les coordonnées et les ajouter au dataframe
df[['north', 'east']] = df['idcar_200m'].apply(lambda x: pd.Series(make_square(x)))
df.set_index(['north', 'east'], inplace=True)

# Calculer la densité
df['density'] = df['ind'] * 25

# Supprimer les colonnes inutiles
df.drop(columns=['idcar_200m', 'ind'], inplace=True)

# Sauvegarder le dataframe filtré dans un fichier CSV
df.to_csv('../resources/pop_filtered.csv')
print(df.head())
