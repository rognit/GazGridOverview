import networkx as nx
import numpy as np
import pandas as pd
from scipy.spatial.distance import euclidean


def make_markers(df):
    def length_graph(graph):
        return sum([sum(data['lengths'].values()) for _, _, data in graph.edges(data=True)])

    def create_graph(df):
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
        total_length = 0
        for u, v, data in graph.edges(data=True):
            #print([u, v, data])
            if condition_func(graph.get_edge_data(u, v)):
                subset_graph.add_edge(u, v, **data)
                total_length += sum(data['lengths'].values())
        print(f"Total length in subset graph: {total_length}")
        #out = list(nx.connected_components(subset_graph))

        connected_components = list(nx.connected_components(subset_graph))
        subsets_with_edges = []

        for component in connected_components:
            subgraph = subset_graph.subgraph(component)
            subset_edges = list(subgraph.edges(data=True))
            subsets_with_edges.append((component, subset_edges))

        return subsets_with_edges

    def calculate_subset_center(graph, subset):
        coordinates = []
        for node in subset:
            for neighbor in graph.neighbors(node):
                if neighbor in subset:
                    edge_data = graph.get_edge_data(node, neighbor)
                    start, end = edge_data['coordinates']
                    coordinates.extend([start, end])
        return tuple(float(coord) for coord in np.mean(coordinates, axis=0))

    def calculate_subset_quantities(graph, subset):
        green_total = orange_total = 0
        region = None
        for node in subset:
            for neighbor in graph.neighbors(node):
                if neighbor in subset:
                    edge_data = graph.get_edge_data(node, neighbor)
                    lengths = edge_data['lengths']
                    green_total += lengths['green']
                    orange_total += lengths['orange']
                    region = edge_data['region']
        return green_total, orange_total, region

    def create_subset_dataframe(graph, subsets_with_edges):
        data = []
        total_green = 0
        total_orange = 0
        for subset_nodes, subset_edges in subsets_with_edges:
            green_quantity = orange_quantity = 0
            coordinates = []
            points_with_regions = []

            for _, _, edge_data in subset_edges:
                lengths = edge_data['lengths']
                green_quantity += lengths['green']
                orange_quantity += lengths['orange']
                start, end = edge_data['coordinates']
                coordinates.extend([start, end])
                points_with_regions.extend([(start, edge_data['region']), (end, edge_data['region'])])

            total_green += green_quantity
            total_orange += orange_quantity

            center = tuple(float(coord) for coord in np.mean(coordinates, axis=0))

            # Find the nearest point to determine the region
            nearest_point = min(points_with_regions, key=lambda x: euclidean(center, x[0]))
            region = nearest_point[1]

            data.append({
                'region': region,
                'coordinates': center,
                'green_quantity': green_quantity,
                'orange_quantity': orange_quantity,
                'edges': subset_edges  # Store the edges for each subset
            })

        print(f"Total green: {total_green}, Total orange: {total_orange}")
        return pd.DataFrame(data)


    initial_total = sum([sum(lengths_str.values()) for lengths_str in df['lengths']])
    print(f"Initial total length: {initial_total}")
    network_graph = create_graph(df)

    print(f"Total length in graph: {length_graph(network_graph)}")

    green_only_subsets = get_connected_subsets(network_graph, is_green_only)
    green_orange_subsets = get_connected_subsets(network_graph, is_green_orange)

    green_only_df = create_subset_dataframe(network_graph, green_only_subsets)
    green_orange_df = create_subset_dataframe(network_graph, green_orange_subsets)



    return green_only_df, green_orange_df
