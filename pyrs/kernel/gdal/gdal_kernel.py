"""
GDAL kernel implementation.
"""
import sys
import os

from osgeo import gdal, ogr

import logging
logger = logging.getLogger(__name__)

class gdal_registry(object):
    def __init__(self, path):
        self.path = path
        
    def open_raster(self, filename):
        """
        Open a raster from a file.
        """
        return gdal_raster(self.path, filename)
        
    def create_composite(self, filename, *rasters):
        """Create a composite raster from a set of rasters.
        filename : The name of the file to save the composite raster to
        returns a raster.
        """
        pass

class gdal_feature(object):
    def __init__(self, path, name, spatial_reference):
        pass
        
    def add_polygon(self, polygon):
        """Add a polygon to this feature.
        """
        pass        

class gdal_raster(object):
    def __init__(self, path, raster_name):
        self.path = path
        self.raster_name = raster_name
        self.dataset = gdal.Open(os.path.join(path, raster_name))
        
    def get_extent(self):
        """
        Get the extent of a raster in its spatial reference.
        Returns a tuple (top, left, right, bottom)
        """
        pass

    def get_pixel_size(self):
        """
        Get the pixel size of the raster in its spatial reference.
        Returns a tuple (pixel_size_x, pixel_size_y)
        """
        pass
        
    def create_feature(self, output):
        """Create a feature using this raster's spatial reference.
        """
        pass
        
    def clip(self, feature, output):
        """
        Clip this raster given a feature.
        """
        pass
