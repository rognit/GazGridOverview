import pandas as pd


def extract_regions(df):
    regions = df['region'].unique()
    region_dfs = {region: df[df['region'] == region] for region in regions}

    region_counts = {region: len(region_dfs[region]) for region in regions}
    region_display_names = {region: f"{region} ({count})" for region, count in region_counts.items()}
    display_to_region = {v: k for k, v in region_display_names.items()}

    return region_dfs, region_display_names, display_to_region
