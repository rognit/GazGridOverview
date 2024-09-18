import os
import sys
from app.app import App
from config import *


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    # Special handling for icon file
    if relative_path.endswith('icon.ico'):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        else:
            return relative_path

    return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    app = App(
        resource_path(BASE_GAZ_NETWORK_PATH),
        resource_path(BASE_POPULATION_PATH),
        resource_path(SIMPLIFIED_COMPUTED_GAZ_NETWORK_PATH),
        resource_path(EXHAUSTIVE_COMPUTED_GAZ_NETWORK_PATH),
        resource_path(INFORMATION_PATH),
        resource_path(GREEN_MARKERS_PATH),
        resource_path(ORANGE_MARKERS_PATH),
        resource_path(ICON_PATH)
    )
    app.start()
