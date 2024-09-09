import customtkinter
from colorama import Fore, Back, Style, init

from app.core_logic.calculator import compute_parameters

init(autoreset=True)  # Initialize colorama

def search_event(app, event=None):
    app.map_widget.set_address(app.entry.get())

def format_length(length):
        return f"{length / 1e3:.3f} km"

def on_marker_click(marker, type):
    def pad_line(content, n_color_tags=0):
        padding = max(0, total_width - len(content) - 4 + n_color_tags * 5)  # 4 for "║ " and " ║"
        left_padding = padding // 2
        right_padding = padding - left_padding
        return ' ' * left_padding + content + ' ' * right_padding

    total_width = 70
    region, (lat, lon), green, orange, simplified = marker.data

    green_length = format_length(green)
    orange_length = format_length(orange)
    total_length = format_length(green + orange)
    simplified_length = format_length(simplified)

    header = f"{type} Marker at {Fore.RED}{lat:.5f}, {lon:.5f}{Fore.CYAN} in {region}"

    padding_len = max(0, total_width - len(header) - 4 + 10)  # 4 for "║ " and " ║", 10 for the color codes
    left_padding = padding_len // 2
    right_padding = padding_len - left_padding

    line_green = f"  Exhaustive Green Length : {Fore.WHITE}{green_length} "
    line_orange = f"+ Exhaustive Orange Length: {Fore.WHITE}{orange_length} "
    line_exhaustive = f"Exhaustive Length   : {Fore.WHITE}{total_length}"
    line_simplified = f"Simplified Length   : {Fore.WHITE}{simplified_length}"

    log = f"{Fore.CYAN}╔{'═' * left_padding} {header} {'═' * right_padding}╗\n"
    if type == 'Green':
        log += (f"{Fore.CYAN}║ {Fore.MAGENTA}{pad_line(line_exhaustive, 1)}{Fore.CYAN} ║\n"
                f"{Fore.CYAN}║ {Fore.BLUE}{pad_line(line_simplified, 1)}{Fore.CYAN} ║\n")
    elif type == 'Orange':
        log += (f"{Fore.CYAN}║ {Fore.GREEN}{pad_line(line_green, 1)}{Fore.CYAN} ║\n"
                f"{Fore.CYAN}║ {Fore.YELLOW}{pad_line(line_orange, 1)}{Fore.CYAN} ║\n"
                f"{Fore.CYAN}║ {Fore.MAGENTA}{pad_line(f"=     {line_exhaustive}", 1)}{Fore.CYAN} ║\n"
                f"{Fore.CYAN}║ {Fore.BLUE}{pad_line(f"  ↳   [ {line_simplified} {Fore.BLUE}] ", 2)}{Fore.CYAN} ║\n")

    log += f"{Fore.CYAN}╚{'═' * (total_width - 2)}╝{Style.RESET_ALL}\n"

    print(log)


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
                        marker = app.map_widget.set_marker(
                            *row['coordinates'],
                            text=f"{format_length(row['green_quantity'])}",
                            marker_color_circle="#3ef50a",
                            marker_color_outside="#1d8001",
                            command=lambda marker=row: on_marker_click(marker, 'Green')
                        )
                        marker.data = row
                for _, row in app.orange_marker_df.iterrows():
                    quantity = row['orange_quantity'] + row['green_quantity']
                    if quantity > int(app.showing_marker_threshold_entry.get()) and row['region'] == region:
                        marker = app.map_widget.set_marker(
                            *row['coordinates'],
                            text=f"{format_length(quantity)}",
                            marker_color_circle="#f5a623",
                            marker_color_outside="#b86b00",
                            command=lambda marker=row: on_marker_click(marker, 'Orange')
                        )
                        marker.data = row


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
