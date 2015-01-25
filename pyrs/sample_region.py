import random
import os
import csv
import numpy as np

def sample_raster(lo_res_raster, hi_res_raster, num_samples, pixel_width):
    """
    Returns a list of sampling boxes from a raster, each of a given pixel
    width. The result is a list of tuples of the form
    (top, left, right, bottom).
    """
    # TODO: Replace with minimum bounding box.
    hi_res_extent = hi_res_raster.get_extent()

    for name, value in extents.iteritems():
        print "Extent %s: %f" % (name, value)

    # Get the size of each pixel.
    pixel_size = lo_res_raster.get_pixel_size()
    window_size = map(lambda x: x * pixel_width, pixel_size)

    print "Generating %d samples with size %s)" % (num_samples, window_size)
    samples = []
    for i in range(num_samples):
        x = random.uniform(extents["LEFT"], extents["RIGHT"] - window_size[0])
        y = random.uniform(extents["BOTTOM"] + window_size[1], extents["TOP"])
        samples.append((y, x, x + window_size[0], y - window_size[1]))
    return samples

def create_sample_features(samples, raster, output):
    """
    Create a shapefile with a set of box samples, each element of samples
    is a tuple of the form (top, left, right, bottom)
    """
    for sample in samples:
        raster.create_feature(output, sample)

def create_sample_rasters(lo_res_raster, hi_res_raster, sample_feature):
    lo_res_raster.clip(sample_feature, "lo_res")
    hi_res_raster.clip(sample_feature, "hi_res")

def run_sampling(registry, lo_res_raster_name, hi_res_raster_name, num_samples):
    lo_res_raster = registry.open_raster(lo_res_raster_name)
    hi_res_raster = registry.open_raster(hi_res_raster_name)

    if not os.path.exists(os.path.join(path, "training.shp")):
        print "No training samples found, generating training samples."
        # Generate the training samples
        samples = sample_raster(lo_res_raster, hi_res_raster, num_samples, 3)
        # Write a shapefile with the training samples in it.
        create_sample_features(samples, hi_res_raster, "training.shp")
    else:
        print "Training samples already generated (--resample to override)."

    print "Generating sample rasters..."
    training_sample_path = os.path.join(path, "training")
    if not os.path.exists(training_sample_path):
        os.makedirs(training_sample_path)
    create_sample_rasters(
        lo_res_raster,
        hi_res_raster,
        "training.shp")


