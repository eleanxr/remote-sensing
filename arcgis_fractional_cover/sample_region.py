import arcpy
from arcpy import env
from arcpy.sa import *
import random
import os
import csv
import numpy as np

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
        lo_res_path = os.path.join(path, "lo_res_%d.tif" % count)
        hi_res_path = os.path.join(path, "hi_res_%d.tif" % count)
        if os.path.exists(lo_res_path) and os.path.exists(hi_res_path):
            print "Skipping sample %d because files exist" % count
        else:
            # Clip the low resolution raster and save the result.
            print "Creating training sample %d..." % count
            arcpy.Clip_management(
                lo_res_raster,
                "#",
                lo_res_path,
                polygon.Shape,
                "#",
                "ClippingGeometry",
                "MAINTAIN_EXTENT")
            arcpy.Clip_management(
                hi_res_raster,
                "#",
                hi_res_path,
                polygon.Shape,
                "#",
                "ClippingGeometry",
                "MAINTAIN_EXTENT")
        count = count + 1

def classify_samples(path, signature_file, num_samples):
    for i in range(num_samples):
        print "Classifying sample %d" % i
        sample = os.path.join(path, "hi_res_%d.tif" % i)
        if not os.path.exists(sample):
            raise Exception("Could not find sample %s" % sample)
        classified = MLClassify(sample, signature_file)
        classified.save(os.path.join(path, "hi_res_%d_cover.tif" % i))

class ClassificationConstants:
    GV1 = 1
    GV2 = 2
    LIGHT_SOIL = 3
    DARK_SOIL = 4

def linear_regression(xs, ys):
    """
    Compute the linear regression for the ys as predicted by xs.
    TODO: Install SciPy and use that!
    Returns m, b where m is the slope and b is the intercept.
    """
    # Linear regression is the least squares minimization of
    # the overdetermined system (x, 1)w = y.
    A = np.array([xs, np.ones(len(xs))])
    w = np.linalg.lstsq(A.T, np.array(ys))[0]
    return w[0], w[1]

def create_regression_model(path, num_samples):
    xs = []
    ys = []
    for i in range(num_samples):
        lo_res_path = os.path.join(path, "lo_res_%d.tif" % i)
        cover_path = os.path.join(path, "hi_res_%d_cover.tif" % i)
        if not os.path.exists(lo_res_path) or not os.path.exists(cover_path):
            raise Exception("Could not locate data for regression model!")
        predictor = Raster(lo_res_path)
        predicted = Raster(cover_path)
        average_predictor = get_float_property(predictor, "MEAN")
        cover_array = arcpy.RasterToNumPyArray(predicted)
        counts = np.bincount(np.ravel(cover_array))
        vegetation_pixels = counts[ClassificationConstants.GV1]
        frac = float(vegetation_pixels)/cover_array.size
        print "Sample %d: ndvi = %f, f_c = %f" % (i, average_predictor, frac)
        xs.append(average_predictor)
        ys.append(frac)
    slope, intercept = linear_regression(xs, ys)
    with open(os.path.join(path, "model.csv"), "w") as datafile:
        writer = csv.writer(datafile)
        writer.writerow(["ndvi", "f_c"])
        for row in zip(xs, ys):
            writer.writerow(row)
    return slope, intercept

def create_regression_raster(raster_name, slope, intercept, output):
    print "Writing regression raster..."
    raster = Raster(raster_name)
    regression_raster = slope * raster + intercept
    regression_raster.save(output)

def run_sampling(path, lo_res_raster_name, hi_res_raster_name, num_samples, run_regression=False, signature_file=None):
    print "Checking out spatial extension..."
    arcpy.CheckOutExtension("Spatial")
    
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

    if signature_file:
        # Perform the classification of each training sample with the
        # given signature file.
        classify_samples(training_sample_path, signature_file, num_samples)

    if run_regression:
        # Create the NDVI-Fractional Cover regression model
        slope, intercept = create_regression_model(training_sample_path, num_samples)
        print "Regression model: m = %f, b = %f" % (slope, intercept)

        # Write the final raster containing fractional coverages
        create_regression_raster(lo_res_raster_name, slope, intercept, "fractional_cover.tif")
    else:
        print "Skipping regression to generate training samples."
        
if __name__ == '__main__':
    run_sampling(
        "C:\\Data\\HackdayFractionalCover2",
        "landsat_ndvi.tif",
        "13SDU050490_201203_0x2000m_CL_1.jp2",
        10,
        True,
        "C:\\Data\\HackdayFractionalCover\\training\\hi_res_3.gsg")

