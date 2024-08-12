import pickle
from collections import defaultdict

from pyproj import Geod
from tqdm import tqdm

from config import *


def make_adjacency_dict(gaz_df):

    def extract_vertices(df_gaz):
        coordinates = df_gaz['coordinates'].apply(eval)
        return set([tuple(vertex) for pair in coordinates for vertex in pair])

    vertices = list(extract_vertices(gaz_df))

    geod = Geod(ellps='WGS84')

    def calculate_length(lat1, lon1, lat2, lon2):
        return geod.inv(lon1, lat1, lon2, lat2)[2]  # 0: Forward Azimuth, 1: Back Azimuth, 2: Distance

    n = len(vertices)
    print(n)

    adjacency_dict = defaultdict(dict)
    proximity_threshold = 1000

    for i in tqdm(range(n), desc="Calculating adjacency dictionary"):
        for j in range(i + 1, n):
            distance = calculate_length(*vertices[i], *vertices[j])
            if distance <= proximity_threshold:
                adjacency_dict[vertices[i]][vertices[j]] = adjacency_dict[vertices[j]][vertices[i]] = distance


    with open('vertex_adjacency_dict.pkl', 'wb') as f:
        pickle.dump(adjacency_dict, f)

def merging_vertex(vertex_adjacency_dict):
