# main.py

import customtkinter
import pandas as pd
from tkintermapview import TkinterMapView
from app.callbacks import change_region, change_map, change_appearance_mode, search_event, recalculate_segments

from tkinter import ttk

class App(customtkinter.CTk):
    APP_NAME = "French Gas Network Overview"
    WIDTH = 800
    HEIGHT = 600

    def __init__(self, gaz_network_path, gaz_network_colored_path, gaz_network_colored_merged_path, pop_filtered_path,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title(App.APP_NAME)
        self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
        self.minsize(App.WIDTH, self.HEIGHT)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bind("<Command-q>", self.on_closing)
        self.bind("<Command-w>", self.on_closing)
        self.createcommand('tk::mac::Quit', self.on_closing)

        self.gaz_network = pd.read_csv(gaz_network_path)
        self.colored_gaz_network = pd.read_csv(gaz_network_colored_path)
        self.gaz_df = pd.read_csv(gaz_network_colored_merged_path)
        self.pop_df = pd.read_csv(pop_filtered_path)
        self.pop_df.set_index(['north', 'east'], inplace=True)

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

        region_counts = {region: len(self.region_dfs_gaz[region]) for region in regions}
        self.region_display_names_gaz = {region: f"{region} ({count})" for region, count in region_counts.items()}
        self.display_to_region_gaz = {v: k for k, v in self.region_display_names_gaz.items()}

    def create_left_frame(self):
        self.frame_left.grid_rowconfigure(0, weight=0)
        self.frame_left.grid_rowconfigure(1, weight=0)
        self.frame_left.grid_rowconfigure(2, weight=0)
        self.frame_left.grid_rowconfigure(3, weight=1)  # Adjusted for spacing
        self.frame_left.grid_rowconfigure(4, weight=0)
        self.frame_left.grid_columnconfigure(0, weight=1)
        self.frame_left.grid_columnconfigure(1, weight=1)

        self.region_label_gaz = customtkinter.CTkLabel(self.frame_left, text="Select regions", anchor="center",
                                                       font=("Helvetica", 16, "bold"))
        self.region_label_gaz.grid(row=0, column=0, columnspan=2, padx=(20, 20), pady=(20, 10))

        self.region_frame_gaz = customtkinter.CTkFrame(self.frame_left, fg_color=None)
        self.region_frame_gaz.grid(row=1, column=0, columnspan=2, padx=(20, 20), pady=(10, 20), sticky="n")

        self.region_checkboxes_gaz = {}
        for idx, (region, display_name) in enumerate(self.region_display_names_gaz.items()):
            self.region_checkboxes_gaz[region] = customtkinter.CTkCheckBox(self.region_frame_gaz, text=display_name,
                                                                           command=lambda: change_region(self))
            self.region_checkboxes_gaz[region].grid(row=idx, column=0, padx=(0, 0), pady=(5, 0), sticky="w")

        self.param_frame = customtkinter.CTkFrame(self.frame_left, fg_color=None)
        self.param_frame.grid(row=2, column=0, columnspan=2, padx=(20, 20), pady=(10, 20), sticky="n")

        self.buffer_distance_label = customtkinter.CTkLabel(self.param_frame, text="Buffer Distance:  ", anchor="w")
        self.buffer_distance_label.grid(row=0, column=0, padx=(20, 0), pady=(10, 0), sticky="e")
        self.buffer_distance_entry = customtkinter.CTkEntry(self.param_frame, width=80, border_width=2,
                                                            border_color="green")
        self.buffer_distance_entry.grid(row=0, column=1, padx=(0, 5), pady=(10, 0), sticky="w")
        self.buffer_distance_unit = customtkinter.CTkLabel(self.param_frame, text="meters", anchor="w")
        self.buffer_distance_unit.grid(row=0, column=2, padx=(0, 20), pady=(10, 0), sticky="w")

        self.orange_threshold_label = customtkinter.CTkLabel(self.param_frame, text="Orange Threshold:  ", anchor="w")
        self.orange_threshold_label.grid(row=1, column=0, padx=(20, 0), pady=(10, 0), sticky="e")
        self.orange_threshold_entry = customtkinter.CTkEntry(self.param_frame, width=80, border_width=2,
                                                             border_color="orange")
        self.orange_threshold_entry.grid(row=1, column=1, padx=(0, 5), pady=(10, 0), sticky="w")
        self.orange_threshold_unit = customtkinter.CTkLabel(self.param_frame, text="hab/km²", anchor="w")
        self.orange_threshold_unit.grid(row=1, column=2, padx=(0, 20), pady=(10, 0), sticky="w")

        self.red_threshold_label = customtkinter.CTkLabel(self.param_frame, text="Red Threshold:  ", anchor="w")
        self.red_threshold_label.grid(row=2, column=0, padx=(20, 0), pady=(10, 0), sticky="e")
        self.red_threshold_entry = customtkinter.CTkEntry(self.param_frame, width=80, border_width=2,
                                                          border_color="red")
        self.red_threshold_entry.grid(row=2, column=1, padx=(0, 5), pady=(10, 0), sticky="w")
        self.red_threshold_unit = customtkinter.CTkLabel(self.param_frame, text="hab/km²", anchor="w")
        self.red_threshold_unit.grid(row=2, column=2, padx=(0, 20), pady=(10, 0), sticky="w")

        self.recalculate_button = customtkinter.CTkButton(self.param_frame, text="Recalculate",
                                                          command=lambda: self.start_recalculation())
        self.recalculate_button.grid(row=3, column=0, columnspan=3, padx=(20, 20), pady=(10, 20))

        self.map_label = customtkinter.CTkLabel(self.frame_left, text="Background:", anchor="w")
        self.map_label.grid(row=4, column=0, padx=(20, 0), pady=(20, 10))
        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left, values=["OpenStreetMap",
                                                                                    "Google Map (classic)",
                                                                                    "Google Map (satellite)"],
                                                           command=lambda new_map: change_map(self, new_map))
        self.map_option_menu.grid(row=4, column=1, padx=(0, 20), pady=(20, 10))

        self.appearance_mode_label = customtkinter.CTkLabel(self.frame_left, text="Appearance:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=(20, 0), pady=(10, 10), sticky="s")
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.frame_left,
                                                                       values=["Light", "Dark", "System"],
                                                                       command=lambda mode: change_appearance_mode(self,
                                                                                                                   mode))
        self.appearance_mode_optionemenu.grid(row=5, column=1, padx=(0, 20), pady=(10, 10), sticky="s")

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
        self.map_option_menu.set("OpenStreetMap")
        self.appearance_mode_optionemenu.set("System")

        self.buffer_distance_entry.insert(0, "200")
        self.orange_threshold_entry.insert(0, "250")
        self.red_threshold_entry.insert(0, "2500")

    def show_loading_screen(self):
        self.loading_screen = customtkinter.CTkToplevel(self)
        self.loading_screen.geometry("300x100")
        self.loading_screen.title("Loading")

        label = customtkinter.CTkLabel(self.loading_screen, text="Calculations in progress, please wait...")
        label.pack(pady=20)

        self.progress_var = customtkinter.IntVar()
        self.progress_bar = ttk.Progressbar(self.loading_screen, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(pady=10)

        self.loading_screen.transient(self)
        self.loading_screen.grab_set()
        self.loading_screen.lift(self)

    def hide_loading_screen(self):
        if self.loading_screen is not None:
            self.loading_screen.destroy()
            self.loading_screen = None

    def start_recalculation(self):
        self.show_loading_screen()
        self.after(100, lambda: recalculate_segments(self))

    def update_progress(self, value):
        if self.progress_var is not None:
            self.progress_var.set(value)
            self.update_idletasks()

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()
