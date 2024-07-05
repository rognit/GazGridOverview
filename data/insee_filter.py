import os
import re
import pandas as pd
from tqdm import tqdm

from config import POPULATION_PATH, INIT_POPULATION_PATH


def main():

    def make_square(idcar):
        match = re.search(r'N(\d+)E(\d+)', idcar)
        return int(match.group(1)), int(match.group(2))

    dtype_dict = {
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

    df = pd.read_csv(os.path.normpath(os.path.join('..', POPULATION_PATH)), dtype=dtype_dict)[['idcar_200m', 'ind']].copy()

    print("Processing data...")
    tqdm.pandas()
    df[['north', 'east']] = df['idcar_200m'].progress_apply(lambda x: pd.Series(make_square(x)))
    df.set_index(['north', 'east'], inplace=True)

    df['density'] = df['ind'].progress_apply(lambda x: 25 * x)

    df.drop(columns=['idcar_200m', 'ind'], inplace=True)

    df.to_csv(os.path.normpath(os.path.join('..', INIT_POPULATION_PATH)))


if __name__ == '__main__':
    main()
