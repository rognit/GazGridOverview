import pandas as pd





df_grt = pd.read_csv('../resources/raw/grt.csv', delimiter=';')
df_terega = pd.read_csv('../resources/raw/terega.csv', delimiter=';')

df_grt_filtered = df_grt[['nom_region', 'geo_point_2d', 'geo_shape']]
df_terega_filtered = df_terega[['region', 'geo_point_2d', 'geo_shape']]

df_grt.rename(columns={'nom_region': 'region'}, inplace=True)

merged_df = pd.concat([df_grt, df_grt])

if 'objectid' in merged_df.columns:
    merged_df.drop(columns=['objectid'], inplace=True)

merged_df.to_csv('../resources/gaz_network.csv', index=False)
