from pyproj import CRS, Transformer

# Définir les systèmes de référence CRS3035 et WGS84
crs3035 = CRS('EPSG:3035')
wgs84 = CRS('EPSG:4326')

#crs3035 = CRS.from_string('EPSG:3035')
#wgs84 = CRS.from_string('EPSG:4326')

#crs3035 = CRS.from_epsg(3035)
#wgs84 = CRS.from_epsg(4326)

# Créer un objet transformer
transformer = Transformer.from_crs(crs3035, wgs84)

# Exemple de coordonnées en CRS3035         CRS3035RES200mN2869000E3466600
x_crs3035 = 2869000
y_crs3035 = 3466600

# Conversion des coordonnées
longitude, latitude = transformer.transform(x_crs3035, y_crs3035)

print(f"Latitude: {latitude}, Longitude: {longitude}")

def convert(N, E):
    return transformer.transform(N, E)

