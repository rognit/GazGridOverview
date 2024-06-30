import math

import pandas as pd
from pyproj import CRS, Transformer

crs3035 = CRS('EPSG:3035')
wgs84 = CRS('EPSG:4326')

to_wgs = Transformer.from_crs(crs3035, wgs84)
to_crs = Transformer.from_crs(wgs84, crs3035)

north, east = 2869000, 3466600
long, lat = to_wgs.transform(north, east)
north, east = to_crs.transform(long, lat)

print(f"{long}, {lat}")
print(f"north: {north}, East: {east}")

pop_df = pd.read_csv('../resources/test_pop_filtered.csv')


def add_color_to_edges(buffer_distance=200,
                       square_size=200,
                       square_size_squared=40000,
                       orange_threshold=300,
                       red_threshold=3000, ):
    def get_density(x, y):
        return pop_df.loc[(pop_df['north'] == y) & (pop_df['east'] == x), 'density'].values[0]

    def round_down_to_nearest(value):
        return int(value // square_size_squared)

    def get_square(x, y):
        return round_down_to_nearest(x), round_down_to_nearest(y)

    def get_colors_from_section(section):

        def get_squares_from_edge(edge):
            x1, y1, x2, y2 = edge
            dx, dy = x2 - x1, y2 - y1
            length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            edge_squares = set()

            def get_line(x1_local, y1_local, x2_local, y2_local):
                dx_local, dy_local = x2_local - x1_local, y2_local - y1_local
                a = dy_local / dx_local
                b = y1_local - a * x1_local
                return lambda x: a * x + b

            def get_squares_from_line(east_point_1, north_point_1, east_point_2, north_point_2):
                north_square_1, east_square_1 = get_square(north_point_1, east_point_1)
                north_square_2, east_square_2 = get_square(north_point_2, east_point_2)

                f = get_line(east_point_1, north_point_1, east_point_2, north_point_2)
                direction = 1 if east_point_1 < east_point_2 else -1

                output_squares = [(north_square_1, east_square_1)]
                old_north_square = north_square_1
                for east_square in range(east_square_1 + 1, east_square_2 + 1, direction * square_size):
                    north_square = round_down_to_nearest(f(east_square))
                    for crossed_north_square in range(old_north_square, north_square + 1, square_size):
                        output_squares.append(get_square(crossed_north_square, east_square))
                    old_north_square = north_square

                return list(set(output_squares))

            def get_boundaries():
                # Normalized normal vectors
                xn1, yn1 = -dy / length, dx / length
                xn2, yn2 = dy / length, -dx / length

                return ((x1 + buffer_distance * xn1,  # Line 1
                         y1 + buffer_distance * yn1,
                         x2 + buffer_distance * xn1,
                         y2 + buffer_distance * yn1),
                        (x1 + buffer_distance * xn2,  # Line 2
                         y1 + buffer_distance * yn2,
                         x2 + buffer_distance * xn2,
                         y2 + buffer_distance * yn2))

            (x1_l1, y1_l1, x2_l1, y2_l1), (x1_l2, y1_l2, x2_l2, y2_l2) = get_boundaries()

            edge_squares.update(get_squares_from_line(x1_l1, y1_l1, x2_l1, y2_l1))
            edge_squares.update(get_squares_from_line(x1_l2, y1_l2, x2_l2, y2_l2))

            number_of_lines = int(buffer_distance * 2 / square_size)
            for i in range(1, number_of_lines):
                offset_x = i * square_size * (x2_l1 - x1_l1) / length
                offset_y = i * square_size * (y2_l1 - y1_l1) / length
                edge_squares.update(
                    get_squares_from_line(x1_l1 + offset_x, y1_l1 + offset_y, x2_l1 + offset_x, y2_l1 + offset_y))

            return edge_squares

        def get_square_from_vertex(vertex):
            x, y = vertex

            def is_within_distance(x_corner, y_corner, x_vertex, y_vertex):
                return math.sqrt((x_corner - x_vertex) ** 2 + (y_corner - y_vertex) ** 2) <= buffer_distance

            def get_squares_from_corner(x_corner, y_corner):
                return ((x_corner, y_corner),
                        (x_corner - square_size, y_corner),
                        (x_corner, y_corner - square_size),
                        (x_corner - square_size, y_corner - square_size))

            x_initial_square, y_initial_square = get_square(x, y)
            edge_corners = set()
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
                        for x_corner, y_corner in corners:
                            edge_corners.add((x_corner, y_corner))
                n_ring += 1

            edge_squares = set()
            for x_corner, y_corner in edge_corners:
                if is_within_distance(x_corner, y_corner, x, y):
                    edge_squares.update(get_squares_from_corner(x_corner, y_corner))

            return edge_squares

        def get_color_from_squares(squares):
            max_density = max([get_density(x, y) for x, y in squares])
            if max_density < orange_threshold:
                return 'green'
            elif max_density < red_threshold:
                return 'orange'
            else:
                return 'red'

        current_vertex_squares = get_square_from_vertex(section[0])
        sub_section_colors = []
        for vertex in section[1:]:
            vertex_squares = get_square_from_vertex(vertex)
            sub_section_squares = current_vertex_squares | get_squares_from_edge(vertex) | vertex_squares
            current_vertex_squares = vertex_squares
            sub_section_color = get_color_from_squares(sub_section_squares)
            sub_section_colors.append(sub_section_color)
