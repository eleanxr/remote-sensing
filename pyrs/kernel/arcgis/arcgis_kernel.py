"""
ArcGIS kernel implementation.
"""
import arcpy
from arcpy import env
from arcpy.sa import *

import sys

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
        
    def create_composite(self, filename, *rasters):
        """Create a composite raster from a set of rasters.
        filename : The name of the file to save the composite raster to
        returns a raster.
        """
        raster_arg = ";".join([raster.raster_name for raster in rasters])
        logger.debug("Creating composite %s from bands %s", filename, raster_arg)
        try:
            arcpy.CompositeBands_management(raster_arg, filename)
            return arcgis_raster(self.path, filename)
        except:
            logger.error("failed to create composite %s: %s", filename, arcpy.GetMessages())
            
    def get_publishing_service(self, uri):
        return arcgis_publishing_service(self.path, uri)
    
    
    

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

class arcgis_publishing_service(object):
    def __init__(self, data_path, uri):
        self.data_path = data_path
        self.uri = uri
        
    def publish_image(self, raster, info, remote_path = None, description = None, tags = None):
        data = os.path.join(self.data_path, raster.raster_name)
        name = info.get_scene_id()
        sddraft = os.path.join(self.data_path, name + ".sddraft")
        sd = os.path.join(self.data_path, name + ".sd")
        
        tags_string = None
        if tags:
            tags_string = ",".join(tags)
        
        try:
            arcpy.CreateImageSDDraft(data, sddraft, name, 'ARCGIS_SERVER', None, True, remote_path, description, tags_string)
        except Exception as error:
            logger.error(arcpy.GetMessages())
            logger.error("Failed to create image service definition: %s", error[0])
            raise error
            
        analysis = arcpy.mapping.AnalyzeForSD(sddraft)
        for key in analysis.keys():
            print("==={}===".format(key.upper()))
            for ((message, code), layerlist) in analysis[key].iteritems():
                print("    {} (CODE {})".format(message, code))
                print("       applies to: {}".format(
                    " ".join([layer.name for layer in layerlist])))
        
        if not analysis["errors"]:
            try:
                logger.info("Staging service definition %s to %s", sddraft, sd)
                arcpy.StageService_server(sddraft, sd)
                logger.info("Uploading image service %s to %s", sd, self.uri)
                arcpy.UploadServiceDefinition_server(sd, self.uri)
            except arcpy.ExecuteError:
                logger.error(arcpy.GetMessages())
            except Exception as error:
                logger.error("Failed to publish image service: %s", error)
                
        
            
