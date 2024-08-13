import networkx as nx
import numpy as np
import pandas as pd

from pyproj import Geod
from tqdm import tqdm

from config import *


geod = Geod(ellps='WGS84')


def calculate_length(lat1, lon1, lat2, lon2):
    return geod.inv(lon1, lat1, lon2, lat2)[2]  # 0: Forward Azimuth, 1: Back Azimuth, 2: Distance


def calculate_centroid(points):
    return (np.mean([p[0] for p in points]), np.mean([p[1] for p in points]))


def cluster_points(df):
    graph = nx.Graph()
    # link nodes with segment size < MERGING_THRESHOLD
    for row in df.itertuples(index=False):
        [start, end] = eval(row.coordinates)

        if float(row.length) < MERGING_THRESHOLD:
            graph.add_edge(start, end)
        else:
            graph.add_node(start)
            graph.add_node(end)

    return list(nx.connected_components(graph))


def refine_clusters(clusters):
    refined_clusters = []
    for cluster in clusters:
        sub_clusters = []
        points = list(cluster)
        while points:  # pick one point and add as many points enough close to it
            sub_cluster = [points.pop(0)]
            i = 0
            while i < len(points):
                if all(calculate_length(*p, *points[i]) <= MERGING_THRESHOLD for p in sub_cluster):
                    sub_cluster.append(points.pop(i))
                else:
                    i += 1
            sub_clusters.append(sub_cluster)
        refined_clusters.extend(sub_clusters)
    return refined_clusters


def create_centroid_df(clusters):
    centroid_dict = {}
    for cluster in clusters:
        centroid = calculate_centroid(cluster)
        for point in cluster:
            centroid_dict[point] = centroid

    return pd.DataFrame(list(centroid_dict.items()), columns=['points', 'centroid']).set_index('points')


def simplify_segments(colored_gaz_df):

    centroid_df = create_centroid_df(refine_clusters(cluster_points(colored_gaz_df)))

    computed_gaz_df = pd.DataFrame(columns=['region', 'coordinates', 'lengths'])
    same_centroid = []

    for row in colored_gaz_df.itertuples(index=False):
        region, (p1, p2), color, length = row
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
    for centroid, color, length in same_centroid:
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

    return computed_gaz_df
