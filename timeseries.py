import landsat
import operations
import rasterclip
import tempfile
import shutil
import os
import sys

import logging
logger = logging.getLogger(__name__)

def process_raster(shapefile, output_path, raster_path):
    logger.debug('process_raster %s %s %s', shapefile, output_path, raster_path)
    rastername = os.path.basename(raster_path)
    rasterfile = os.path.splitext(rastername)[0]
    output_file = rasterfile + '_processed'
    output_path = os.path.join(output_path, output_file)
    rasterclip.clip_raster(raster_path, shapefile, output_path)

def clip_imagery(landsat_bundles, shapefile, output_path):
    """
    Clips a set of landsat images to a given shapefile.
    """
    tempdir = tempfile.mkdtemp(prefix='imgclip')
    try:
        for bundle in landsat_bundles:
            logging.info("Processing %s in %s", bundle, tempdir)
            landsat.process_landsat_bundle(bundle, tempdir, lambda f: process_raster(shapefile, output_path, f))
    finally:
        shutil.rmtree(tempdir)
    
    
        
def main():
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) < 3:
        print "Usage: %s <shapefile> <output_path>" % sys.argv[0]
        sys.exit(-1)
    
    shapefile = sys.argv[1]
    output_path = sys.argv[2]
    files = sys.argv[3:]
    
    logging.info('Masking by %s in %s', shapefile, output_path)
    
    if not os.path.exists(output_path):
        os.mkdir(output_path)
        
    clip_imagery(files, shapefile, output_path)
    
if __name__ == '__main__':
    main()