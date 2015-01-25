"""
ArcGIS kernel implementation.
"""
import arcpy
from arcpy import env
from arcpy.sa import *

from utils import *

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


    def create_feature(self, output, polygon):
        """
        Create a polygonal feature using the spatial reference
        of this raster.
        
        Parameters
        ----------
        output : str
        polygon : iterable set of (x, y) tuples.

        Returns
        -------
        Feature
        """
        spatial_reference = arcpy.Describy(self.raster_name)
        points = map(lambda p: arcpy.Point(p[0], p[1]), polygon)
        array = arcpy.Array()
        for point in points:
            array.add(point)
        array.add(points[0]) # close the polygon
        polygon = arcpy.Polygon(array, spatial_reference)
        arcpy.Append_management(polygon, output, "NO_TEST")

    def clip(self, feature, output):
        """
        Clip this raster given a feature.
        """
        feature_items = arcpy.SearchCursor(feature)
        
        count = 0
        for feature_item in feature_items:
            output_path = os.path.join(self.path, "%s_%d.tif" % (output, count)
            arcpy.Clip_management(
                self.raster,
                "#",
                output_path,
                polygon.Shape,
                "#",
                "ClippingGeometry",
                "MAINTAIN_EXTENT")

