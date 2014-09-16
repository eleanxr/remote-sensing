import os
import tarfile
import sys

from osgeo import gdal, gdalnumeric, ogr, osr

import numpy

import logging
logger = logging.getLogger(os.path.basename(__file__))

LANDSAT_BANDS = [
    None,
    {"Name": "Coastal Aerosol", "Range": (0.43e-6, 0.45e-6), "Resolution": 30.0}, #1
    {"Name": "Blue", "Range": (0.45e-6, 0.51e-6), "Resolution": 30.0}, #2
    {"Name": "Green", "Range": (0.53e-6, 0.59e-6), "Resolution": 30.0}, #3
    
    {"Name": "Red", "Range": (0.64e-6, 0.67e-6), "Resolution": 30.0}, #4
    {"Name": "NIR", "Range": (0.85e-6, 0.88e-6), "Resolution": 30.0}, #5
    {"Name": "SWIR 1", "Range": (1.57e-6, 1.65e-6), "Resolution": 30.0}, #6
    
    {"Name": "SWIR 2", "Range": (2.11e-6, 2.29e-6), "Resolution": 30.0}, #7
    {"Name": "Pan Chromatic", "Range": (0.50e-6, 0.68e-6), "Resolution": 15.0}, #8
    {"Name": "Cirrus", "Range": (1.36e-6, 1.38e-6), "Resolution": 30.0}, #9
    
    {"Name": "TIRS 1", "Range": (10.6e-6, 11.19e-6), "Resolution": 30.0 * 100.0}, #10
    {"Name": "TIRS 2", "Range": (11.5e-6, 12.51e-6), "Resolution": 30.0 * 100.0}, #11
]

def extract_landsat_bundle(landsat_download, output_path):
    archive = tarfile.open(landsat_download)
    archive.extractall(output_path)
    
def is_band(bands, tarinfo):
    name = tarinfo.name.lower()
    no_ext = os.path.splitext(name)[0]
    logger.debug("Looking for specified bands in %s", tarinfo.name)
    for band in bands:
        if no_ext.endswith('_b%d' % band):
            logger.debug("Found band %d in file '%s'", band, tarinfo.name)
            return True
    return False
    
def process_landsat_bundle(landsat_download, output_path, bands, raster_transform):
    """
    Applies a transformation to a landsat bundle.
    Returns the identifier for the bundle.
    """
    identifier = os.path.splitext(os.path.splitext(os.path.basename(landsat_download))[0])[0]
    archive = tarfile.open(landsat_download)
    rasters = filter(lambda i: is_band(bands, i), archive.getmembers())
    # Extract them.
    archive.extractall(output_path, rasters)
    # Process them
    for raster in rasters:
        raster_path = os.path.join(output_path, raster.name)
        raster_transform(raster_path)
    return identifier
        
def combine_landsat_bands(path, ident, f, band_ids):
    """
    Perform some function to combine a set of bands in landsat imagery.
    - ident : The identifier for the image bundle
    - f : The function to apply. Takes a single argument, a list of numpy arrays.
    - band_ids : The band ids to map (in the same order as the argument to f)
    """
    band_images = []
    for band_id in band_ids:
        raster_file = os.path.join(path, '%s_B%d.tif' % (ident, band_id))
        logger.debug('Loading band raster %s', raster_file)
        if not os.path.exists(raster_file):
            raise IOError("Failed to locate file %s" % raster_file)
        band_raster = gdalnumeric.LoadFile(raster_file)
        band_images.append(band_raster)
    return f(band_images)
    
def main():
    if len(sys.argv) < 2:
        print "Usage: %s <output-path>" % sys.argv[0]
        sys.exit(-1)
    for archive in sys.argv[2:]:
        print "Extracting %s" % archive
        extract_landsat_bundle(archive, sys.argv[1])
        
if __name__ == '__main__':
    main()
    