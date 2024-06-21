import pandas as pd
from pyproj import CRS, Transformer
import re


crs3035 = CRS('EPSG:3035')
wgs84 = CRS('EPSG:4326')

transformer = Transformer.from_crs(crs3035, wgs84)

def convert(N, E):
    return transformer.transform(N, E)

def extract_coordinates(idcar):
    match = re.search(r'N(\d+)E(\d+)', idcar)
    if match:
        N = int(match.group(1))
        E = int(match.group(2))
        return N, E
    print('ERROR')

# Lire le fichier CSV
df = pd.read_csv('../resources/test_pop.csv')

# Extraire les coordonnées et les convertir
coordinates = df['idcar_200m'].apply(lambda x: extract_coordinates(x))
df['N'] = coordinates.apply(lambda x: x[0])
df['E'] = coordinates.apply(lambda x: x[1])
df[['latitude', 'longitude']] = df.apply(lambda row: convert(row['N'], row['E']), axis=1, result_type='expand')

# Garder les colonnes nécessaires
columns_to_keep = ['idcar_200m', 'ind', 'latitude', 'longitude']
filtered_df = df[columns_to_keep]

# Sauvegarder le nouveau dataset
filtered_df.to_csv('../resources/test_pop_filtered.csv', index=False)

print(filtered_df.head())
