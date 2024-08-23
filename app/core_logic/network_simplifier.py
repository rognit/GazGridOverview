import pandas as pd
from tqdm import tqdm
from collections import defaultdict

from scipy.spatial import cKDTree

from app.tools import calculate_length
from config import *


def simplify_segments(colored_gaz_df, merging_threshold, show_tqdm):

    def calculate_centroid(points):
        return sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points)

    def make_clusters(df):
        coordinates = list(set([point for segment in df['coordinates'].tolist() for point in segment]))
        tree = cKDTree(coordinates)

        # Step 1: Approximation to retrieve VERY QUICKLY the roughly close points
        # Approximate conversion from meters to degrees (1 degree ≈ 111km at the equator)
        approx_distance_deg = MAX_MERGING_THRESHOLD / 111000

        def find_nearby_points(point):
            potential_neighbors = tree.query_ball_point(point, r=approx_distance_deg)

            nearby_points = []
            for idx in potential_neighbors:
                if coordinates[idx] != point and calculate_length((point, coordinates[idx])) <= merging_threshold:
                    nearby_points.append(coordinates[idx])
            return nearby_points

        # Step 2: Then clustering is carried out with maximum precision.
        visited = set()
        clusters = []

        iterator = tqdm(enumerate(coordinates), desc="Clustering Points", total=len(coordinates)) \
            if show_tqdm else enumerate(coordinates)

        for i, point in iterator:
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
        iterator = tqdm(clusters, desc="Calculating Centroids", total=len(clusters)) if show_tqdm else clusters
        for cluster in iterator:
            centroid = calculate_centroid(cluster)
            for point in cluster:
                centroid_dict[point] = centroid

        return pd.DataFrame(list(centroid_dict.items()), columns=['points', 'centroid']).set_index('points')

    def choose_color(lengths):
        match lengths['red'], lengths['orange'], lengths['green']:
            case 0, 0, green if green > 0:
                return 'green'
            case 0, orange, 0 if orange > 0:
                return 'orange'
            case 0, orange, green if orange > 0 and green > 0:
                return 'yellow'
            case red, 0, 0 if red > 0:
                return 'red'
            case red, _, _ if red > 0:
                return 'brown'
            case _, _, _:
                print(f"Unexpected lengths: {lengths}")
                return 'red'


    centroid_df = create_centroid_df(make_clusters(colored_gaz_df))

    centroid_df.to_csv("centroid.csv")
    centroid_df.index = centroid_df.index.map(lambda x: tuple(map(float, x)))

    iterator = tqdm(colored_gaz_df.itertuples(index=False), desc="Simplifying Segments", total=len(colored_gaz_df)) \
        if show_tqdm else colored_gaz_df.itertuples(index=False)


    computed_gaz = {}
    same_centroid = []

    for region, (p1, p2), length, color in iterator:
        c1, c2 = centroid_df.loc[p1, 'centroid'], centroid_df.loc[p2, 'centroid']
        if c1 == c2:
            same_centroid.append((c1, color, length))
        else:
            key = (c1, c2) if c1 < c2 else (c2, c1)
            if key not in computed_gaz:
                computed_gaz[key] = {'region': region, 'lengths': {'red': 0, 'orange': 0, 'green': 0}}
            computed_gaz[key]['lengths'][color] += length

    # Handle segments with same centroid
    centroid_connections = defaultdict(list)
    for key in computed_gaz:
        centroid_connections[key[0]].append(key)
        centroid_connections[key[1]].append(key)

    for centroid, color, length in same_centroid:
        connected_branches = centroid_connections[centroid]
        if connected_branches:
            length_per_branch = length / len(connected_branches)
            for key in connected_branches:
                computed_gaz[key]['lengths'][color] += length_per_branch

    # Convert to DataFrame
    computed_gaz_df = pd.DataFrame([
        {'region': data['region'], 'coordinates': key, 'lengths': data['lengths']}
        for key, data in computed_gaz.items()
    ])

    computed_gaz_df['color'] = computed_gaz_df['lengths'].apply(choose_color)
    computed_gaz_df['length'] = computed_gaz_df['coordinates'].apply(calculate_length)

    return computed_gaz_df
