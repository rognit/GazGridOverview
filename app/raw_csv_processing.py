import json
import re

import pandas as pd
from tqdm import tqdm

from app.tools import calculate_length
from config import SQUARE_SIZE


def process_gaz(df_grt, df_terega):
    def grt_df_clean_up(df):
        # add "Provence-Alpes-Côte d'Azur" and "Alpes-Maritimes" for "nom_region" and "departement" of objectid 764
        df.loc[df['objectid'] == 764, 'nom_region'] = "Provence-Alpes-Côte d'Azur"
        df.loc[df['objectid'] == 764, 'departement'] = "Alpes-Maritimes"

        # add "Provence-Alpes-Côte d'Azur" and "Alpes-Maritimes" for "nom_region" and "departement" of objectid 958
        df.loc[df['objectid'] == 958, 'nom_region'] = "Provence-Alpes-Côte d'Azur"
        df.loc[df['objectid'] == 958, 'departement'] = "Alpes-Maritimes"

        # add "Provence-Alpes-Côte d'Azur" and "Bouches-du-Rhône" for "nom_region" and "departement" of objectid 8442
        df.loc[df['objectid'] == 8442, 'nom_region'] = "Provence-Alpes-Côte d'Azur"
        df.loc[df['objectid'] == 8442, 'departement'] = "Bouches-du-Rhône"

        df = df[['nom_region', 'geo_shape']]
        df = df.rename(columns={'nom_region': 'region'})

        return df

    def terega_df_clean_up(df):
        # delete row where geo_point_2d = "43.18000060207648, 0.008788065393684546"
        df = df[df['geo_point_2d'] != '43.18000060207648, 0.008788065393684546']

        df = df[['region', 'geo_shape']]

        return df

    def extract_coordinates(geo_shape):
        shape = json.loads(geo_shape)
        coordinates = shape['coordinates']
        if shape['type'] == 'LineString':
            return [(lat, lon) if len(coord) == 2 else (lat, lon, alt)[:2] for coord in coordinates for lon, lat, *alt
                    in
                    [coord]]
        elif shape['type'] == 'MultiLineString':
            return [(lat, lon) if len(coord) == 2 else (lat, lon, alt)[:2] for line in coordinates for coord in line for
                    lon, lat, *alt in [coord]]

    def create_segments(coordinates):
        return [(coordinates[i], coordinates[i + 1]) for i in range(len(coordinates) - 1)]

    # Manual cleaning of csv errors
    df_grt = grt_df_clean_up(df_grt)
    df_terega = terega_df_clean_up(df_terega)

    merged_df = pd.concat([df_grt, df_terega])

    tqdm.pandas(desc="Extracting coordinates")
    merged_df['coordinates'] = merged_df['geo_shape'].progress_apply(extract_coordinates)

    tqdm.pandas(desc="Creating segments")
    merged_df['segments'] = merged_df['coordinates'].progress_apply(create_segments)

    # Explode the segments into separate rows
    df_segments = merged_df.explode('segments').drop(columns=['geo_shape', 'coordinates']).rename(
        columns={'segments': 'coordinates'}).reset_index(drop=True)

    tqdm.pandas(desc="Calculating segment lengths")
    df_segments['length'] = df_segments['coordinates'].progress_apply(calculate_length)

    return df_segments


def process_pop(df):
    def make_square(idcar):
        match = re.search(r'N(\d+)E(\d+)', idcar)
        return int(match.group(1)), int(match.group(2))

    tqdm.pandas(desc="Making squares")
    df[['north', 'east']] = df['idcar_200m'].progress_apply(lambda x: pd.Series(make_square(x)))

    tqdm.pandas(desc="Indexing")
    df.set_index(['north', 'east'], inplace=True)

    factor = round(1e6 / (SQUARE_SIZE**2))

    tqdm.pandas(desc="Calculating density")
    df['density'] = df['ind'].progress_apply(lambda x: factor * x)

    df.drop(columns=['idcar_200m', 'ind'], inplace=True)

    return df
