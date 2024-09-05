import networkx as nx
import numpy as np
import pandas as pd
from scipy.spatial.distance import euclidean


def make_markers(df):
    def create_graph():
        graph = nx.Graph()
        for _, row in df.iterrows():
            start, end = row['coordinates']
            graph.add_edge(start, end, **row.to_dict())
        return graph

    def is_green_only(edge_data):
        return edge_data['lengths']['red'] == edge_data['lengths']['orange'] == 0

    def is_green_orange(edge_data):
        return edge_data['lengths']['red'] == 0

    def get_connected_subsets(graph, condition_func):
        subset_graph = nx.Graph()
        for u, v, data in graph.edges(data=True):
            if condition_func(graph.get_edge_data(u, v)):
                subset_graph.add_edge(u, v, **data)

        connected_components = list(nx.connected_components(subset_graph))
        subsets_with_edges = []

        for component in connected_components:
            subgraph = subset_graph.subgraph(component)
            subset_edges = list(subgraph.edges(data=True))
            subsets_with_edges.append((component, subset_edges))

        return subsets_with_edges

    def create_subset_dataframe(subsets_with_edges):
        data = []
        for subset_nodes, subset_edges in subsets_with_edges:
            green_quantity = orange_quantity = simplified_length = 0
            coordinates = points_with_regions = []

            for _, _, edge_data in subset_edges:
                lengths = edge_data['lengths']
                green_quantity += lengths['green']
                orange_quantity += lengths['orange']
                simplified_length += edge_data['length']
                start, end = edge_data['coordinates']
                coordinates.extend([start, end])
                points_with_regions.extend([(start, edge_data['region']), (end, edge_data['region'])])

            center = tuple(float(coord) for coord in np.mean(coordinates, axis=0))

            # Find the nearest point to determine the region
            nearest_point = min(points_with_regions, key=lambda x: euclidean(center, x[0]))
            region = nearest_point[1]

            data.append({
                'region': region,
                'coordinates': center,
                'green_quantity': green_quantity,
                'orange_quantity': orange_quantity,
                'simplified_length': simplified_length
            })

        return pd.DataFrame(data)

    network_graph = create_graph()

    initial_total = sum([sum(lengths_str.values()) for lengths_str in df['lengths']])
    print(f"Initial total length: {initial_total}")
    total_length = sum([sum(data['lengths'].values()) for _, _, data in network_graph.edges(data=True)])
    print(f"Total length in graph: {total_length}")

    green_only_subsets = get_connected_subsets(network_graph, is_green_only)
    green_orange_subsets = get_connected_subsets(network_graph, is_green_orange)

    green_only_df = create_subset_dataframe(green_only_subsets)
    green_orange_df = create_subset_dataframe(green_orange_subsets)

    green_orange_df = green_orange_df[green_orange_df['orange_quantity'] != 0]

    return green_only_df, green_orange_df
