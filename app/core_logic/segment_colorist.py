import math

from pyproj import CRS, Transformer
from tqdm import tqdm

from config import *


def color_segments(gaz_df, pop_df, buffer_distance, orange_threshold, red_threshold, progress_callback, show_tqdm):

    squared_buffer_distance = buffer_distance ** 2

    crs3035 = CRS('EPSG:3035')  # CRS for Europe
    wgs84 = CRS('EPSG:4326')  # CRS for GPS coordinates
    to_crs = Transformer.from_crs(wgs84, crs3035)

    def get_density(x, y):
        try:
            return pop_df.loc[(y, x), 'density']  # x, y = east, north
        except KeyError:
            return 0

    def round_down_to_nearest(value):
        return int(value // SQUARE_SIZE * SQUARE_SIZE)

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
                    (x_square_start, y) for y in range(y_square_start, y_square_end + dir_y, SQUARE_SIZE * dir_y))

            f = get_line(x1_local, y1_local)
            output_squares = set()

            def add_column_squares(low_bound, high_bound, step, abscissa):
                for crossed_y_square in range(low_bound, high_bound, step):
                    output_squares.add((get_square(abscissa, crossed_y_square)))

            # Start
            y_first_axis = round_down_to_nearest(f(x_square_start + SQUARE_SIZE))
            add_column_squares(y_square_start, y_first_axis + dir_y, SQUARE_SIZE * dir_y, x_square_start)

            old_y = y_first_axis
            for x_square in range(round_down_to_nearest(x_square_start + SQUARE_SIZE), x_square_end, SQUARE_SIZE):
                y_square = round_down_to_nearest(f(x_square + SQUARE_SIZE))
                add_column_squares(old_y, y_square + dir_y, SQUARE_SIZE * dir_y, x_square)
                old_y = y_square

            # End
            add_column_squares(old_y, y_square_end + dir_y, SQUARE_SIZE * dir_y, x_square_end)

            return output_squares

        # Line 1 = Border left
        x1_l1, y1_l1 = x1 + buffer_distance * dxnp, y1 + buffer_distance * dynp
        x2_l1, y2_l1 = x2 + buffer_distance * dxnp, y2 + buffer_distance * dynp
        # Line 2 = Border right
        x1_l2, y1_l2 = x1 + buffer_distance * -dxnp, y1 + buffer_distance * -dynp
        x2_l2, y2_l2 = x2 + buffer_distance * -dxnp, y2 + buffer_distance * -dynp

        number_of_lines = int(buffer_distance * 2 / SQUARE_SIZE - 1)

        offset_x = SQUARE_SIZE * -dxnp
        offset_y = SQUARE_SIZE * -dynp

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
                    (x_corner - SQUARE_SIZE, y_corner),
                    (x_corner, y_corner - SQUARE_SIZE),
                    (x_corner - SQUARE_SIZE, y_corner - SQUARE_SIZE))

        x_initial_square, y_initial_square = get_square(x, y)
        edge_squares = {(x_initial_square, y_initial_square)}
        n_ring = 0
        while n_ring * SQUARE_SIZE <= buffer_distance:
            for i in range(-n_ring, n_ring + 1):
                for j in range(-n_ring, n_ring + 1):
                    corners = [
                        (x_initial_square + j * SQUARE_SIZE, y_initial_square + i * SQUARE_SIZE),
                        (x_initial_square + j * SQUARE_SIZE, y_initial_square + (i + 1) * SQUARE_SIZE),
                        (x_initial_square + (j + 1) * SQUARE_SIZE, y_initial_square + i * SQUARE_SIZE),
                        (x_initial_square + (j + 1) * SQUARE_SIZE, y_initial_square + (i + 1) * SQUARE_SIZE)
                    ]

                    edge_squares.update(
                        square
                        for corner in corners if is_within_distance(*corner)
                        for square in get_squares_from_corner(*corner)
                    )

                    # Ring squares in the same line or column as the vertex's initial square can be both under buffer
                    # distance and not having their corner detected
                    if i == 0:  # Same line
                        x_local = x_initial_square + j * SQUARE_SIZE
                        if is_within_distance(x_local, y) or is_within_distance(x_local + SQUARE_SIZE, y):
                            edge_squares.add(get_square(x_local, y))
                    if j == 0:  # Same column
                        y_local = y_initial_square + i * SQUARE_SIZE
                        if is_within_distance(x, y_local) or is_within_distance(x, y_local + SQUARE_SIZE):
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
        ((y1, x1), (y2, x2)) = (to_crs.transform(*vertex) for vertex in segment)

        segment_squares = (get_squares_from_vertex(x1, y1) |
                           get_squares_from_edge(x1, y1, x2, y2) |
                           get_squares_from_vertex(x2, y2))

        return get_color_from_squares(segment_squares)

    progress_callback(0)
    colored_gaz_df = gaz_df.copy()

    total_segments = len(colored_gaz_df)

    iterator = tqdm(enumerate(colored_gaz_df.itertuples()), desc="Calculating colors", total=total_segments) \
        if show_tqdm else enumerate(colored_gaz_df.itertuples())

    for idx, row in iterator:
        color = get_color_from_segment(row.coordinates)
        colored_gaz_df.at[row.Index, 'color'] = color
        if idx % 100 == 0:
            progress_callback(int((idx / total_segments) * 80))

    return colored_gaz_df
