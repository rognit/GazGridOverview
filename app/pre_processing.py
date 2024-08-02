import json
import re

import pandas as pd
from pyproj import Geod
from tqdm import tqdm


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
    # delete row where geo_point_2d = 43.18000060207648, 0.008788065393684546
    df = df[df['geo_point_2d'] != '43.18000060207648, 0.008788065393684546']

    df = df[['region', 'geo_shape']]

    return df


def extract_coordinates(geo_shape):
    shape = json.loads(geo_shape)
    coordinates = shape['coordinates']
    if shape['type'] == 'LineString':
        return [(lat, lon) if len(coord) == 2 else (lat, lon, alt)[:2] for coord in coordinates for lon, lat, *alt in
                [coord]]
    elif shape['type'] == 'MultiLineString':
        return [(lat, lon) if len(coord) == 2 else (lat, lon, alt)[:2] for line in coordinates for coord in line for
                lon, lat, *alt in [coord]]
    else:
        raise ValueError(f"Unsupported geometry type: {shape['type']}")


def create_segments(coordinates):
    return [(coordinates[i], coordinates[i + 1]) for i in range(len(coordinates) - 1)]


def process_gaz(df_grt, df_terega):
    geod = Geod(ellps='WGS84')

    def calculate_length(coords):
        (lon1, lat1), (lon2, lat2) = coords
        return geod.inv(lon1, lat1, lon2, lat2)[2]  # 0: Forward Azimuth, 1: Back Azimuth, 2: Distance

    # Manual cleaning of csv errors
    df_grt = grt_df_clean_up(df_grt)
    df_terega = terega_df_clean_up(df_terega)

    merged_df = pd.concat([df_grt, df_terega])

    tqdm.pandas()
    print("Extracting coordinates...", flush=True)
    merged_df['coordinates'] = merged_df['geo_shape'].progress_apply(extract_coordinates)
    print("Creating segments...", flush=True)
    merged_df['segments'] = merged_df['coordinates'].progress_apply(create_segments)

    # Explode the segments into separate rows
    df_segments = merged_df.explode('segments').drop(columns=['geo_shape', 'coordinates']).rename(
        columns={'segments': 'coordinates'})

    print("Calculating segment lengths...", flush=True)
    df_segments['length'] = df_segments['coordinates'].progress_apply(calculate_length)

    return df_segments


def process_pop(df):
    def make_square(idcar):
        match = re.search(r'N(\d+)E(\d+)', idcar)
        return int(match.group(1)), int(match.group(2))

    tqdm.pandas()
    print("Making squares...", flush=True)
    df[['north', 'east']] = df['idcar_200m'].progress_apply(lambda x: pd.Series(make_square(x)))

    print("Indexing...", flush=True)
    df.set_index(['north', 'east'], inplace=True)

    print("Calculating density...", flush=True)
    df['density'] = df['ind'].progress_apply(lambda x: 25 * x)

    df.drop(columns=['idcar_200m', 'ind'], inplace=True)

    return df
