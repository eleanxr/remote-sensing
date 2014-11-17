import arcpy
from arcpy import env
from arcpy.sa import *
import random
import os

def get_float_property(raster, name):
    return float(arcpy.GetRasterProperties_management(raster, name).getOutput(0))

def sample_raster(raster_name, num_samples, pixel_width):
    """
    Returns a list of sampling boxes from a raster, each of a given pixel
    width. The result is a list of tuples of the form
    (top, left, right, bottom).
    """
    raster = Raster(raster_name)
    extents = {}
    prop_names = ("TOP", "LEFT", "RIGHT", "BOTTOM")
    for prop_name in prop_names:
        extents[prop_name] = get_float_property(raster, prop_name)
        print "Low Res Extent %s: %f" % (prop_name, extents[prop_name])

    # Get the size of each pixel.
    pixel_size = (
        get_float_property(raster, "CELLSIZEX"),
        get_float_property(raster, "CELLSIZEY"))
    window_size = map(lambda x: x * pixel_width, pixel_size)

    print "Generating %d samples with size %s)" % (num_samples, window_size)
    samples = []
    for i in range(num_samples):
        x = random.uniform(extents["LEFT"], extents["RIGHT"])
        y = random.uniform(extents["BOTTOM"], extents["TOP"])
        samples.append((y, x, x + window_size[0], y - window_size[1]))
    return samples
    
    

def run_sampling(path, lo_res_raster_name, hi_res_raster_name, num_samples):
    if not os.path.exists(path):
        os.makedirs(path)
        
    env.workspace  = path
    env.overwriteOutput = True
    
    points = sample_raster(lo_res_raster_name, num_samples, 3)


if __name__ == '__main__':
    run_sampling("C:\\Data\\HackdayFractionalCover", "landsat_ndvi.tif", "13SDU050490_201203_0x2000m_CL_1.jp2", 5)

