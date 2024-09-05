import customtkinter
import pandas as pd

from threading import Thread
from tkintermapview import TkinterMapView
from tkinter import ttk

from app.callbacks import change_region, change_map, change_appearance_mode, search_event, recalculate_segments, \
    toggle_view_mode, toggle_markers
from config import *


class App(customtkinter.CTk):
    APP_NAME = "Gaz Grid Overview"
    WIDTH = 1400
    HEIGHT = 1000

    def __init__(self, base_gaz_network_path, base_population_path, simplified_gaz_network_path,
                 exhaustive_gaz_network_path, information_path, green_marker_path, orange_marker_path, icon_path):
        super().__init__()
        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, self.HEIGHT)
        self.iconbitmap(icon_path)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.bind("<Command-w>", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)

        self.base_gaz_network_path = pd.read_csv(base_gaz_network_path)
        self.base_gaz_network_path['coordinates'] = self.base_gaz_network_path['coordinates'].apply(lambda x: eval(x))

        self.pop_df = pd.read_csv(base_population_path)
        self.pop_df.set_index(['north', 'east'], inplace=True)

        self.simplified_gaz_df = pd.read_csv(simplified_gaz_network_path)
        self.simplified_gaz_df['coordinates'] = self.simplified_gaz_df['coordinates'].apply(lambda x: eval(x))

        self.exhaustive_gaz_df = pd.read_csv(exhaustive_gaz_network_path)
        self.exhaustive_gaz_df['coordinates'] = self.exhaustive_gaz_df['coordinates'].apply(lambda x: eval(x))

        self.information_df = pd.read_csv(information_path)
        self.exhaustive_network_length, self.simplified_network_length = self.information_df.iloc[0]

        self.green_marker_df = pd.read_csv(green_marker_path)
        self.green_marker_df['coordinates'] = self.green_marker_df['coordinates'].apply(lambda x: eval(x))

        self.orange_marker_df = pd.read_csv(orange_marker_path)
        self.orange_marker_df['coordinates'] = self.orange_marker_df['coordinates'].apply(lambda x: eval(x))

        self.view_mode = "exhaustive"
        self.gaz_df = self.exhaustive_gaz_df

        self.loading_screen = None
        self.progress_var = None
        self.progress_bar = None

        self.extract_regions()
        self.setup_ui()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self, width=150, corner_radius=0, fg_color=None)
        self.frame_left.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        self.frame_right = customtkinter.CTkFrame(master=self, corner_radius=0)
        self.frame_right.grid(row=0, column=1, rowspan=1, pady=0, padx=0, sticky="nsew")

        self.create_left_frame()
        self.create_right_frame()

    def extract_regions(self):
        regions = self.gaz_df['region'].unique()
        self.region_dfs_gaz = {
            region: self.gaz_df[self.gaz_df['region'] == region] for region in regions
        }
        self.region_dfs_green_marker = {
            region: self.green_marker_df[self.green_marker_df['region'] == region] for region in regions
        }
        self.region_dfs_orange_marker = {
            region: self.orange_marker_df[self.orange_marker_df['region'] == region] for region in regions
        }

        region_counts = {region: len(self.region_dfs_gaz[region]) for region in regions}
        self.region_display_names_gaz = {region: f"{region} ({count})" for region, count in region_counts.items()}

        # Refreshing the display of region labels because their paths number has surely changed
        if hasattr(self, 'region_checkboxes_gaz'):
            for region, display_name in self.region_display_names_gaz.items():
                if region in self.region_checkboxes_gaz:
                    self.region_checkboxes_gaz[region].configure(text=display_name)

    def create_left_frame(self):
        self.frame_left.grid_rowconfigure(0, weight=0)  # Toggle buttons frame
        self.frame_left.grid_rowconfigure(1, weight=0)  # Region checkboxes frame
        self.frame_left.grid_rowconfigure(2, weight=0)  # Parameters frame
        self.frame_left.grid_rowconfigure(3, weight=0)  # Network info frame
        self.frame_left.grid_rowconfigure(4, weight=1)  # Spacer
        self.frame_left.grid_rowconfigure(5, weight=0)  # Background
        self.frame_left.grid_rowconfigure(6, weight=0)  # Appearance

        self.frame_left.grid_columnconfigure(0, weight=1)

        # Toggle buttons frame
        self.toggle_frame = customtkinter.CTkFrame(self.frame_left, fg_color=None)
        self.toggle_frame.grid(row=0, column=0, padx=(20, 20), pady=(20, 10), sticky="ew")

        self.markers_toggle_switch = customtkinter.CTkSwitch(self.toggle_frame, text="Markers",
                                                             font=("Helvetica", 16, "bold"),
                                                             command=lambda: toggle_markers(self))
        self.markers_toggle_switch.grid(row=0, column=0, padx=(0, 10), pady=(0, 0), sticky="w")

        self.view_mode_toggle_switch = customtkinter.CTkSwitch(self.toggle_frame, text="Simplified View",
                                                               font=("Helvetica", 16, "bold"),
                                                               command=lambda: toggle_view_mode(self))
        self.view_mode_toggle_switch.grid(row=0, column=1, padx=(10, 0), pady=(0, 0), sticky="w")

        # Region frame
        self.region_frame_gaz = customtkinter.CTkFrame(self.frame_left, fg_color=None)
        self.region_frame_gaz.grid(row=1, column=0, padx=(20, 20), pady=(10, 20), sticky="nsew")

        self.region_label_gaz = customtkinter.CTkLabel(self.region_frame_gaz, text="Select regions",
                                                       font=("Helvetica", 16, "bold"))
        self.region_label_gaz.grid(row=0, column=0, padx=(0, 0), pady=(0, 10), sticky="n")
        self.region_frame_gaz.grid_columnconfigure(0, weight=1)

        self.region_checkboxes_gaz = {}
        for idx, (region, display_name) in enumerate(self.region_display_names_gaz.items()):
            self.region_checkboxes_gaz[region] = customtkinter.CTkCheckBox(self.region_frame_gaz, text=display_name,
                                                                           command=lambda: change_region(self))
            self.region_checkboxes_gaz[region].grid(row=idx + 1, column=0, padx=(0, 0), pady=(5, 0), sticky="w")

        # Parameters frame
        self.param_frame = customtkinter.CTkFrame(self.frame_left, fg_color=None)
        self.param_frame.grid(row=2, column=0, padx=(20, 20), pady=(10, 20), sticky="nsew")

        self.buffer_distance_label = customtkinter.CTkLabel(self.param_frame, text="Buffer Distance:  ", anchor="w")
        self.buffer_distance_label.grid(row=0, column=0, padx=(20, 0), pady=(10, 0), sticky="e")
        self.buffer_distance_entry = customtkinter.CTkEntry(self.param_frame, width=80, border_width=2, border_color="green")
        self.buffer_distance_entry.grid(row=0, column=1, padx=(0, 5), pady=(10, 0), sticky="w")
        self.buffer_distance_unit = customtkinter.CTkLabel(self.param_frame, text="meters", anchor="w")
        self.buffer_distance_unit.grid(row=0, column=2, padx=(0, 20), pady=(10, 0), sticky="w")

        self.orange_threshold_label = customtkinter.CTkLabel(self.param_frame, text="Orange Threshold:  ", anchor="w")
        self.orange_threshold_label.grid(row=1, column=0, padx=(20, 0), pady=(10, 0), sticky="e")
        self.orange_threshold_entry = customtkinter.CTkEntry(self.param_frame, width=80, border_width=2, border_color="orange")
        self.orange_threshold_entry.grid(row=1, column=1, padx=(0, 5), pady=(10, 0), sticky="w")
        self.orange_threshold_unit = customtkinter.CTkLabel(self.param_frame, text="hab/km²", anchor="w")
        self.orange_threshold_unit.grid(row=1, column=2, padx=(0, 20), pady=(10, 0), sticky="w")

        self.red_threshold_label = customtkinter.CTkLabel(self.param_frame, text="Red Threshold:  ", anchor="w")
        self.red_threshold_label.grid(row=2, column=0, padx=(20, 0), pady=(10, 0), sticky="e")
        self.red_threshold_entry = customtkinter.CTkEntry(self.param_frame, width=80, border_width=2, border_color="red")
        self.red_threshold_entry.grid(row=2, column=1, padx=(0, 5), pady=(10, 0), sticky="w")
        self.red_threshold_unit = customtkinter.CTkLabel(self.param_frame, text="hab/km²", anchor="w")
        self.red_threshold_unit.grid(row=2, column=2, padx=(0, 20), pady=(10, 0), sticky="w")

        self.merging_threshold_label = customtkinter.CTkLabel(self.param_frame, text="Merging Threshold:  ", anchor="w")
        self.merging_threshold_label.grid(row=3, column=0, padx=(20, 0), pady=(10, 0), sticky="e")
        self.merging_threshold_entry = customtkinter.CTkEntry(self.param_frame, width=80, border_width=2, border_color="purple")
        self.merging_threshold_entry.grid(row=3, column=1, padx=(0, 5), pady=(10, 0), sticky="w")
        self.merging_threshold_unit = customtkinter.CTkLabel(self.param_frame, text="meters", anchor="w")
        self.merging_threshold_unit.grid(row=3, column=2, padx=(0, 20), pady=(10, 0), sticky="w")

        self.showing_marker_threshold_label = customtkinter.CTkLabel(self.param_frame, text="Marker Threshold:  ", anchor="w")
        self.showing_marker_threshold_label.grid(row=4, column=0, padx=(20, 0), pady=(10, 0), sticky="e")
        self.showing_marker_threshold_entry = customtkinter.CTkEntry(self.param_frame, width=80, border_width=2, border_color="blue")
        self.showing_marker_threshold_entry.grid(row=4, column=1, padx=(0, 5), pady=(10, 0), sticky="w")
        self.showing_marker_threshold_unit = customtkinter.CTkLabel(self.param_frame, text="meters", anchor="w")
        self.showing_marker_threshold_unit.grid(row=4, column=2, padx=(0, 20), pady=(10, 0), sticky="w")

        self.recalculate_button = customtkinter.CTkButton(self.param_frame, text="Recalculate", command=lambda: self.start_recalculation())
        self.recalculate_button.grid(row=5, column=0, columnspan=3, padx=(20, 20), pady=(10, 20))

        # Network info frame
        self.network_info_frame = customtkinter.CTkFrame(self.frame_left, fg_color=None)
        self.network_info_frame.grid(row=4, column=0, columnspan=2, padx=(20, 20), pady=(20, 10), sticky="ew")

        self.exhaustive_network_text_label = customtkinter.CTkLabel(self.network_info_frame, text="Exhaustive network length :  ", font=("Helvetica", 14))
        self.exhaustive_network_text_label.grid(row=0, column=0, padx=(10, 0), pady=(5, 5), sticky="e")
        self.exhaustive_network_length_label = customtkinter.CTkLabel(self.network_info_frame,
            text=f"{self.exhaustive_network_length / 1000:,.3f} km".replace(",", " "), font=("Helvetica", 14, "bold"))
        self.exhaustive_network_length_label.grid(row=0, column=1, padx=(0, 10), pady=(5, 5), sticky="w")

        self.simplified_network_text_label = customtkinter.CTkLabel(self.network_info_frame, text="Simplified network length :  ", font=("Helvetica", 14))
        self.simplified_network_text_label.grid(row=1, column=0, padx=(10, 0), pady=(5, 5), sticky="e")
        self.simplified_network_length_label = customtkinter.CTkLabel(self.network_info_frame,
            text=f"{self.simplified_network_length / 1000:,.3f} km".replace(",", " "), font=("Helvetica", 14, "bold"))
        self.simplified_network_length_label.grid(row=1, column=1, padx=(0, 10), pady=(5, 5), sticky="w")

        # Background and appearance options
        self.map_label = customtkinter.CTkLabel(self.frame_left, text="Background:", anchor="w")
        self.map_label.grid(row=5, column=0, padx=(20, 20), pady=(10, 10), sticky="sw")
        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left,
                                                           values=["Open Street Map", "Google Map (classic)",
                                                                   "Google Map (satellite)"],
                                                           command=lambda new_map: change_map(self, new_map))
        self.map_option_menu.grid(row=5, column=0, padx=(20, 20), pady=(10, 10), sticky="se")

        self.appearance_mode_label = customtkinter.CTkLabel(self.frame_left, text="Appearance:", anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=(20, 20), pady=(10, 20), sticky="sw")
        self.appearance_mode_option_menu = customtkinter.CTkOptionMenu(self.frame_left,
                                                                       values=["Light", "Dark", "System"],
                                                                       command=lambda mode: change_appearance_mode(self,
                                                                                                                   mode))
        self.appearance_mode_option_menu.grid(row=6, column=0, padx=(20, 20), pady=(10, 20), sticky="se")

        # Set initial values for entries
        self.buffer_distance_entry.insert(0, BUFFER_DISTANCE)
        self.orange_threshold_entry.insert(0, ORANGE_THRESHOLD)
        self.red_threshold_entry.insert(0, RED_THRESHOLD)
        self.merging_threshold_entry.insert(0, MERGING_THRESHOLD)
        self.showing_marker_threshold_entry.insert(0, MIN_SHOWING_MARKER_THRESHOLD)


    def create_right_frame(self):
        self.frame_right.grid_rowconfigure(1, weight=1)
        self.frame_right.grid_rowconfigure(0, weight=0)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(1, weight=0)
        self.frame_right.grid_columnconfigure(2, weight=1)

        self.map_widget = TkinterMapView(self.frame_right, corner_radius=0)
        self.map_widget.grid(row=1, rowspan=1, column=0, columnspan=3, sticky="nswe", padx=(0, 0), pady=(0, 0))


        self.entry = customtkinter.CTkEntry(master=self.frame_right, placeholder_text="type address")
        self.entry.grid(row=0, column=0, sticky="we", padx=(12, 0), pady=12)
        self.entry.bind("<Return>", lambda event: search_event(self, event))

        self.button_5 = customtkinter.CTkButton(master=self.frame_right, text="Search", width=90,
                                                command=lambda: search_event(self))
        self.button_5.grid(row=0, column=1, sticky="w", padx=(12, 0), pady=12)

        # Set default values
        self.map_widget.set_position(47, 2.5, marker=False)
        self.map_widget.set_zoom(6)
        self.map_option_menu.set("Open Street Map")
        self.appearance_mode_option_menu.set("System")



    def show_loading_screen(self):
        self.loading_screen = customtkinter.CTkToplevel(self)
        self.loading_screen.geometry("300x100")
        self.loading_screen.title("Loading")

        label = customtkinter.CTkLabel(self.loading_screen, text="Calculations in progress, please wait...")
        label.pack(pady=20)

        self.progress_var = customtkinter.IntVar()
        self.progress_bar = ttk.Progressbar(self.loading_screen, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(pady=10)

        self.loading_screen.update_idletasks()
        self.loading_screen.geometry(f"{300}x{100}+{self.loading_screen.winfo_screenwidth() // 2}+{self.loading_screen.winfo_screenheight() // 2}")

        self.loading_screen.transient(self)
        self.loading_screen.grab_set()
        self.loading_screen.lift(self)

    def hide_loading_screen(self):
        if self.loading_screen is not None:
            self.loading_screen.destroy()
            self.loading_screen = None

    def start_recalculation(self):
        for checkbox in self.region_checkboxes_gaz:
            self.region_checkboxes_gaz[checkbox].deselect()
        change_region(self)
        self.show_loading_screen()
        thread = Thread(target=self.run_recalculation)
        thread.start()

    def run_recalculation(self):
        recalculate_segments(self)
        self.after(0, self.hide_loading_screen)

    def update_progress(self, value):
        if self.progress_var is not None:
            self.progress_var.set(value)
            self.update_idletasks()

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()
