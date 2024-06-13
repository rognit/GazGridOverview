import pandas as pd
import json
import customtkinter
from tkintermapview import TkinterMapView

customtkinter.set_default_color_theme("blue")

# Load the CSV file
csv_file = 'resources/grt.csv'
df = pd.read_csv(csv_file, delimiter=';')

# Function to extract coordinates from the geo_shape column
def extract_coordinates(geo_shape):
    geo_shape_dict = json.loads(geo_shape)
    coordinates = geo_shape_dict['coordinates']
    swapped_coordinates = [(lat, lon) for lon, lat in coordinates]
    return swapped_coordinates

# Apply the function to the geo_shape column to create a new coordinates column
df['coordinates'] = df['geo_shape'].apply(extract_coordinates)

# Create a dictionary of DataFrames, one for each region
regions = df['nom_region'].unique()
region_dfs = {region: df[df['nom_region'] == region] for region in regions}

# Create a dictionary to store the number of sections for each region
region_counts = {region: len(region_dfs[region]) for region in regions}

# Create a dictionary to store the display names for the dropdown menu
region_display_names = {region: f"{region} ({count})" for region, count in region_counts.items()}

# Add the "-----Empty----- (0)" option
region_display_names["-----Empty-----"] = "-----Empty----- (0)"

# Reverse the dictionary for easy lookup during region selection
display_to_region = {v: k for k, v in region_display_names.items()}

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
        self.frame_left.grid_rowconfigure(1, weight=0)
        self.frame_left.grid_rowconfigure(2, weight=1)
        self.frame_left.grid_rowconfigure(3, weight=0)
        self.frame_left.grid_rowconfigure(4, weight=0)
        self.frame_left.grid_rowconfigure(5, weight=0)
        self.frame_left.grid_rowconfigure(6, weight=0)

        self.region_label = customtkinter.CTkLabel(self.frame_left, text="Region:", anchor="w")
        self.region_label.grid(row=0, column=0, padx=(20, 20), pady=(20, 0))
        self.region_option_menu = customtkinter.CTkOptionMenu(self.frame_left, values=list(region_display_names.values()),
                                                              command=self.change_region)
        self.region_option_menu.grid(row=1, column=0, padx=(20, 20), pady=(10, 0))

        self.map_label = customtkinter.CTkLabel(self.frame_left, text="Background:", anchor="w")
        self.map_label.grid(row=3, column=0, padx=(20, 20), pady=(20, 0))
        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left, values=["OpenStreetMap", "Google normal", "Google satellite"],
                                                           command=self.change_map)
        self.map_option_menu.grid(row=4, column=0, padx=(20, 20), pady=(10, 0))

        self.appearance_mode_label = customtkinter.CTkLabel(self.frame_left, text="Appearance:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=(20, 20), pady=(20, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.frame_left, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=(20, 20), pady=(10, 20))

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
        self.region_option_menu.set("-----Empty----- (0)")

        # Initial region display
        self.change_region("-----Empty----- (0)")

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
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        elif new_map == "Google Map (satellite)":
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

    def change_region(self, display_name):
        self.map_widget.delete_all_path()
        if display_name == "-----Empty----- (0)":
            return
        region = display_to_region[display_name]
        for index, row in region_dfs[region].iterrows():
            coordinates = row['coordinates']
            self.map_widget.set_path(coordinates)

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.start()
