import os

import pandas as pd

from config import *
from app.calculator import compute_parameters
from app.pre_processing import process_gaz, process_pop


def main():
    dtype_pop_dict = {
        'idcar_200m': str,
        'idcar_1km': str,
        'idcar_nat': str,
        'i_est_200': int,
        'i_est_1km': int,
        'lcog_geo': str,
        'ind': float,
        'men': float,
        'men_pauv': float,
        'men_1ind': float,
        'men_5ind': float,
        'men_prop': float,
        'men_fmp': float,
        'ind_snv': float,
        'men_surf': float,
        'men_coll': float,
        'men_mais': float,
        'log_av45': float,
        'log_45_70': float,
        'log_70_90': float,
        'log_ap90': float,
        'log_inc': float,
        'log_soc': float,
        'ind_0_3': float,
        'ind_4_5': float,
        'ind_6_10': float,
        'ind_11_17': float,
        'ind_18_24': float,
        'ind_25_39': float,
        'ind_40_54': float,
        'ind_55_64': float,
        'ind_65_79': float,
        'ind_80p': float,
        'ind_inc': float
    }

    raw_df_pop = pd.read_csv(os.path.normpath(INIT_POPULATION_PATH), dtype=dtype_pop_dict)[
        ['idcar_200m', 'ind']].copy()
    raw_df_grt = pd.read_csv(os.path.normpath(INIT_GRT_PATH), delimiter=';')
    raw_df_terega = pd.read_csv(os.path.normpath(INIT_TEREGA_PATH), delimiter=';')

    df_gaz = process_gaz(raw_df_grt, raw_df_terega)
    df_pop = process_pop(raw_df_pop)

    df_gaz.to_csv(os.path.normpath(BASE_GAZ_NETWORK_PATH), index=False)
    df_pop.to_csv(os.path.normpath(BASE_POPULATION_PATH))

    print("Initial computing with preset parameters...")
    computed_df = compute_parameters(df_gaz, df_pop, progress_callback=lambda x: None)

    computed_df.to_csv(os.path.normpath(COMPUTED_GAZ_NETWORK_PATH), index=False)

    print("\n\nSetup completed successfully!\n\n")


if __name__ == '__main__':
    main()
