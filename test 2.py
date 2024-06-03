import pandas as pd
import json
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import tkinter as tk
from tkinter import filedialog, messagebox

# Load the CSV file
csv_file = 'resources/terega.csv'
data = pd.read_csv(csv_file, delimiter=';')

# Process the 'geo_point_2d' column
data['lat'] = data['geo_point_2d'].apply(lambda x: float(str(x).split(',')[0]))
data['lon'] = data['geo_point_2d'].apply(lambda x: float(str(x).split(',')[1]))


# Process the 'geo_shape' column
def extract_coordinates(geo_shape):
    if isinstance(geo_shape, str):
        try:
            coordinates = json.loads(geo_shape)['coordinates']
            if isinstance(coordinates, list) and all(isinstance(coord, list) for coord in coordinates):
                return [(coord[1], coord[0]) for coord in coordinates if len(coord) >= 2]
        except (json.JSONDecodeError, KeyError):
            return None
    return None


data['coordinates'] = data['geo_shape'].apply(extract_coordinates)

# Filter out rows with invalid coordinates
data = data.dropna(subset=['coordinates'])


def plot_gas_network(data):
    fig, ax = plt.subplots(figsize=(10, 8))
    m = Basemap(projection='lcc', resolution='h',
                lat_0=46.5, lon_0=2.5,
                width=1.5E6, height=2.2E6, ax=ax)

    m.shadedrelief()
    m.drawcoastlines()
    m.drawcountries()
    m.drawparallels(range(40, 60, 1), labels=[1, 0, 0, 0])
    m.drawmeridians(range(-5, 10, 2), labels=[0, 0, 0, 1])

    # Plot each set of coordinates
    for coords in data['coordinates']:
        if coords:  # Ensure coords is not None
            lats, lons = zip(*coords)
            if all(isinstance(lat, float) for lat in lats) and all(isinstance(lon, float) for lon in lons):
                x, y = m(lons, lats)
                m.plot(x, y, marker='o', markersize=2, linewidth=1, color='r')

    plt.title('Gas Network in Mainland France')
    plt.show()


# Tkinter GUI
def on_show_map():
    plot_gas_network(data)


# Create the main Tkinter window
root = tk.Tk()
root.title("Gas Network Map")

# Add a button to display the map
btn_show_map = tk.Button(root, text="Show Map", command=on_show_map)
btn_show_map.pack(pady=20)

# Start the Tkinter main loop
root.mainloop()
