import customtkinter


def search_event(app, event=None):
    app.map_widget.set_address(app.entry.get())


def change_region(app):
    app.map_widget.delete_all_path()
    for region, checkbox in app.region_checkboxes_grt.items():
        if checkbox.get():
            for index, row in app.region_dfs_grt[region].iterrows():
                coordinates = row['coordinates']
                app.map_widget.set_path(coordinates, color="blue")
    for region, checkbox in app.region_checkboxes_terega.items():
        if checkbox.get():
            for index, row in app.region_dfs_terega[region].iterrows():
                coordinates = row['coordinates']
                app.map_widget.set_path(coordinates, color="green")


def change_map(app, new_map):
    if new_map == "OpenStreetMap":
        app.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
    elif new_map == "Google Map (classic)":
        app.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
    elif new_map == "Google Map (satellite)":
        app.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)


def change_appearance_mode(app, new_appearance_mode):
    customtkinter.set_appearance_mode(new_appearance_mode)
