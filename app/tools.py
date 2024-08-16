from pyproj import Geod

geod = Geod(ellps='WGS84')

def calculate_length(coords):
    (lat1, lon1), (lat2, lon2) = coords
    return geod.inv(lon1, lat1, lon2, lat2)[2]  # 0: Forward Azimuth, 1: Back Azimuth, 2: Distance