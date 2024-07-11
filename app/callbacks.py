import ast
import customtkinter

from data.calculator import compute_parameters


def search_event(app, event=None):
    app.map_widget.set_address(app.entry.get())


def change_region(app):
    app.map_widget.delete_all_path()
    for region, checkbox in app.region_checkboxes_gaz.items():
        if checkbox.get():
            for index, row in app.region_dfs_gaz[region].iterrows():
                app.map_widget.set_path(ast.literal_eval(row['coordinates']), color=row['color'])


def change_map(app, new_map):
    if new_map == "OpenStreetMap":
        app.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
    elif new_map == "Google Map (classic)":
        app.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
    elif new_map == "Google Map (satellite)":
        app.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)


def change_appearance_mode(app, new_appearance_mode):
    customtkinter.set_appearance_mode(new_appearance_mode)


def recalculate_segments(app):
    buffer_distance = int(app.buffer_distance_entry.get())
    orange_threshold = int(app.orange_threshold_entry.get())
    red_threshold = int(app.red_threshold_entry.get())

    app.colored_gaz_network, app.gaz_df = compute_parameters(
        app.gaz_network,
        app.pop_df,
        buffer_distance,
        orange_threshold,
        red_threshold
    )

    app.extract_regions()

    change_region(app)
