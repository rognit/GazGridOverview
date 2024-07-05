import json
import os
import pandas as pd
from tqdm import tqdm
from config import *


def extract_coordinates(geo_shape):
    shape = json.loads(geo_shape)
    coordinates = shape['coordinates']
    if shape['type'] == 'LineString':
        return [(lat, lon) if len(coord) == 2 else (lat, lon, alt)[:2] for coord in coordinates for lon, lat, *alt in [coord]]
    elif shape['type'] == 'MultiLineString':
        return [(lat, lon) if len(coord) == 2 else (lat, lon, alt)[:2] for line in coordinates for coord in line for lon, lat, *alt in [coord]]
    else:
        raise ValueError(f"Unsupported geometry type: {shape['type']}")

def create_segments(coordinates):
    return [(coordinates[i], coordinates[i + 1]) for i in range(len(coordinates) - 1)]

def main():
    df_grt = pd.read_csv(os.path.normpath(os.path.join('..', INIT_GRT_PATH)), delimiter=';')
    df_terega = pd.read_csv(os.path.normpath(os.path.join('..', INIT_TEREGA_PATH)), delimiter=';')

    df_terega_filtered = df_terega[['region', 'geo_shape']]
    df_grt_filtered = df_grt[['nom_region', 'geo_shape']]
    df_grt_filtered = df_grt_filtered.rename(columns={'nom_region': 'region'})

    merged_df = pd.concat([df_grt_filtered, df_terega_filtered])

    print("Processing data...")
    tqdm.pandas()
    merged_df['coordinates'] = merged_df['geo_shape'].progress_apply(extract_coordinates)
    merged_df['segments'] = merged_df['coordinates'].progress_apply(create_segments)

    # Explode the segments into separate rows
    df_segments = merged_df.explode('segments').drop(columns=['geo_shape', 'coordinates']).rename(columns={'segments': 'coordinates'})

    #df_segments['start_point'] = df_segments['segments'].apply(lambda x: x[0])
    #df_segments['end_point'] = df_segments['segments'].apply(lambda x: x[1])
    #df_segments = df_segments.drop(columns=['segments'])

    df_segments.to_csv(os.path.normpath(os.path.join('..', GAZ_NETWORK_PATH)), index=False)

if __name__ == '__main__':
    main()
