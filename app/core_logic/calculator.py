import pandas as pd

from app.core_logic.path_maker import make_paths
from app.core_logic.network_simplifier import simplify_segments

from app.core_logic.segment_colorist import color_segments
from config import *


def compute_parameters(gaz_df, pop_df,
                       buffer_distance=BUFFER_DISTANCE,
                       orange_threshold=ORANGE_THRESHOLD,
                       red_threshold=RED_THRESHOLD,
                       merging_threshold=MERGING_THRESHOLD,
                       progress_callback=None,
                       show_tqdm=False):


    progress_callback(0)

    exhaustive_gaz_df = color_segments(gaz_df, pop_df, buffer_distance, orange_threshold, red_threshold, progress_callback,show_tqdm)

    simplified_gaz_df = simplify_segments(exhaustive_gaz_df, merging_threshold, show_tqdm)

    progress_callback(85)

    # We want to highlight the issues above. So green will be drawn under yellow, then yellow under orange, etc.
    color_order = pd.CategoricalDtype(categories=['green', 'yellow', 'orange', 'brown', 'red'], ordered=True)
    exhaustive_gaz_df['color'] = exhaustive_gaz_df['color'].astype(color_order)
    exhaustive_gaz_df = exhaustive_gaz_df.sort_values(by=['region', 'color'])
    simplified_gaz_df = simplified_gaz_df.sort_values(by=['region', 'color'])

    exhaustive_network_length = exhaustive_gaz_df['length'].sum()
    simplified_network_length = simplified_gaz_df['length'].sum()
    information_df = pd.DataFrame({'exhaustive_network_length': [exhaustive_network_length],
                                   'simplified_network_length': [simplified_network_length]})
    progress_callback(90)
    exhaustive_gaz_df = make_paths(exhaustive_gaz_df, show_tqdm,
                                   desc="Making paths for exhaustive segments region by region")
    progress_callback(95)
    simplified_gaz_df = make_paths(simplified_gaz_df, show_tqdm,
                                   desc="Making paths for simplified segments region by region")

    progress_callback(100)

    return simplified_gaz_df, exhaustive_gaz_df, information_df
