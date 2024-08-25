import pandas as pd
import networkx as nx
import numpy as np


def make_markers(df):

    def create_graph(df):
        graph = nx.Graph()
        for _, row in df.iterrows():
            start, end = row['coordinates']
            graph.add_edge(start, end, **row.to_dict())
        return graph

    def is_green_only(graph, u, v):
        edge_data = graph.get_edge_data(u, v)
        lengths = edge_data['lengths']
        return lengths['red'] == lengths['orange'] == 0

    def is_green_orange(graph, u, v):
        edge_data = graph.get_edge_data(u, v)
        return edge_data['lengths']['red'] == 0

    def get_connected_subsets(graph, condition_func):
        subset_graph = nx.Graph()
        for u, v, data in graph.edges(data=True):
            if condition_func(graph, u, v):
                subset_graph.add_edge(u, v, **data)
        return list(nx.connected_components(subset_graph))

    def calculate_subset_center(graph, subset):
        coordinates = []
        for node in subset:
            for neighbor in graph.neighbors(node):
                if neighbor in subset:
                    edge_data = graph.get_edge_data(node, neighbor)
                    start, end = edge_data['coordinates']
                    coordinates.extend([start, end])
        mean_coordinates = np.mean(coordinates, axis=0)
        return tuple(float(coord) for coord in mean_coordinates)

    def calculate_subset_quantities(graph, subset):
        green_total = orange_total = 0
        for node in subset:
            for neighbor in graph.neighbors(node):
                if neighbor in subset:
                    edge_data = graph.get_edge_data(node, neighbor)
                    lengths = edge_data['lengths']
                    green_total += lengths['green']
                    orange_total += lengths['orange']
                    region = edge_data['region']
        return green_total, orange_total, region

    def create_subset_dataframe(graph, subsets):
        data = []
        for subset in subsets:
            green_quantity, orange_quantity, region = calculate_subset_quantities(graph, subset)
            data.append({
                'region': region,
                'coordinates': calculate_subset_center(graph, subset),
                'green_quantity': green_quantity,
                'orange_quantity': orange_quantity,
            })
        return pd.DataFrame(data)

    network_graph = create_graph(df)

    green_only_subsets = get_connected_subsets(network_graph, is_green_only)
    green_orange_subsets = get_connected_subsets(network_graph, is_green_orange)

    green_only_df = create_subset_dataframe(network_graph, green_only_subsets)
    green_orange_df = create_subset_dataframe(network_graph, green_orange_subsets)

    green_only_df.to_csv("green_only_subsets.csv", index=False)
    green_orange_df.to_csv("green_orange_subsets.csv", index=False)

    return green_only_df, green_orange_df
