from math import pi, log, tan, exp, atan, log2, floor
from typing import Any
import urllib.request
from PIL import Image
import os


class TileUtils:
    """Class for getting merged map-image  by bounding box"""

    def __init__(self: str, config: dict):
        self.api_token = config["api_token"]
        self.tile_size = config["tile_size"]
        self.tmp_dir = config["tmp_dir"]

    @staticmethod
    def latlon2px(zoom: int, lat: float, lon: float, tile_size: int):
        x = tile_size * (2 ** zoom) * (1 + lon / 180) / 2
        y = tile_size / (2 * pi) * (2 ** zoom) * \
            (pi - log(tan(pi / 4 * (1 + lat / 90))))
        return x, y

    @staticmethod
    def latlon2xy(zoom: int, lat: float, lon: float, tile_size: int):
        x, y = TileUtils.latlon2px(zoom, lat, lon, tile_size)
        x = int(x/tile_size)
        y = int(y/tile_size)
        return x, y

    def get_map(self, bbox: list, zoom: int):
        """ get map """
        (left, bottom, right, top) = bbox
        x_min, y_max = TileUtils.latlon2xy(
            zoom, bottom, left, self.tile_size)
        x_max, y_min = TileUtils.latlon2xy(zoom, top, right, self.tile_size)
        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                self.__image_loader(x, y, zoom)
        
        self.__merge_tiles(x_min, x_max, y_min, y_max, zoom)

    def __image_loader(self, x, y, zoom):
        """ collecting image from mapbox tile server """
        tile_server = f"https://api.mapbox.com/v4/mapbox.satellite/{zoom}/{x}/{y}.png?access_token={self.api_token}"
        path = f'{self.tmp_dir}/{x}_{y}_{zoom}.png'
        urllib.request.urlretrieve(tile_server, path)

    def __merge_tiles(self, x_min: int, x_max: int, y_min: int, y_max: int, zoom):
        """
        """
        wigth = (x_max - x_min + 1) * self.tile_size
        height = (y_max - y_min + 1) * self.tile_size    
        result = Image.new("RGB", (wigth, height))
    
        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                path = f'{self.tmp_dir}/{x}_{y}_{zoom}.png'
                if not os.path.exists(path):
                    print ("-- missing", filename)
                    continue
                        
                x_paste = (x - x_min) * self.tile_size
                y_paste = height - (y_max + 1 - y) * self.tile_size

                img = Image.open(path)
                result.paste(img, (x_paste, y_paste))
                del img

        result.save(f'{self.tmp_dir}/1.jpg')