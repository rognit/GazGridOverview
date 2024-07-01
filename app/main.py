import customtkinter
from tkintermapview import TkinterMapView
from data.load_data import load_gaz_data, extract_coordinates
from app.callbacks import change_region, change_map, change_appearance_mode, search_event


class App(customtkinter.CTk):
    APP_NAME = "French Gas Network Overview"
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

        self.df_gaz = load_gaz_data()

        self.region_dfs_gaz, self.region_display_names_gaz, self.display_to_region_gaz = extract_coordinates(
            self.df_gaz)

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

    def create_left_frame(self):
        self.frame_left.grid_rowconfigure(0, weight=0)
        self.frame_left.grid_rowconfigure(1, weight=0)
        self.frame_left.grid_rowconfigure(2, weight=0)
        self.frame_left.grid_rowconfigure(3, weight=0)
        self.frame_left.grid_rowconfigure(4, weight=1)
        self.frame_left.grid_rowconfigure(5, weight=0)
        self.frame_left.grid_rowconfigure(6, weight=0)
        self.frame_left.grid_columnconfigure(0, weight=1)
        self.frame_left.grid_columnconfigure(1, weight=1)

        self.region_label_gaz = customtkinter.CTkLabel(self.frame_left, text="Gaz Network:", anchor="w")
        self.region_label_gaz.grid(row=0, column=0, padx=(20, 20), pady=(20, 0))

        self.region_frame_gaz = customtkinter.CTkFrame(self.frame_left, fg_color=None)
        self.region_frame_gaz.grid(row=1, column=0, columnspan=2, padx=(20, 20), pady=(10, 0), sticky="n")

        self.region_checkboxes_gaz = {}
        for idx, (region, display_name) in enumerate(self.region_display_names_gaz.items()):
            self.region_checkboxes_gaz[region] = customtkinter.CTkCheckBox(self.region_frame_gaz, text=display_name,
                                                                           command=lambda: change_region(self))
            self.region_checkboxes_gaz[region].grid(row=idx, column=0, padx=(0, 0), pady=(5, 0), sticky="w")

        self.map_label = customtkinter.CTkLabel(self.frame_left, text="Background:", anchor="w")
        self.map_label.grid(row=5, column=0, padx=(20, 0), pady=(20, 0))
        self.map_option_menu = customtkinter.CTkOptionMenu(self.frame_left, values=["OpenStreetMap",
                                                                                    "Google Map (classic)",
                                                                                    "Google Map (satellite)"],
                                                           command=lambda new_map: change_map(self, new_map))
        self.map_option_menu.grid(row=5, column=1, padx=(0, 20), pady=(20, 0))

        self.appearance_mode_label = customtkinter.CTkLabel(self.frame_left, text="Appearance:", anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=(20, 0), pady=(20, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.frame_left,
                                                                       values=["Light", "Dark", "System"],
                                                                       command=lambda mode: change_appearance_mode(self,
                                                                                                                   mode))
        self.appearance_mode_optionemenu.grid(row=6, column=1, padx=(0, 20), pady=(20, 0))

    def create_right_frame(self):
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
        self.entry.bind("<Return>", lambda event: search_event(self, event))

        self.button_5 = customtkinter.CTkButton(master=self.frame_right,
                                                text="Search",
                                                width=90,
                                                command=lambda: search_event(self))
        self.button_5.grid(row=0, column=1, sticky="w", padx=(12, 0), pady=12)

        # Set default values
        self.map_widget.set_position(47, 2.5, marker=False)
        self.map_widget.set_zoom(6)
        self.map_option_menu.set("OpenStreetMap")
        self.appearance_mode_optionemenu.set("System")

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()
