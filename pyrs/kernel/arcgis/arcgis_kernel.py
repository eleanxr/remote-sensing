"""
ArcGIS kernel implementation.
"""
import arcpy
from arcpy import env
from arcpy.sa import *

from utils import *

import logging
logger = logging.getLogger(__name__)

class arcgis_registry(object):
    def __init__(self, path):
        self.path = path
        arcpy.CheckOutExtension("Spatial")
        
        if not os.path.exists(path):
            os.makedirs(path)
            
        env.workspace  = path
        env.overwriteOutput = True

    def open_raster(self, filename):
        """
        Open a raster from a file.
        """
        return arcgis_raster(self.path, filename)

class arcgis_feature(object):
    def __init__(self, path, name, spatial_reference):
        self.path = path
        self.name = name
        self.spatial_reference = spatial_reference
        
    def add_polygon(self, polygon):
        """Add a polygon to this feature.
        """
        points = [arcpy.Point(p[0], p[1]) for p in polygon]
        array = arcpy.Array()
        for point in points:
            array.add(point)
        array.add(points[0]) # close the polygon
        polygon = arcpy.Polygon(array, self.spatial_reference)
        arcpy.Append_management(polygon, self.name, "NO_TEST")
        

class arcgis_raster(object):
    def __init__(self, path, raster_name):
        self.path = path
        self.raster_name = raster_name
        self.raster = Raster(raster_name)

    def get_extent(self):
        """
        Get the extent of a raster in its spatial reference.
        Returns a tuple (top, left, right, bottom)
        """
        extent = self.raster.extent
        return(extent.YMax, extent.XMin, extent.XMax, extent.YMin)

    def get_pixel_size(self):
        """
        Get the pixel size of the raster in its spatial reference.
        Returns a tuple (pixel_size_x, pixel_size_y)
        """
        return (
            get_float_property(self.raster, "CELLSIZEX"),
            get_float_property(self.raster, "CELLSIZEY"))

    def create_feature(self, output):
        """Create a feature using this raster's spatial reference.
        """
        spatial_reference = arcpy.Describe(self.raster_name).spatialReference
        logger.debug("CreateFeatureclass_management arguments: %s %s %s %s", self.path, output, "POLYGON", spatial_reference)
        arcpy.CreateFeatureclass_management(self.path, output, "POLYGON", spatial_reference=spatial_reference)
        return arcgis_feature(self.path, output, spatial_reference)
    
    def clip(self, feature, output):
        """
        Clip this raster given a feature.
        """
        this_path = os.path.join(self.path, self.raster_name)
        feature_path = os.path.join(feature.path, feature.name)
        logger.debug("Clipping %s by %s", this_path, feature_path)
        feature_items = arcpy.SearchCursor(feature_path)
        
        count = 0
        for feature_item in feature_items:
            output_path = os.path.join(self.path, "%s_%d.tif" % (output, count))
            logger.debug("Clip raster %s to %s", self.raster_name, output_path)
            arcpy.Clip_management(
                self.raster,
                "#",
                output_path,
                feature_item.Shape,
                "#",
                "ClippingGeometry",
                "MAINTAIN_EXTENT")
            count = count + 1

