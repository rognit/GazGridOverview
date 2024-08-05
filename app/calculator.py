import math
import ast

import pandas as pd
from tqdm import tqdm
from pyproj import CRS, Transformer

from config import *

def extract_vertices(df_gaz):
    vertices = []
    for row in df_gaz.itertuples():
        p1, p2 = ast.literal_eval(row.coordinates)
        vertices.append(p1)
        vertices.append(p2)
    return vertices



def merge_region_color_segments(df):
    def parse_segment(segment):
        return ast.literal_eval(segment.strip()) if isinstance(segment, str) else segment

    def comon_point(seg0, group):
        for seg in group:
            if seg0[0] in seg or seg0[1] in seg:
                return True
        return False

    def recursive_merge(paths):
        for i, path1 in enumerate(paths):
            for j, path2 in enumerate(paths):
                if i != j:
                    if path1[-1] == path2[0]:
                        return recursive_merge(
                            [path for k, path in enumerate(paths) if i != k != j] + [path1 + path2[1:]])
                    elif path1[0] == path2[-1]:
                        return recursive_merge(
                            [path for k, path in enumerate(paths) if i != k != j] + [path2 + path1[1:]])
                    elif path1[0] == path2[0]:
                        return recursive_merge(
                            [path for k, path in enumerate(paths) if i != k != j] + [path2[::-1] + path1[1:]])
                    elif path1[-1] == path2[-1]:
                        return recursive_merge(
                            [path for k, path in enumerate(paths) if i != k != j] + [path1 + path2[::-1][1:]])
        return paths

    # Making groups of segment that share at least one comon point
    groups = []
    for row in df.itertuples():
        seg0 = parse_segment(row.coordinates)
        relevant_groups = []
        for i, group in enumerate(groups):
            if comon_point(seg0, group):
                relevant_groups.append(i)
        if relevant_groups:
            new_group = [seg0]
            for i in sorted(relevant_groups, reverse=True):
                new_group.extend(groups.pop(i))
            groups.append(new_group)
        else:
            groups.append([seg0])

    # Merge segments into a minimum of paths
    paths = []
    for group in groups:
        paths.extend(map(list, recursive_merge(group)))
    return paths

def merge_all_segments(df):
    merged_section = []
    for region in df['region'].unique():
        region_df = df[df['region'] == region]
        for color in region_df['color'].unique():
            color_df = region_df[region_df['color'] == color]
            merged_segments = merge_region_color_segments(color_df)
            for section in merged_segments:
                merged_section.append({'region': region, 'color': color, 'coordinates': section, 'length': length})

    out = pd.DataFrame(merged_section)
    return out

def compute_parameters(gaz_df, pop_df,
                       buffer_distance=BUFFER_DISTANCE,
                       orange_threshold=ORANGE_THRESHOLD,
                       red_threshold=RED_THRESHOLD,
                       progress_callback=None):

    square_size = SQUARE_SIZE
    squared_buffer_distance = buffer_distance ** 2

    crs3035 = CRS('EPSG:3035')
    wgs84 = CRS('EPSG:4326')
    to_crs = Transformer.from_crs(wgs84, crs3035)

    def get_density(x, y):
        try:
            return pop_df.loc[(y, x), 'density']  # x, y = east, north
        except KeyError:
            return 0

    def round_down_to_nearest(value):
        return int(value // square_size * square_size)

    def get_square(x, y):
        return round_down_to_nearest(x), round_down_to_nearest(y)

    def get_squares_from_edge(x1, y1, x2, y2):
        if x1 > x2:
            x1, y1, x2, y2 = x2, y2, x1, y1
        dx, dy = x2 - x1, y2 - y1
        dir_y = -1 if dy < 0 else 1
        length = math.sqrt(dx ** 2 + dy ** 2)
        edge_squares = set()
        if length == 0:
            return edge_squares
        dxn, dyn = dx / length, dy / length  # Normalized direction vector
        dxnp, dynp = -dyn, dxn  # Perpendicular normalized direction vector (trigonometric direction = left)

        def get_line(x1_local, y1_local):
            a = dy / dx
            b = y1_local - a * x1_local
            return lambda x: a * x + b

        def get_squares_from_line(x1_local, y1_local, x2_local, y2_local):

            x_square_start, y_square_start = get_square(x1_local, y1_local)
            x_square_end, y_square_end = get_square(x2_local, y2_local)

            if x_square_start == x_square_end:
                return set(
                    (x_square_start, y) for y in range(y_square_start, y_square_end + dir_y, square_size * dir_y))

            f = get_line(x1_local, y1_local)
            output_squares = set()

            def add_column_squares(low_bound, high_bound, step, abscissa):
                for crossed_y_square in range(low_bound, high_bound, step):
                    output_squares.add((get_square(abscissa, crossed_y_square)))

            # Start
            y_first_axis = round_down_to_nearest(f(x_square_start + square_size))
            add_column_squares(y_square_start, y_first_axis + dir_y, square_size * dir_y, x_square_start)

            old_y = y_first_axis
            for x_square in range(round_down_to_nearest(x_square_start + square_size), x_square_end, square_size):
                y_square = round_down_to_nearest(f(x_square + square_size))
                add_column_squares(old_y, y_square + dir_y, square_size * dir_y, x_square)
                old_y = y_square

            # End
            add_column_squares(old_y, y_square_end + dir_y, square_size * dir_y, x_square_end)

            return output_squares

        # Line 1 = Border left
        x1_l1, y1_l1 = x1 + buffer_distance * dxnp, y1 + buffer_distance * dynp
        x2_l1, y2_l1 = x2 + buffer_distance * dxnp, y2 + buffer_distance * dynp
        # Line 2 = Border right
        x1_l2, y1_l2 = x1 + buffer_distance * -dxnp, y1 + buffer_distance * -dynp
        x2_l2, y2_l2 = x2 + buffer_distance * -dxnp, y2 + buffer_distance * -dynp

        number_of_lines = int(buffer_distance * 2 / square_size - 1)

        offset_x = square_size * -dxnp
        offset_y = square_size * -dynp

        for i in range(number_of_lines + 1):
            line = x1_l1 + i * offset_x, y1_l1 + i * offset_y, x2_l1 + i * offset_x, y2_l1 + i * offset_y
            edge_squares.update(get_squares_from_line(*line))

        edge_squares.update(get_squares_from_line(x1_l2, y1_l2, x2_l2, y2_l2))

        return edge_squares

    def get_squares_from_vertex(x, y):
        def is_within_distance(x_corner, y_corner):
            return (x_corner - x) ** 2 + (y_corner - y) ** 2 <= squared_buffer_distance

        def get_squares_from_corner(x_corner, y_corner):
            return ((x_corner, y_corner),
                    (x_corner - square_size, y_corner),
                    (x_corner, y_corner - square_size),
                    (x_corner - square_size, y_corner - square_size))

        x_initial_square, y_initial_square = get_square(x, y)
        edge_squares = {(x_initial_square, y_initial_square)}
        n_ring = 0
        while n_ring * square_size <= buffer_distance:
            for i in range(-n_ring, n_ring + 1):
                for j in range(-n_ring, n_ring + 1):
                    corners = [
                        (x_initial_square + j * square_size, y_initial_square + i * square_size),
                        (x_initial_square + j * square_size, y_initial_square + (i + 1) * square_size),
                        (x_initial_square + (j + 1) * square_size, y_initial_square + i * square_size),
                        (x_initial_square + (j + 1) * square_size, y_initial_square + (i + 1) * square_size)
                    ]

                    edge_squares.update(
                        square
                        for corner in corners if is_within_distance(*corner)
                        for square in get_squares_from_corner(*corner)
                    )

                    # Ring squares in the same line or column as the vertex's initial square can be both under buffer
                    # distance and not having their corner detected
                    if i == 0:  # Same line
                        x_local = x_initial_square + j * square_size
                        if is_within_distance(x_local, y) or is_within_distance(x_local + square_size, y):
                            edge_squares.add(get_square(x_local, y))
                    if j == 0:  # Same column
                        y_local = y_initial_square + i * square_size
                        if is_within_distance(x, y_local) or is_within_distance(x, y_local + square_size):
                            edge_squares.add(get_square(x, y_local))

            n_ring += 1

        return edge_squares

    def get_color_from_squares(squares):
        max_density = max(get_density(x, y) for (x, y) in squares)

        if max_density < orange_threshold:
            return 'green'
        elif max_density < red_threshold:
            return 'orange'
        else:
            return 'red'

    def get_color_from_segment(segment):

        ((y1, x1), (y2, x2)) = (to_crs.transform(*vertex) for vertex in
                                (ast.literal_eval(segment) if isinstance(segment, str) else segment))

        segment_squares = (get_squares_from_vertex(x1, y1) | get_squares_from_edge(x1, y1, x2, y2) |
                           get_squares_from_vertex(x2, y2))

        return get_color_from_squares(segment_squares)

    colored_gaz_df = gaz_df.copy()
    tqdm.pandas()

    total_segments = len(colored_gaz_df)
    progress_callback(0)

    for idx, row in enumerate(colored_gaz_df.itertuples()):
        color = get_color_from_segment(row.coordinates)
        colored_gaz_df.at[row.Index, 'color'] = color
        progress_callback(int((idx / total_segments) * 100))

    color_order = pd.CategoricalDtype(categories=['green', 'orange', 'red'], ordered=True)
    colored_gaz_df['color'] = colored_gaz_df['color'].astype(color_order)

    colored_gaz_df = colored_gaz_df.sort_values(by=['region', 'color'])  # Because we want to draw Green under Orange
    # under Red

    merged_colored_gaz_df = merge_all_segments(colored_gaz_df)

    progress_callback(100)

    return merged_colored_gaz_df
