import tkinter
import tkintermapview

root_tk = tkinter.Tk()
root_tk.geometry(f"{1000}x{700}")
root_tk.title("map_view_simple_example.py")

# Open Street Map
map_widget = tkintermapview.TkinterMapView(root_tk, width=1000, height=700)
map_widget.pack(fill="both", expand=True)

# Google Map
map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")  # OpenStreetMap (default)
#map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)  # google normal
#map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)  # google satellite


map_widget.set_position(48.270102, 4.064850, marker=False)
map_widget.set_zoom(17)


# set current position with address
# map_widget.set_address("Troyes, France", marker=False)

def marker_click(marker):
    print(f"marker clicked - text: {marker.text}  position: {marker.position}")


marker_1 = map_widget.set_marker(48.269115, 4.066943, text="Un peu de travail", command=marker_click)
marker_2 = map_widget.set_marker(48.271725, 4.065020, text="Un peu d'escalade")
marker_3 = map_widget.set_marker(48.271696, 4.063122, text="Encore plus d'escalade !")

path_1 = map_widget.set_path([marker_1.position, [48.270380, 4.064498], marker_2.position, marker_3.position])

root_tk.mainloop()
