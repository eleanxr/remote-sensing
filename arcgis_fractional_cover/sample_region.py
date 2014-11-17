import arcpy
from arcpy import env
from arcpy.sa import *
import random
import os

def get_float_property(raster, name):
    return float(arcpy.GetRasterProperties_management(raster, name).getOutput(0))

def sample_raster(lo_res_raster_name, hi_res_raster_name, num_samples, pixel_width):
    """
    Returns a list of sampling boxes from a raster, each of a given pixel
    width. The result is a list of tuples of the form
    (top, left, right, bottom).
    """
    hi_res_raster = Raster(hi_res_raster_name)
    lo_res_raster = Raster(lo_res_raster_name)

    # TODO: Replace with minimum bounding box.
    hi_res_extent = hi_res_raster.extent
    extents = {
        "TOP": float(hi_res_extent.YMax),
        "LEFT": float(hi_res_extent.XMin),
        "RIGHT": float(hi_res_extent.XMax),
        "BOTTOM": float(hi_res_extent.YMin)
    }

    for name, value in extents.iteritems():
        print "Extent %s: %f" % (name, value)

    # Get the size of each pixel.
    pixel_size = (
        get_float_property(lo_res_raster, "CELLSIZEX"),
        get_float_property(lo_res_raster, "CELLSIZEY"))
    window_size = map(lambda x: x * pixel_width, pixel_size)

    print "Generating %d samples with size %s)" % (num_samples, window_size)
    samples = []
    for i in range(num_samples):
        x = random.uniform(extents["LEFT"], extents["RIGHT"])
        y = random.uniform(extents["BOTTOM"], extents["TOP"])
        samples.append((y, x, x + window_size[0], y - window_size[1]))
    return samples

def create_sample_features(samples, raster_name, path, output):
    """
    Create a shapefile with a set of box samples, each element of samples
    is a tuple of the form (top, left, right, bottom)
    """
    spatial_reference = arcpy.Describe(raster_name).spatialReference

    print "Writing samples feature to %s with spatial reference %s" \
          % (output, spatial_reference)

    arcpy.CreateFeatureclass_management(path, output, "POLYGON", spatial_reference=spatial_reference)
    
    for sample in samples:
        # Samples are of the form (top, left, right, bottom)
        lower_left = arcpy.Point(sample[1], sample[3])
        lower_right = arcpy.Point(sample[2], sample[3])
        upper_right = arcpy.Point(sample[2], sample[0])
        upper_left = arcpy.Point(sample[1], sample[0])

        array = arcpy.Array()
        for point in (lower_left, lower_right, upper_right, upper_left):
            array.add(point)
        # Close the polygon.
        array.add(lower_left)
        polygon = arcpy.Polygon(array, spatial_reference)
        arcpy.Append_management(polygon, output, "NO_TEST")

def create_sample_rasters(path, lo_res_raster_name, hi_res_raster_name, sample_feature):
    lo_res_raster = Raster(lo_res_raster_name)
    hi_res_raster = Raster(hi_res_raster_name)

    polygons = arcpy.SearchCursor(sample_feature)

    count = 0
    for polygon in polygons:
        # Clip the low resolution raster and save the result.
        print "Creating training sample %d..." % count
        arcpy.Clip_management(
            lo_res_raster,
            "#",
            os.path.join(path, "lo_res_%d.tif" % count),
            polygon.Shape,
            "#",
            "ClippingGeometry",
            "MAINTAIN_EXTENT")
        arcpy.Clip_management(
            hi_res_raster,
            "#",
            os.path.join(path, "hi_res_%d.tif" % count),
            polygon.Shape,
            "#",
            "ClippingGeometry",
            "MAINTAIN_EXTENT")
        count = count + 1

def run_sampling(path, lo_res_raster_name, hi_res_raster_name, num_samples):
    if not os.path.exists(path):
        os.makedirs(path)
        
    env.workspace  = path
    env.overwriteOutput = True

    if not os.path.exists(os.path.join(path, "training.shp")):
        print "No training samples found, generating training samples."
        # Generate the training samples
        samples = sample_raster(lo_res_raster_name, hi_res_raster_name, num_samples, 3)
        # Write a shapefile with the training samples in it.
        create_sample_features(samples, hi_res_raster_name, path, "training.shp")
    else:
        print "Training samples already generated (--resample to override)."

    print "Generating sample rasters..."
    training_sample_path = os.path.join(path, "training")
    if not os.path.exists(training_sample_path):
        os.makedirs(training_sample_path)
    create_sample_rasters(
        training_sample_path,
        lo_res_raster_name,
        hi_res_raster_name,
        "training.shp")


if __name__ == '__main__':
    run_sampling("C:\\Data\\HackdayFractionalCover", "landsat_ndvi.tif", "13SDU050490_201203_0x2000m_CL_1.jp2", 5)

