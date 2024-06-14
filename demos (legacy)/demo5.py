import pandas as pd
import json
import customtkinter
from tkintermapview import TkinterMapView
import numpy as np

customtkinter.set_default_color_theme("blue")

# Load the CSV files
grt_csv_file = '../resources/grt.csv'
terega_csv_file = '../resources/terega.csv'

df_grt = pd.read_csv(grt_csv_file, delimiter=';')
df_terega = pd.read_csv(terega_csv_file, delimiter=';')


# Function to extract coordinates from the geo_shape column
def extract_coordinates(geo_shape, has_altitude=False):
    if isinstance(geo_shape, str):
        geo_shape_dict = json.loads(geo_shape)
        coordinates = geo_shape_dict['coordinates']
        flattened_coordinates = []

        if has_altitude:
            if isinstance(coordinates[0][0], list):
                for segment in coordinates:
                    for lon, lat, alt in segment:
                        flattened_coordinates.append((lat, lon))
            else:
                for lon, lat, alt in coordinates:
                    flattened_coordinates.append((lat, lon))
        else:
            if isinstance(coordinates[0][0], list):
                for segment in coordinates:
                    for lon, lat in segment:
                        flattened_coordinates.append((lat, lon))
            else:
                for lon, lat in coordinates:
                    flattened_coordinates.append((lat, lon))

        return flattened_coordinates
    else:
        return np.nan


# Apply the function to the geo_shape column to create a new coordinates column
df_grt['coordinates'] = df_grt['geo_shape'].apply(extract_coordinates)
df_terega['coordinates'] = df_terega['geo_shape'].apply(lambda x: extract_coordinates(x, has_altitude=True))

# Create a dictionary of DataFrames, one for each region
regions_grt = df_grt['nom_region'].unique()
region_dfs_grt = {region: df_grt[df_grt['nom_region'] == region] for region in regions_grt}

regions_terega = df_terega['region'].unique()
region_dfs_terega = {region: df_terega[df_terega['region'] == region] for region in regions_terega}

# Create a dictionary to store the number of sections for each region
region_counts_grt = {region: len(region_dfs_grt[region]) for region in regions_grt}
region_counts_terega = {region: len(region_dfs_terega[region]) for region in regions_terega}

# Create a dictionary to store the display names for the dropdown menu
region_display_names_grt = {region: f"{region} ({count})" for region, count in region_counts_grt.items()}
region_display_names_terega = {region: f"{region} ({count})" for region, count in region_counts_terega.items()}

# Reverse the dictionary for easy lookup during region selection
display_to_region_grt = {v: k for k, v in region_display_names_grt.items()}
display_to_region_terega = {v: k for k, v in region_display_names_terega.items()}


class App(customtkinter.CTk):
    APP_NAME = "French gaz network overview"
    WIDTH = 800
    HEIGHT = 500

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, App.HEIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.bind("<Command-w>", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)

        self.marker_list = []

        # ============ create two CTkFrames ============

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self, width=150, corner_radius=0, fg_color=None)
        self.frame_left.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.frame_right = customtkinter.CTkFrame(master=self, corner_radius=0)
        self.frame_right.grid(row=0, column=1, rowspan=1, pady=0, padx=0, sticky="nsew")

        # ============ frame_left ============

        self.frame_left.grid_rowconfigure(0, weight=0)
        self.frame_left.grid_rowconfigure(1, weight=0)  # Adjusted row weight for GRTgaz checkboxes
        self.frame_left.grid_rowconfigure(2, weight=0)
        self.frame_left.grid_rowconfigure(3, weight=0)  # Adjusted row weight for Terega checkboxes
        self.frame_left.grid_rowconfigure(4, weight=1)  # Spacer to push dropdowns to the bottom
        self.frame_left.grid_rowconfigure(5, weight=0)
        self.frame_left.grid_rowconfigure(6, weight=0)
        self.frame_left.grid_columnconfigure(0, weight=1)
        self.frame_left.grid_columnconfigure(1, weight=1)

        self.region_label_grt = customtkinter.CTkLabel(self.frame_left, text="GRTgaz Network:", anchor="w")
        self.region_label_grt.grid(row=0, column=0, padx=(20, 20), pady=(20, 0))

        self.region_frame_grt = customtkinter.CTkFrame(self.frame_left, fg_color=None)
        self.region_frame_grt.grid(row=1, column=0, columnspan=2, padx=(20, 20), pady=(10, 0), sticky="n")

        self.region_checkboxes_grt = {}
        for idx, (region, display_name) in enumerate(region_display_names_grt.items()):
            self.region_checkboxes_grt[region] = customtkinter.CTkCheckBox(self.region_frame_grt, text=display_name,
                                                                           command=self.change_region)
            self.region_checkboxes_grt[region].grid(row=idx, column=0, padx=(0, 0), pady=(5, 0), sticky="w")

        self.region_label_terega = customtkinter.CTkLabel(self.frame_left, text="Terega Network:", anchor="w")
        self.region_label_terega.grid(row=2, column=0, padx=(20, 20), pady=(20, 0))

        self.region_frame_terega = customtkinter.CTkFrame(self.frame_left, fg_color=None)
        self.region_frame_terega.grid(row=3, column=0, columnspan=2, padx=(20, 20), pady=(10, 0), sticky="n")

        self.region_checkboxes_terega = {}
        for idx, (region, display_name) in enumerate(region_display_names_terega.items()):
            self.region_checkboxes_terega[region] = customtkinter.CTkCheckBox(self.region_frame_terega,
                                                                              text=display_name,
                                                                              command=self.change_region)
            self.region_checkboxes_terega[region].grid(row=idx, column=0, padx=(0, 0), pady=(5, 0), sticky="w")

        self.map_label = customtkinter.CTkLabel(self.frame_left, text="Background:", anchor="w")
        self.map_label.grid(row=5, column=0, padx=(20, 0), pady=(20, 0))
        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left, values=["OpenStreetMap",
                                                                                    "Google Map (classic)",
                                                                                    "Google Map (satellite)"],
                                                           command=self.change_map)
        self.map_option_menu.grid(row=5, column=1, padx=(0, 20), pady=(20, 0))

        self.appearance_mode_label = customtkinter.CTkLabel(self.frame_left, text="Appearance:", anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=(20, 0), pady=(20, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.frame_left,
                                                                       values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.grid(row=6, column=1, padx=(0, 20), pady=(20, 0))

        # ============ frame_right ============

        self.frame_right.grid_rowconfigure(1, weight=1)
        self.frame_right.grid_rowconfigure(0, weight=0)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(1, weight=0)
        self.frame_right.grid_columnconfigure(2, weight=1)

        self.map_widget = TkinterMapView(self.frame_right, corner_radius=0)
        self.map_widget.grid(row=1, rowspan=1, column=0, columnspan=3, sticky="nswe", padx=(0, 0), pady=(0, 0))

        self.entry = customtkinter.CTkEntry(master=self.frame_right,
                                            placeholder_text="type address")
        self.entry.grid(row=0, column=0, sticky="we", padx=(12, 0), pady=12)
        self.entry.bind("<Return>", self.search_event)

        self.button_5 = customtkinter.CTkButton(master=self.frame_right,
                                                text="Search",
                                                width=90,
                                                command=self.search_event)
        self.button_5.grid(row=0, column=1, sticky="w", padx=(12, 0), pady=12)

        # Set default values
        self.map_widget.set_position(47, 2.5, marker=False)
        self.map_widget.set_zoom(6)
        self.map_option_menu.set("OpenStreetMap")
        self.appearance_mode_optionemenu.set("System")

    def search_event(self, event=None):
        self.map_widget.set_address(self.entry.get())

    def set_marker_event(self):
        current_position = self.map_widget.get_position()
        self.marker_list.append(self.map_widget.set_marker(current_position[0], current_position[1]))

    def clear_marker_event(self):
        for marker in self.marker_list:
            marker.delete()

    def change_appearance_mode(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_map(self, new_map: str):
        if new_map == "OpenStreetMap":
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        elif new_map == "Google Map (classic)":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga",
                                            max_zoom=22)
        elif new_map == "Google Map (satellite)":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga",
                                            max_zoom=22)

    def change_region(self):
        self.map_widget.delete_all_path()
        for region, checkbox in self.region_checkboxes_grt.items():
            if checkbox.get():
                for index, row in region_dfs_grt[region].iterrows():
                    coordinates = row['coordinates']
                    self.map_widget.set_path(coordinates, color="blue")
        for region, checkbox in self.region_checkboxes_terega.items():
            if checkbox.get():
                for index, row in region_dfs_terega[region].iterrows():
                    coordinates = row['coordinates']
                    self.map_widget.set_path(coordinates, color="green")

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()






if __name__ == "__main__":
    app = App()
    app.start()
