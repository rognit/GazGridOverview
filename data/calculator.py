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



def round_down_to_nearest_200(value):
    return int(value // 200 * 200)

def get_square(north_point, east_point):
    return round_down_to_nearest_200(north_point), round_down_to_nearest_200(east_point)

def get_density(north_square, east_point):
    return pop_df.loc[(pop_df['north'] == north_square) & (pop_df['east'] == east_point), 'density'].values[0]

def get_line(x1, y1, x2, y2):
    a = (y2 - y1) / (x2 - x1)
    b = y1 - a * x1
    return lambda x: a * x + b

def get_squares_from_line(north_point_1, east_point_1, north_point_2, east_point_2):

    north_square_1, east_square_1 = get_square(north_point_1, east_point_1)
    north_square_2, east_square_2 = get_square(north_point_2, east_point_2)

    f = get_line(east_point_1, north_point_1, east_point_2, north_point_2)
    direction = 1 if east_point_1 < east_point_2 else -1

    squares = [(north_square_1, east_square_1)]
    old_north_square = north_square_1
    for east_square in range(east_square_1 + 1, east_square_2 + 1, direction * 200):
        north_square = round_down_to_nearest_200(f(east_square))
        for crossed_north_square in range(old_north_square, north_square + 1, 200):
            squares.append(get_square(crossed_north_square, east_square))
        old_north_square = north_square

    return list(set(squares))


def calculate_parallel_lines(vector, d):
    x1, y1, x2, y2 = vector
    dx, dy = x2 - x1, y2 - y1
    length = math.sqrt(dx ** 2 + dy ** 2)

    # Normalized normal vectors
    n1_unit_x, n1_unit_y = -dy / length, dx / length
    n2_unit_x, n2_unit_y = dy / length, -dx / length

    # First parallel line
    x1_l1 = x1 + d * n1_unit_x
    y1_l1 = y1 + d * n1_unit_y
    x2_l1 = x2 + d * n1_unit_x
    y2_l1 = y2 + d * n1_unit_y

    # Second parallel line
    x1_l2 = x1 + d * n2_unit_x
    y1_l2 = y1 + d * n2_unit_y
    x2_l2 = x2 + d * n2_unit_x
    y2_l2 = y2 + d * n2_unit_y

    return (x1_l1, y1_l1, x2_l1, y2_l1), (x1_l2, y1_l2, x2_l2, y2_l2)

def get_squares_from_edge(north_point_1, east_point_1, north_point_2, east_point_2, buffer_distance):
    edge_f = get_line(east_point_1, north_point_1, east_point_2, north_point_2)

def get_square_from_vertex(north_point, east_point):
    return get_square(north_point, east_point)


