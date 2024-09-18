import pandas as pd
from tqdm import tqdm

def make_paths(df, show_tqdm, desc):
    def merge_region_color_segments(df):
        def common_point(seg0, group):
            for seg, _ in group:
                if seg0[0] in seg or seg0[1] in seg:
                    return True
            return False

        def recursive_merge(paths):
            for i, (path1, length1) in enumerate(paths):
                for j, (path2, length2) in enumerate(paths):
                    if i != j:
                        if path1[-1] == path2[0]:
                            return recursive_merge(
                                [p for k, p in enumerate(paths) if i != k != j] + [(path1 + path2[1:], length1 + length2)])
                        elif path1[0] == path2[-1]:
                            return recursive_merge(
                                [p for k, p in enumerate(paths) if i != k != j] + [(path2 + path1[1:], length1 + length2)])
                        elif path1[0] == path2[0]:
                            return recursive_merge(
                                [p for k, p in enumerate(paths) if i != k != j] + [(path2[::-1] + path1[1:], length1 + length2)])
                        elif path1[-1] == path2[-1]:
                            return recursive_merge(
                                [p for k, p in enumerate(paths) if i != k != j] + [(path1 + path2[::-1][1:], length1 + length2)])
            return paths

        # Making groups of segment that share at least one common point
        groups = []
        for row in df.itertuples():
            seg0 = row.coordinates
            length0 = row.length
            relevant_groups = []
            for i, group in enumerate(groups):
                if common_point(seg0, group):
                    relevant_groups.append(i)
            if relevant_groups:
                new_group = [(seg0, length0)]
                for i in sorted(relevant_groups, reverse=True):
                    new_group.extend(groups.pop(i))
                groups.append(new_group)
            else:
                groups.append([(seg0, length0)])

        # Merge segments into a minimum of paths
        paths = []
        for group in groups:
            paths.extend(recursive_merge(group))
        return paths

    merged_section = []

    iterator = tqdm(df['region'].unique(), desc=desc, total=len(df['region'].unique())) \
        if show_tqdm else df['region'].unique()

    for region in iterator:
        region_df = df[df['region'] == region]
        for color in region_df['color'].unique():
            color_df = region_df[region_df['color'] == color]
            merged_segments = merge_region_color_segments(color_df)
            for section, length in merged_segments:
                merged_section.append({'region': region, 'color': color, 'coordinates': section, 'length': length})

    out = pd.DataFrame(merged_section)
    return out