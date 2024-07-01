import pandas as pd
import json
import numpy as np


def load_gaz_data():
    grt_csv_file = 'resources/gaz_network_colored.csv'
    df_grt = pd.read_csv(grt_csv_file)
    return df_grt

def extract_coordinates(df, has_altitude=False):
    def get_coordinates(geo_shape):
        if isinstance(geo_shape, str):
            geo_shape_dict = json.loads(geo_shape)
            coordinates = geo_shape_dict['coordinates']
            flattened_coordinates = []

            if has_altitude:
                if isinstance(coordinates[0][0], list):
                    for segment in coordinates:
                        for lon, lat, alt in segment:
                            flattened_coordinates.append((lat, lon))
                else:
                    for lon, lat, alt in coordinates:
                        flattened_coordinates.append((lat, lon))
            else:
                if isinstance(coordinates[0][0], list):
                    for segment in coordinates:
                        for lon, lat in segment:
                            flattened_coordinates.append((lat, lon))
                else:
                    for lon, lat in coordinates:
                        flattened_coordinates.append((lat, lon))

            return flattened_coordinates
        else:
            return np.nan

    df['coordinates'] = df['geo_shape'].apply(get_coordinates)

    regions = df['nom_region' if 'nom_region' in df.columns else 'region'].unique()
    region_dfs = {region: df[df['nom_region' if 'nom_region' in df.columns else 'region'] == region] for region in
                  regions}

    region_counts = {region: len(region_dfs[region]) for region in regions}
    region_display_names = {region: f"{region} ({count})" for region, count in region_counts.items()}
    display_to_region = {v: k for k, v in region_display_names.items()}

    return region_dfs, region_display_names, display_to_region
