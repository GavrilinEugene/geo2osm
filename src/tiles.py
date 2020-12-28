from math import pi, log, tan, exp, atan, log2, floor
from typing import Any
import urllib.request
import os


class TileUtils:
    """Class for getting merged map-image  by bounding box"""

    def __init__(self: str, config: dict):
        self.api_token = config["api_token"]
        self.tile_size = config["tile_size"]
        # self.image_resolution = config["image_resolution"]
        self.tmp_dir = config["tmp_dir"]

    @staticmethod
    def latlon2px(zoom: int, lat: float, lon: float, tile_size: int):
        x = tile_size * (2 ** zoom) * (1 + lon / 180) / 2
        y = tile_size / (2 * pi) * (2 ** zoom) * \
            (pi - log(tan(pi / 4 * (1 + lat / 90))))
        return x, y

    @staticmethod
    def latlon2xy(zoom: int, lat: float, lon: float, tile_size: int:
        x, y = TileUtils.latlon2px(zoom, lat, lon, tile_size)
        x = int(x/tile_size)
        y = int(y/tile_size)
        return x, y

    def get_map(self, bbox: list, zoom: int):
        """ ge"""
        (left, bottom, right, top) = bbox
        x_min, y_max = TileUtils.latlon2xy(
            zoom, bottom, left, self.tile_size)
        x_max, y_min = TileUtils.latlon2xy(zoom, top, right, self.tile_size)
        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                print(f"{x},{y}")
                self.__image_loader(x, y, zoom)
        
        __merge_tiles()

    def __image_loader(self, x, y, zoom):
        """ collecting image from mapbox tile server """
        tile_server = f"https://api.mapbox.com/v4/mapbox.satellite/{zoom}/{x}/{y}.png?access_token={self.api_token}"
        path = f'{self.tmp_dir}/{x}_{y}_{zoom}.png'
        urllib.request.urlretrieve(tile_server, path)

    def __merge_tiles(self):
        """
        """
        pass


def test():
    import config

    dict_params = {"api_token": config.get_mapbox_token(),
        "tile_size": 256,
        "tmp_dir": config.get_project_root() + "/data/tmp_data"}

    c = TileUtils(dict_params)
    bbox = [120.2206, 22.4827, 120.4308, 22.7578]
    c.get_tiles(bbox, 15)

test()