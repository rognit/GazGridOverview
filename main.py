import os
import sys
from app.main import App


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


gaz_network_path = resource_path('resources/gaz_network.csv')
gaz_network_colored_path = resource_path('resources/gaz_network_colored.csv')
pop_filtered_path = resource_path('resources/pop_filtered.csv')

if __name__ == "__main__":
    app = App(gaz_network_path, gaz_network_colored_path, pop_filtered_path)
    app.start()
