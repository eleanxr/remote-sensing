import arcpy
from arcpy import env
from arcpy.sa import *
import random
import os
import csv
import numpy as np

from utils import *

def classify_samples(path, num_samples):
    for i in range(num_samples):
        print "Classifying sample %d" % i
        sample = os.path.join(path, "hi_res_%d.tif" % i)
        signature_file = os.path.join(path, "hi_res_%d.gsg" % i)
        if not os.path.exists(sample):
            raise Exception("Could not find sample %s" % sample)
        if not os.path.exists(signature_file):
            raise Exception("Could not find signature file %s" % signature_file)
        classified = MLClassify(sample, os.path.join(path,signature_file))
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

def measure_coverage(path, num_samples, lo_res_raster_name):
    print "Checking out spatial extension..."
    arcpy.CheckOutExtension("Spatial")
    
    if not os.path.exists(path):
        os.makedirs(path)
        
    env.workspace  = path
    env.overwriteOutput = True
    
    training_sample_path = os.path.join(path, "training")

    # Perform the classification of each training sample with the
    # given signature file.
    classify_samples(training_sample_path, num_samples)
    
    # Create the NDVI-Fractional Cover regression model
    slope, intercept = create_regression_model(training_sample_path, num_samples)
    print "Regression model: m = %f, b = %f" % (slope, intercept)

    # Write the final raster containing fractional coverages
    create_regression_raster(lo_res_raster_name, slope, intercept, "fractional_cover.tif")

if __name__ == "__main__":
    measure_coverage("C:\\Data\\FractionalCoverDemo3", 5, "ndvi_landsat_13SDU05049011.tif")
