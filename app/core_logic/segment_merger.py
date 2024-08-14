from scipy.spatial import cKDTree
import numpy as np
import pandas as pd
from pyproj import Geod
from tqdm import tqdm

# Assuming MAX_MERGING_THRESHOLD and MERGING_THRESHOLD are defined in config
from config import *

geod = Geod(ellps='WGS84')


def calculate_length(lat1, lon1, lat2, lon2):
    return geod.inv(lon1, lat1, lon2, lat2)[2]  # 0: Forward Azimuth, 1: Back Azimuth, 2: Distance


def calculate_centroid(points):
    return (np.mean([p[0] for p in points]), np.mean([p[1] for p in points]))


def make_clusters(df):
    geod = Geod(ellps="WGS84")

    coordinates = list(set([point for segment in df['coordinates'].tolist() for point in segment]))

    tree = cKDTree(coordinates)
    # Approximate conversion from meters to degrees (1 degree ≈ 111km at the equator)
    approx_distance_deg = MAX_MERGING_THRESHOLD / 111000

    def calculate_length(coords):
        (lat1, lon1), (lat2, lon2) = coords
        return geod.inv(lon1, lat1, lon2, lat2)[2]  # 0: Forward Azimuth, 1: Back Azimuth, 2: Distance

    def find_nearby_points(point):
        potential_neighbors = tree.query_ball_point(point, r=approx_distance_deg)

        nearby_points = []
        for idx in potential_neighbors:
            if coordinates[idx] != point and calculate_length((point, coordinates[idx])) <= MERGING_THRESHOLD:
                nearby_points.append(coordinates[idx])
        return nearby_points

    visited = set()
    clusters = []

    for i, point in tqdm(enumerate(coordinates), desc="Clustering Points", total=len(coordinates)):
        if i in visited:
            continue

        cluster = [point]
        visited.add(i)

        neighbors = find_nearby_points(point)

        for neighbor in neighbors:
            neighbor_idx = coordinates.index(neighbor)
            if neighbor_idx not in visited:
                cluster.append(neighbor)
                visited.add(neighbor_idx)

        clusters.append(cluster)

    return clusters


def create_centroid_df(clusters):
    centroid_dict = {}
    for cluster in tqdm(clusters, desc="Calculating Centroids"):
        centroid = calculate_centroid(cluster)
        for point in cluster:
            centroid_dict[point] = centroid

    return pd.DataFrame(list(centroid_dict.items()), columns=['points', 'centroid']).set_index('points')


def simplify_segments(colored_gaz_df):
    centroid_df = create_centroid_df(make_clusters(colored_gaz_df))

    centroid_df.to_csv("centroid.csv")
    centroid_df.index = centroid_df.index.map(lambda x: tuple(map(float, x)))

    computed_gaz_df = pd.DataFrame(columns=['region', 'coordinates', 'lengths'])
    same_centroid = []

    for row in tqdm(colored_gaz_df.itertuples(index=False), desc="Simplifying Segments", total=len(colored_gaz_df)):
        region, (p1, p2), length, color = row
        c1, c2 = centroid_df.loc[p1, 'centroid'], centroid_df.loc[p2, 'centroid']
        if c1 == c2:
            same_centroid.append((c1, color, length))
        else:
            if not computed_gaz_df['coordinates'].apply(lambda x: x == (c1, c2)).any():
                new_row = pd.DataFrame({
                    'region': [region],
                    'coordinates': [(c1, c2)],
                    'lengths': [{'red': 0, 'orange': 0, 'green': 0}]
                })
                computed_gaz_df = pd.concat([computed_gaz_df, new_row], ignore_index=True)

            idx = computed_gaz_df[computed_gaz_df['coordinates'] == (c1, c2)].index[0]
            computed_gaz_df.at[idx, 'lengths'][color] += length

    # Handle segments with same centroid
    for centroid, color, length in tqdm(same_centroid, desc="Handling Same Centroid Segments"):
        # Find all branches connected to this centroid
        connected_branches = computed_gaz_df[
            computed_gaz_df['coordinates'].apply(lambda x: centroid in x)
        ]

        if not connected_branches.empty:
            # Calculate the length to add to each branch
            length_per_branch = length / len(connected_branches)

            # Distribute the length equally among all connected branches
            for idx in connected_branches.index:
                computed_gaz_df.at[idx, 'lengths'][color] += length_per_branch

    computed_gaz_df.to_csv("computed_gaz_df.csv")

    return computed_gaz_df
