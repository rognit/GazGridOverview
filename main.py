import os
import sys
from app.main import App
from config import *


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    app = App(
        resource_path(GAZ_NETWORK_PATH),
        resource_path(GAZ_NETWORK_COLORED_PATH),
        resource_path(GAZ_NETWORK_COLORED_MERGED_PATH),
        resource_path(POPULATION_PATH)
    )
    app.start()
