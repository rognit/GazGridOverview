import pandas as pd
from pyproj import CRS, Transformer
import re

crs3035 = CRS('EPSG:3035')
wgs84 = CRS('EPSG:4326')

transformer = Transformer.from_crs(crs3035, wgs84)


def convert(N, E):
    return transformer.transform(N, E)


def make_square(idcar):
    match = re.search(r'N(\d+)E(\d+)', idcar)
    return int(match.group(1)), int(match.group(2))


# Lire le fichier CSV
init_df = pd.read_csv('../resources/raw/test_pop.csv').copy()

df = init_df[['idcar_200m', 'ind']].copy()
df[['north', 'east']] = df['idcar_200m'].apply(lambda x: pd.Series(make_square(x)))
df['density'] = df['ind'] * 25

df.to_csv('../resources/test_pop_filtered.csv', index=False)
print(df.head())
