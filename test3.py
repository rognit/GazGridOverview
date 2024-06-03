import tkinter
import tkintermapview


# create tkinter window
root_tk = tkinter.Tk()
root_tk.geometry(f"{800}x{600}")
root_tk.title("map_view_example.py")

# create map widget
map_widget = tkintermapview.TkinterMapView(root_tk, width=800, height=600, corner_radius=0)
map_widget.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)


# set current widget position and zoom
map_widget.set_position(48.860381, 2.338594)  # Paris, France
map_widget.set_zoom(15)


# set current widget position by address
map_widget.set_address("colosseo, rome, italy")


# set current widget position by address
marker_1 = map_widget.set_address("colosseo, rome, italy", marker=True)

print(marker_1.position, marker_1.text)  # get position and text

marker_1.set_text("Colosseo in Rome")  # set new text
# marker_1.set_position(48.860381, 2.338594)  # change position
# marker_1.delete()


map_widget.fit_bounding_box((48.860381, 2.338594), (41.890251, 12.492373))
# Paris, France and Rome, Italy


# set a position marker
marker_2 = map_widget.set_marker(52.516268, 13.377695, text="Brandenburger Tor")
marker_3 = map_widget.set_marker(52.55, 13.4, text="52.55, 13.4")

# methods
marker_3.set_position(...)
marker_3.set_text(...)
marker_3.change_icon(new_icon)
marker_3.hide_image(True)  # or False
marker_3.delete()
