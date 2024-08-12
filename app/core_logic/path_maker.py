import ast

import pandas as pd


def merge_region_color_segments(df):
    def parse_segment(segment):
        return ast.literal_eval(segment.strip()) if isinstance(segment, str) else segment

    def comon_point(seg0, group):
        for seg in group:
            if seg0[0] in seg or seg0[1] in seg:
                return True
        return False

    def recursive_merge(paths):
        for i, path1 in enumerate(paths):
            for j, path2 in enumerate(paths):
                if i != j:
                    if path1[-1] == path2[0]:
                        return recursive_merge(
                            [path for k, path in enumerate(paths) if i != k != j] + [path1 + path2[1:]])
                    elif path1[0] == path2[-1]:
                        return recursive_merge(
                            [path for k, path in enumerate(paths) if i != k != j] + [path2 + path1[1:]])
                    elif path1[0] == path2[0]:
                        return recursive_merge(
                            [path for k, path in enumerate(paths) if i != k != j] + [path2[::-1] + path1[1:]])
                    elif path1[-1] == path2[-1]:
                        return recursive_merge(
                            [path for k, path in enumerate(paths) if i != k != j] + [path1 + path2[::-1][1:]])
        return paths

    # Making groups of segment that share at least one comon point
    groups = []
    for row in df.itertuples():
        seg0 = parse_segment(row.coordinates)
        relevant_groups = []
        for i, group in enumerate(groups):
            if comon_point(seg0, group):
                relevant_groups.append(i)
        if relevant_groups:
            new_group = [seg0]
            for i in sorted(relevant_groups, reverse=True):
                new_group.extend(groups.pop(i))
            groups.append(new_group)
        else:
            groups.append([seg0])

    # Merge segments into a minimum of paths
    paths = []
    for group in groups:
        paths.extend(map(list, recursive_merge(group)))
    return paths


def merge_all_segments(df):
    merged_section = []
    for region in df['region'].unique():
        region_df = df[df['region'] == region]
        for color in region_df['color'].unique():
            color_df = region_df[region_df['color'] == color]
            merged_segments = merge_region_color_segments(color_df)
            for section in merged_segments:
                merged_section.append({'region': region, 'color': color, 'coordinates': section})

    out = pd.DataFrame(merged_section)
    return out
