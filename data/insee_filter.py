import pandas as pd


columns_to_keep = [
    'idcar_200m',
    'idcar_1km',
    'idcar_nat',
    'i_est_200',
    'i_est_1km',
    'lcog_geo',
    'ind'
]


df = pd.read_csv('../resources/test_pop.csv')
filtered_df = df[columns_to_keep]
filtered_df.to_csv('../resources/test_pop_filtered.csv', index=False)

