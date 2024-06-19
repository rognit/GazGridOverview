import re
import pandas as pd
import tkinter
import tkintermapview


# Convert Inspire identifiants to latitude and longitude
def inspire_to_lat_lon(inspire_id):
    match = re.search(r'N(\d+)E(\d+)', inspire_id)
    if match:
        north = int(match.group(1))
        east = int(match.group(2))
        # Conversion based on a fixed point (e.g., a specific location in the CRS3035 coordinate system)
        # Here, just returning some dummy values for the sake of example
        return north / 100000.0, east / 100000.0
    else:
        raise ValueError(f"Invalid Inspire ID format: {inspire_id}")


# Load the first 100,000 rows of the CSV file using pandas
df = pd.read_csv('resources/population2019.csv', nrows=100000)

# Create tkinter window
root_tk = tkinter.Tk()
root_tk.geometry(f"{1000}x{700}")
root_tk.title("Map View - Population 2019")

# Create map widget
map_widget = tkintermapview.TkinterMapView(root_tk, width=1000, height=700, corner_radius=0)
map_widget.pack(fill="both", expand=True)

# Set a default view (you can adjust this as needed)
map_widget.set_position(46.603354, 1.888334)  # Center of France
map_widget.set_zoom(6)


# Function to handle polygon clicks
def polygon_click(polygon):
    print(f"Polygon clicked - text: {polygon.name}")


# Plot each carreau on the map
for index, row in df.iterrows():
    idcar_200m = row["idcar_200m"]
    ind = row["ind"]

    try:
        # Convert the Inspire ID to coordinates
        lat, lon = inspire_to_lat_lon(idcar_200m)
    except ValueError as e:
        print(e)
        continue

    # Create a square polygon around the point (dummy size, adjust as needed)
    size = 0.01  # Size of the square sides, in degrees
    polygon_coords = [
        (lat - size / 2, lon - size / 2),
        (lat + size / 2, lon - size / 2),
        (lat + size / 2, lon + size / 2),
        (lat - size / 2, lon + size / 2),
    ]

    # Create polygon on the map
    polygon = map_widget.set_polygon(polygon_coords,
                                     fill_color="blue" if ind > 5 else "green",
                                     outline_color="black",
                                     border_width=2,
                                     command=polygon_click,
                                     name=f"Carreau {idcar_200m} - Ind: {ind}")

root_tk.mainloop()
