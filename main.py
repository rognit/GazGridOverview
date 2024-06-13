import pandas as pd
import json
import tkinter
import tkintermapview


csv_file = 'resources/grt.csv'
df = pd.read_csv(csv_file, delimiter=';')


def extract_coordinates(geo_shape):
    geo_shape_dict = json.loads(geo_shape)
    coordinates = geo_shape_dict['coordinates']
    swapped_coordinates = [(lat, lon) for lon, lat in coordinates]
    return swapped_coordinates

df['coordinates'] = df['geo_shape'].apply(extract_coordinates)

coordinates_df = df[['coordinates']]


root_tk = tkinter.Tk()
root_tk.geometry(f"{1000}x{700}")
root_tk.title("map_view_simple_example.py")

# Open Street Map
map_widget = tkintermapview.TkinterMapView(root_tk, width=1000, height=700)
map_widget.pack(fill="both", expand=True)

map_widget.set_position(47, 2.5, marker=False)
map_widget.set_zoom(6)


for index, row in df.iterrows():
    coordinates = row['coordinates']
    path = map_widget.set_path(coordinates)


root_tk.mainloop()
