import customtkinter

from app.core_logic.calculator import compute_parameters
from config import *


def search_event(app, event=None):
    app.map_widget.set_address(app.entry.get())


def change_region(app):
    app.map_widget.delete_all_path()
    app.map_widget.delete_all_marker()
    for region, checkbox in app.region_checkboxes_gaz.items():
        if checkbox.get():
            for _, row in app.region_dfs_gaz[region].iterrows():
                app.map_widget.set_path(row['coordinates'], color=row['color'])
            if app.markers_toggle_switch.get() == 1:
                for _, row in app.green_marker_df.iterrows():
                    if row['green_quantity'] > int(app.showing_marker_threshold_entry.get()) and row['region'] == region:
                        app.map_widget.set_marker(*row['coordinates'], text=f"{row['green_quantity'] / 1e3:.3f} km",
                                                   marker_color_circle="#3ef50a", marker_color_outside="#1d8001")
                for _, row in app.orange_marker_df.iterrows():
                    quantity = row['orange_quantity'] + row['green_quantity']
                    if quantity > int(app.showing_marker_threshold_entry.get()) and row['region'] == region:
                        app.map_widget.set_marker(*row['coordinates'], text=f"{quantity / 1e3:.3f} km",
                                                   marker_color_circle="#f5a623", marker_color_outside="#b86b00")


def change_map(app, new_map):
    if new_map == "Open Street Map":
        app.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
    elif new_map == "Google Map (classic)":
        app.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
    elif new_map == "Google Map (satellite)":
        app.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)


def change_appearance_mode(app, new_appearance_mode):
    customtkinter.set_appearance_mode(new_appearance_mode)


def toggle_view_mode(app):
    if app.view_mode_toggle_switch.get() == 0:  # Switch is off (Exhaustive view)
        app.view_mode = "exhaustive"
        app.gaz_df = app.exhaustive_gaz_df
        app.view_mode_toggle_switch.configure(text="Exhaustive View")
    else:  # Switch is on (Simplified view)
        app.view_mode = "simplified"
        app.gaz_df = app.simplified_gaz_df
        app.view_mode_toggle_switch.configure(text="Simplified View")

    app.extract_regions()
    change_region(app)

def toggle_markers(app):
    if app.markers_toggle_switch.get() == 0:  # Switch is off (Hide markers)
        app.map_widget.delete_all_marker()
    else:  # Switch is on (Show markers)
        change_region(app)

def recalculate_segments(app):

    app.simplified_gaz_df, app.exhaustive_gaz_df, app.information_df, app.green_marker_df, app.orange_marker_df = \
        compute_parameters(
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
