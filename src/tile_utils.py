from math import pi, log, tan, exp, atan, log2, floor, sinh
from typing import Any
import urllib.request
from PIL import Image
import os
import mercantile
from osgeo import gdal, osr


def convert_jpg_to_geotiff(image_source_path: str, image_output_path: str, geo_transform: list) -> None:
    """
    Convert jpg to geotiff

    params: 
        image_source_path: absolute path of imput image
        image_output_path: absolute path of output image
        geo_transform: gdal-like list of 6 attributes
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


def clip_geotiff(image_source_path: str, image_output_path: str, bbox: list) -> None:
    """
    Clip geotif by bounding box (left, bottom, right, top])

    params: 
        image_source_path: absolute path of imput image
        image_output_path: absolute path of output image
        bbox: list of left, bottom, right, top coordinates for clipping
    """
    ds = gdal.Open(image_source_path)
    ds = gdal.Translate(image_output_path, ds, projWin=[
                        bbox[0], bbox[3], bbox[2], bbox[1]])
    ds = None


def get_geo_transform(tile_lt, tile_rb, width, height) -> list:
    """
    Calculcate gdal transform list

    params:
        tile_lt: mercantile.Tile fo left-top tile
        tile_rb: mercantile.Tile fo right-bottom tile
        width: image width
        height: image height

    return:
        [lon_lt, lon_pixel_res, 0, lat, 0 lat_pixel_res]
    """
    lt_bounds = mercantile.bounds(tile_lt)
    rb_bounds = mercantile.bounds(tile_rb)
    geotransform = []
    geotransform.append(lt_bounds.west)
    geotransform.append((rb_bounds.east - lt_bounds.west) / width)
    geotransform.append(0)
    geotransform.append(lt_bounds.north)
    geotransform.append(0)
    geotransform.append((rb_bounds.south - lt_bounds.north) / height)
    return geotransform


class TileUtils:
    """ 
    Class for getting merged satellite-image by bounding box
    
    params:
        config with 
            - mapbox api key
            - tile size
            - tmp working dir to store image
    """

    def __init__(self: str, config: dict):
        self.api_token = config["api_token"]
        self.tile_size = config["tile_size"]
        self.tmp_dir = config["tmp_dir"]
        self.tmp_image_name = self.tmp_dir + '/mapbox_raw_image'

    def get_map(self, bbox: list, zoom: int) -> None:
        """
        Get bounded map with defined scale level
        
        params:
            bbox: list of left, bottom, right, top coordinates
            zoom: map scale level

        return:
        """
        tile_lb, tile_lt, tile_rt, tile_rb = self.__get_bbox_tiles(bbox, zoom)

        # load and merge tiles
        self.__load_tiles(tile_lb.x, tile_rt.x, tile_rt.y, tile_lb.y, zoom)
        (wigth, height) = self.__merge_tiles(
            tile_lb.x, tile_rt.x, tile_rt.y, tile_lb.y, zoom)
        # clip image to original bouding box
        geo_transform = get_geo_transform(tile_lt, tile_rb, wigth, height)
        convert_jpg_to_geotiff(self.tmp_image_name + '.jpg',
                               self.tmp_image_name + '.tif', geo_transform)
        clip_geotiff(self.tmp_image_name + '.tif',
                     self.tmp_dir + '/mapbox_final_image.tif', bbox)

        # remove redundant tmp images
        os.remove(self.tmp_image_name + '.jpg')
        os.remove(self.tmp_image_name + '.tif')

    def __get_bbox_tiles(self: str, bbox: list, zoom: int):
        (left, bottom, right, top) = bbox
        # get tiles x_y pos
        tile_lb = mercantile.tile(left, bottom, zoom)
        tile_lt = mercantile.tile(left, top, zoom)
        tile_rt = mercantile.tile(right, top, zoom)
        tile_rb = mercantile.tile(right, bottom, zoom)
        return tile_lb, tile_lt, tile_rt, tile_rb

    def __load_tiles(self: str, x_min: int, x_max: int, y_min: int, y_max: int, zoom: int) -> None:
        """ 
        Collecting tile image from mapbox tile server

        params:
            x_min: x_sell start number (west)
            x_max: x_sell end number (east)
            y_min: y_sell start number (north)
            y_max: y_sell start number (south)
            zoom: map zoom level
        """
        for x in range(x_min, x_max + 1):
            for y in range(y_min, y_max + 1):
                self.__load_tile(x, y, zoom)

    def __load_tile(self, x: int, y: int, zoom: int) -> None:
        """ 
        Collecting tile image from mapbox tile server 
        
        params:
            x: x_sell number (longitude)
            y: y_sell number (latitude)
            zoom: map zoom level
        """
        tile_server = f"https://api.mapbox.com/v4/mapbox.satellite/{zoom}/{x}/{y}.png?access_token={self.api_token}"
        path = f'{self.tmp_dir}/{x}_{y}_{zoom}.png'
        urllib.request.urlretrieve(tile_server, path)

    def __merge_tiles(self, x_min: int, x_max: int, y_min: int, y_max: int, zoom: int) -> (int, int):
        """
        Merging x_y tiles in one big image

        params:
            x_min: x_sell start number (west)
            x_max: x_sell end number (east)
            y_min: y_sell start number (north)
            y_max: y_sell start number (south)
            zoom: map zoom level
        
        return:
            width, height: image resolution params
        """
        width = (x_max - x_min + 1) * self.tile_size
        height = (y_max - y_min + 1) * self.tile_size
        result_image = Image.new("RGB", (width, height))

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
        result_image.save(self.tmp_image_name + '.jpg')
        return (width, height)
