import os
import tarfile
import sys
import shutil

import numpy

import logging
logger = logging.getLogger(__name__)

class Band:
    COASTAL_AEROSOL = 1
    BLUE = 2
    GREEN = 3
    RED = 4
    NIR = 5
    SWIR_1 = 6
    SWIR_2 = 7
    PAN_CHROMATIC = 8
    CIRRUS = 9
    TIRS_1 = 10
    TIRS_2 = 11

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
    
def read_bands(registry, data_path, landsat_file, bands):
    """Read a set of bands from a landsat data download
    Returns a set of rasters containing the requested bands.
    """
    identifier = os.path.splitext(os.path.splitext(os.path.basename(landsat_file))[0])[0]
    logger.debug("Reading members from %s", landsat_file)
    archive = tarfile.open(os.path.join(data_path, landsat_file))
    members = archive.getmembers()
    rasters = filter(lambda i: is_band(bands, i), members)
    metadata = filter(lambda i: os.path.splitext(i.name)[1].lower() == '.txt', members)
    # Extract them.
    logger.debug("Extracting bands %s from %s", bands, landsat_file)
    archive.extractall(data_path, rasters + metadata)
    info = LandsatInfo(data_path, identifier)
    result = []
    for band in bands:
        band_file = os.path.join(data_path, info.get_band_file(band))
        if not os.path.exists(band_file):
            raise IOError("Failed to find %s" % info.get_band_file(band))
        logger.debug("Adding %s to the result set.", info.get_band_file(band))
        result.append(registry.open_raster(info.get_band_file(band)))
    return result
    
class LandsatInfo(object):
    def __init__(self, path, ident):
        info = os.path.join(path, '%s_MTL.txt' % ident)
        if not os.path.exists(info):
            raise IOError("Could not locate metadata for %s at %s", ident, path)
        with open(info, 'r') as data:
            lines = data.readlines()
            self.__info = {}
            for line in lines:
                items = line.split('=')
                if len(items) == 2:
                    self.__info[items[0].strip()] = items[1].strip()
                
    def get_date(self):
        return self.__info['DATE_ACQUIRED']
    
    def get_band_file(self, band):
        return self.__info['FILE_NAME_BAND_%d' % band][1:-1]
    

def main():
    if len(sys.argv) < 2:
        print "Usage: %s <output-path>" % sys.argv[0]
        sys.exit(-1)
    for archive in sys.argv[2:]:
        print "Extracting %s" % archive
        extract_landsat_bundle(archive, sys.argv[1])
        
if __name__ == '__main__':
    main()
    