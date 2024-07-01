import math
import json
import pandas as pd
from tqdm import tqdm
from pyproj import CRS, Transformer


def add_color_to_edges(buffer_distance=200,
                       square_size=200,
                       orange_threshold=300,
                       red_threshold=3000):

    gaz_df = pd.read_csv('../resources/gaz_network.csv')
    pop_df = pd.read_csv('../resources/pop_filtered.csv')
    pop_df.set_index(['north', 'east'], inplace=True)

    crs3035 = CRS('EPSG:3035')
    wgs84 = CRS('EPSG:4326')
    to_crs = Transformer.from_crs(wgs84, crs3035)

    # to_wgs = Transformer.from_crs(crs3035, wgs84)
    # north, east = 2869000, 3466600
    # lat, lon = to_wgs.transform(north, east)
    # (48.329768832956944 -1.5720923688546355)
    # north, east = to_crs.transform(lon, lat)

    def get_density(east, north):
        try:
            return pop_df.loc[(north, east), 'density']
        except KeyError:
            return 0

    def round_down_to_nearest(value):
        return int(value // square_size * square_size)

    def get_square(x, y):
        return round_down_to_nearest(x), round_down_to_nearest(y)

    def swap_lat_lon(coordinates):
        return [(lon, lat) for lat, lon in coordinates]

    def get_colors_from_section(geoshape):
        section = [to_crs.transform(*vertex) for vertex in swap_lat_lon(json.loads(geoshape)["coordinates"])]

        def get_squares_from_edge(x1, y1, x2, y2):
            dx, dy = x2 - x1, y2 - y1
            length = math.sqrt(dx ** 2 + dy ** 2)
            edge_squares = set()
            if length == 0:
                return edge_squares

            def get_line(x1_local, y1_local, x2_local, y2_local):
                dx_local, dy_local = x2_local - x1_local, y2_local - y1_local
                a = dy_local / dx_local
                b = y1_local - a * x1_local
                return lambda x: a * x + b

            def get_squares_from_line(x1_local, y1_local, x2_local, y2_local):
                x_square_1, y_square_1 = get_square(x1_local, y1_local)
                x_square_2, y_square_2 = get_square(x2_local, y2_local)

                f = get_line(x1_local, y1_local, x2_local, y2_local)
                direction = 1 if x1_local < x2_local else -1

                output_squares = [(y_square_1, x_square_1)]
                old_north_square = y_square_1
                for east_square in range(x_square_1 + 1, x_square_2 + 1, direction * square_size):
                    north_square = round_down_to_nearest(f(east_square))
                    for crossed_north_square in range(old_north_square, north_square + 1, square_size):
                        output_squares.append(get_square(crossed_north_square, east_square))
                    old_north_square = north_square

                return output_squares

            def get_boundaries():
                # Normalized normal vectors
                xn1, yn1 = -dy / length, dx / length
                xn2, yn2 = dy / length, -dx / length

                return ((x1 + buffer_distance * xn1,  # Border 1
                         y1 + buffer_distance * yn1,
                         x2 + buffer_distance * xn1,
                         y2 + buffer_distance * yn1),
                        (x1 + buffer_distance * xn2,  # Border 2
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
            def is_within_distance(x_corner, y_corner, x_vertex, y_vertex):
                return math.sqrt((x_corner - x_vertex) ** 2 + (y_corner - y_vertex) ** 2) <= buffer_distance

            def get_squares_from_corner(x_corner, y_corner):
                return ((x_corner, y_corner),
                        (x_corner - square_size, y_corner),
                        (x_corner, y_corner - square_size),
                        (x_corner - square_size, y_corner - square_size))

            x_initial_square, y_initial_square = get_square(*vertex)
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
                        for corner in corners:
                            edge_corners.add(corner)
                n_ring += 1

            edge_squares = set()
            for edge_corner in edge_corners:
                if is_within_distance(*edge_corner, *vertex):
                    edge_squares.update(get_squares_from_corner(*edge_corner))

            return edge_squares

        def get_color_from_squares(squares):
            max_density = max(get_density(*square) for square in squares)
            #(max_density)
            if max_density < orange_threshold:
                return 'green'
            elif max_density < red_threshold:
                return 'orange'
            else:
                return 'red'

        if len(section) == 0 or len(section) == 1:
            print(f"ERROR: Section has {len(section)} vertices")
        #print(section)
        old_vertex = section[0]
        old_vertex_squares = get_square_from_vertex(old_vertex)
        sub_section_colors = []

        for vertex in section[1:]:
            vertex_squares = get_square_from_vertex(vertex)
            sub_section_squares = old_vertex_squares | get_squares_from_edge(*old_vertex, *vertex) | vertex_squares
            #print("\nsub_section_squares", sub_section_squares, "\nold_vertex_squares", old_vertex_squares, "\nedge", get_squares_from_edge(*old_vertex, *vertex), "\nvertex_squares\n", vertex_squares)

            old_vertex = vertex
            old_vertex_squares = vertex_squares

            sub_section_colors.append(get_color_from_squares(sub_section_squares))
        print(sub_section_colors)
        return sub_section_colors

    tqdm.pandas()
    gaz_df['section_colors'] = gaz_df['geo_shape'].progress_apply(get_colors_from_section)
    gaz_df.to_csv('../resources/gaz_network_colored.csv', index=False)


add_color_to_edges()