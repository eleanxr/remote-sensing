import random
import os
import csv
import numpy as np

import logging
logger = logging.getLogger(__name__)

def sample_raster(lo_res_raster, hi_res_raster, num_samples, pixel_width):
    """
    Returns a list of sampling boxes from a raster, each of a given pixel
    width. The result is a list of tuples of the form
    (top, left, right, bottom).
    """
    # TODO: Replace with minimum bounding box.
    hi_res_extent = hi_res_raster.get_extent()
    logger.debug("Sample extent bounds: %s", hi_res_extent)

    # Get the size of each pixel.
    pixel_size = lo_res_raster.get_pixel_size()
    window_size = map(lambda x: x * pixel_width, pixel_size)

    logger.info("Generating %d samples with size %s)" % (num_samples, window_size))
    samples = []
    for i in range(num_samples):
        x = random.uniform(hi_res_extent[1], hi_res_extent[2] - window_size[0])
        y = random.uniform(hi_res_extent[3] + window_size[1], hi_res_extent[0])
        samples.append((y, x, x + window_size[0], y - window_size[1]))
    return samples

def create_sample_features(samples, raster, output):
    """
    Create a shapefile with a set of box samples, each element of samples
    is a tuple of the form (top, left, right, bottom)
    """
    feature = raster.create_feature(output)
    for s in samples:
        logger.debug("Adding polygon: %s", s)
        polygon = [
            (s[1], s[3]),
            (s[2], s[3]),
            (s[2], s[0]),
            (s[1], s[0]),
        ]
        feature.add_polygon(polygon)
    return feature

def create_sample_rasters(lo_res_raster, hi_res_raster, sample_feature):
    lo_res_raster.clip(sample_feature, "lo_res")
    hi_res_raster.clip(sample_feature, "hi_res")

def run_sampling(registry, lo_res_raster_name, hi_res_raster_name, num_samples):
    lo_res_raster = registry.open_raster(lo_res_raster_name)
    hi_res_raster = registry.open_raster(hi_res_raster_name)

    # Generate the training samples
    samples = sample_raster(lo_res_raster, hi_res_raster, num_samples, 3)
    # Write a shapefile with the training samples in it.
    sample_feature = create_sample_features(samples, hi_res_raster, "training.shp")

    logger.info("Generating sample rasters")
    create_sample_rasters(
        lo_res_raster,
        hi_res_raster,
        sample_feature)


