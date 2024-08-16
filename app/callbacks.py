# callbacks.py
import ast
import customtkinter
from scipy.interpolate import approximate_taylor_polynomial

from app.core_logic.calculator import compute_parameters


def search_event(app, event=None):
    app.map_widget.set_address(app.entry.get())


def change_region(app):
    app.map_widget.delete_all_path()
    for region, checkbox in app.region_checkboxes_gaz.items():
        if checkbox.get():
            for index, row in app.region_dfs_gaz[region].iterrows():
                coordinates = ast.literal_eval(row['coordinates']) if isinstance(row['coordinates'], str)\
                    else row['coordinates']
                app.map_widget.set_path(coordinates, color=row['color'])


def change_map(app, new_map):
    if new_map == "Open Street Map":
        app.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
    elif new_map == "Google Map (classic)":
        app.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
    elif new_map == "Google Map (satellite)":
        app.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)


def change_appearance_mode(app, new_appearance_mode):
    customtkinter.set_appearance_mode(new_appearance_mode)


def toggle_view_mode(self):
    if self.toggle_switch.get() == 0:  # Switch is off (Exhaustive view)
        self.view_mode = "exhaustive"
        self.gaz_df = self.exhaustive_gaz_df
        self.toggle_switch.configure(text="Exhaustive View")
    else:  # Switch is on (Simplified view)
        self.view_mode = "simplified"
        self.gaz_df = self.simplified_gaz_df
        self.toggle_switch.configure(text="Simplified View")

    self.extract_regions()
    change_region(self)


def recalculate_segments(app):

    app.simplified_gaz_df, app.exhaustive_gaz_df, app.information_df = compute_parameters(
        app.base_gaz_network_path,
        app.pop_df,
        buffer_distance= int(app.buffer_distance_entry.get()),
        orange_threshold= int(app.orange_threshold_entry.get()),
        red_threshold=int(app.red_threshold_entry.get()),
        merging_threshold=int(app.merging_threshold_entry.get()),
        progress_callback=app.update_progress
    )

    app.exhaustive_network_length, app.simplified_network_length = app.information_df.iloc[0]
    app.gaz_df = app.exhaustive_gaz_df if app.view_mode == "exhaustive" else app.simplified_gaz_df

    app.extract_regions()
    change_region(app)
    app.hide_loading_screen()
