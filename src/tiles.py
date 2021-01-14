from math import pi, log, tan, exp, atan, log2, floor, sinh
from typing import Any
import urllib.request
from PIL import Image
import os
import mercantile
from osgeo import gdal, osr


def convert_jpg_to_geotiff(image_source_path: str, image_output_path: str, geo_transform: list):
    """

    """
    input_ds = gdal.Open(image_source_path)
    sr = osr.SpatialReference()
    sr.ImportFromEPSG(4326)
    driver = gdal.GetDriverByName('GTiff')
    output_ds = driver.CreateCopy(image_output_path, input_ds, strict=0)
    output_ds.SetProjection(sr.ExportToWkt())
    output_ds.SetGeoTransform(geo_transform)
    output_ds = None
    input_ds = None


def clip_geotiff(image_source_path: str, image_output_path: str, bbox: list):
    """ clip geotif by bounding box (left, bottom, right, top]) """
    ds = gdal.Open(image_source_path)
    ds = gdal.Translate(image_output_path, ds, projWin = [bbox[0], bbox[3], bbox[2], bbox[1]])
    ds = None


def get_geo_transform(tile_lt, tile_rb, width, height):
    lt_bounds = mercantile.bounds(tile_lt)
    rb_bound = mercantile.bounds(tile_rb)
    x = lt_bounds.west
    y = lt_bounds.north
    geotransform = []
    geotransform.append(x)
    geotransform.append((rb_bound.east - lt_bounds.west) / width)
    geotransform.append(0)
    geotransform.append(y)
    geotransform.append(0)
    geotransform.append((rb_bound.south - lt_bounds.north) / height)
    return geotransform


class TileUtils:
    """ Class for getting merged satellite-image by bounding box"""

    def __init__(self: str, config: dict):
        self.api_token = config["api_token"]
        self.tile_size = config["tile_size"]
        self.tmp_dir = config["tmp_dir"]

    def get_map(self, bbox: list, zoom: int):
        """ get map """
        (left, bottom, right, top) = bbox
        # get tile x_y pos
        tile_lb = mercantile.tile(left, bottom, zoom)
        tile_lt = mercantile.tile(left, top, zoom)
        # get right top tile x_y pos
        tile_rt = mercantile.tile(right, top, zoom)
        tile_rb = mercantile.tile(right, bottom, zoom)

        x_min, y_min, x_max, y_max = tile_lb.x, tile_rt.y, tile_rt.x, tile_lb.y

        # loading tiles
        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                self.__image_loader(x, y, zoom)

        (wigth, height) = self.__merge_tiles(x_min, x_max, y_min, y_max, zoom)
        # clip image to original bouding box
        geo_transform = get_geo_transform(tile_lt, tile_rb, wigth, height)
        convert_jpg_to_geotiff(self.tmp_dir + '/mapbox_raw_image.jpg',
                               self.tmp_dir + '/mapbox_raw_image.tif', geo_transform)
        clip_geotiff(self.tmp_dir + '/mapbox_raw_image.tif', self.tmp_dir + '/mapbox_final_image.tif', bbox)


    def __image_loader(self, x, y, zoom):
        """ collecting image from mapbox tile server """
        t = "openstreetmap"
        t = "satellite"
        tile_server = f"https://api.mapbox.com/v4/mapbox.{t}/{zoom}/{x}/{y}.png?access_token={self.api_token}"
        path = f'{self.tmp_dir}/{x}_{y}_{zoom}.png'
        urllib.request.urlretrieve(tile_server, path)

    def __merge_tiles(self, x_min: int, x_max: int, y_min: int, y_max: int, zoom):
        """
            merging x_y tiles in one big image
        """
        wigth = (x_max - x_min + 1) * self.tile_size
        height = (y_max - y_min + 1) * self.tile_size
        result_image = Image.new("RGB", (wigth, height))

        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                path = f'{self.tmp_dir}/{x}_{y}_{zoom}.png'
                if not os.path.exists(path):
                    print("-- missing", filename)
                    continue

                x_paste = (x - x_min) * self.tile_size
                y_paste = height - (y_max + 1 - y) * self.tile_size

                img = Image.open(path)
                result_image.paste(img, (x_paste, y_paste))
                
                del img
                os.remove(path)
        result_image.save(self.tmp_dir + '/mapbox_raw_image.jpg')
        return (wigth, height)
