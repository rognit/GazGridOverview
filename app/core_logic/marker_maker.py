import pandas as pd
import networkx as nx
import numpy as np


def make_markers(df):
    def check_total_length(df):
        total_length = sum([sum(lengths_str.values()) for lengths_str in df['lengths']])
        print(f"Initial total length: {total_length}")
        return total_length

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

    def create_subset_dataframe(graph, subsets):
        data = []
        total_green = 0
        total_orange = 0
        for subset in subsets:
            green_quantity, orange_quantity, region = calculate_subset_quantities(graph, subset)
            total_green += green_quantity
            total_orange += orange_quantity
            data.append({
                'region': region,
                'coordinates': calculate_subset_center(graph, subset),
                'green_quantity': green_quantity,
                'orange_quantity': orange_quantity,
            })
        print(f"Total green: {total_green}, Total orange: {total_orange}")
        return pd.DataFrame(data)

    initial_total = check_total_length(df)
    network_graph = create_graph(df)

    print("After create_graph:")
    graph_total = sum([sum(data['lengths'].values()) for _, _, data in network_graph.edges(data=True)])
    print(f"Total length in graph: {graph_total}")

    green_only_subsets = get_connected_subsets(network_graph, is_green_only)
    green_orange_subsets = get_connected_subsets(network_graph, is_green_orange)

    print("Green only subsets:")
    green_only_df = create_subset_dataframe(network_graph, green_only_subsets)

    print("Green orange subsets:")
    green_orange_df = create_subset_dataframe(network_graph, green_orange_subsets)

    final_total = green_only_df['green_quantity'].sum() + green_orange_df['green_quantity'].sum() + green_orange_df[
        'orange_quantity'].sum()
    print(f"Final total length: {final_total}")
    print(f"Difference from initial: {final_total - initial_total}")

    return green_only_df, green_orange_df