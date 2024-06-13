import pandas as pd
import json
import tkinter as tk
import tkintermapview

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

# Function to update the map based on the selected region
def update_map(region):
    map_widget.delete_all_path()
    for index, row in region_dfs[region].iterrows():
        coordinates = row['coordinates']
        map_widget.set_path(coordinates)

# Create the main Tkinter window
root_tk = tk.Tk()
root_tk.geometry(f"{1000}x{700}")
root_tk.title("Map View by Region")

# Initialize the map widget with Open Street Map
map_widget = tkintermapview.TkinterMapView(root_tk, width=1000, height=700)
map_widget.pack(fill="both", expand=True)

# Set the initial map position and zoom level
map_widget.set_position(47, 2.5, marker=False)
map_widget.set_zoom(6)

update_map("Bretagne")

# Start the Tkinter main loop
root_tk.mainloop()
