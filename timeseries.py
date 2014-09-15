import landsat
import operations
import rasterclip
import tempfile
import shutil
import os
import sys

import numpy
import csv

from PIL import Image

import logging
logger = logging.getLogger(__name__)

def process_raster(shapefile, output_path, raster_path):
    logger.debug('process_raster %s %s %s', shapefile, output_path, raster_path)
    rastername = os.path.basename(raster_path)
    rasterfile = os.path.splitext(rastername)[0]
    output_path = os.path.join(output_path, rasterfile)
    rasterclip.clip_raster(raster_path, shapefile, output_path)

def clip_imagery(landsat_bundles, shapefile, output_path):
    """
    Clips a set of landsat images to a given shapefile.
    Returns a list of landsat scene ids.
    """
    tempdir = tempfile.mkdtemp(prefix='imgclip')
    ids = []
    try:
        for bundle in landsat_bundles:
            logging.info("Processing %s in %s", bundle, tempdir)
            bundle_id = landsat.process_landsat_bundle(bundle, tempdir, lambda f: process_raster(shapefile, output_path, f))
            ids.append(bundle_id)
    finally:
        shutil.rmtree(tempdir)
    return ids

def ndvi_manual(red, nir):
    denom = float(red) + float(nir)
    if denom == 0:
        return 0
    else:
        return (nir - red) / denom

def compute_ndvi(band_arrays):
    red = band_arrays[0].astype(float)
    nir = band_arrays[1].astype(float)
    num = nir - red
    denom = nir + red
    result = numpy.divide(num, denom)
    return numpy.ma.masked_invalid(result)

def compute_ndvi_vectorized(band_arrays):
    red = band_arrays[0]
    nir = band_arrays[1]
    return numpy.vectorize(ndvi_manual)(red, nir)

def compute_savi(band_arrays):
    red_float = band_arrays[0].astype(float)
    nir_float = band_arrays[1].astype(float)
    l = 0.5 # suggested soil correction.
    return numpy.divide(nir_float - red_float, nir_float + red_float + l) * (1 + l)

    
def write_raster(raster, path, name):
    # Rescale
    #rescaled = (255.0 / raster.max()) * (raster - raster.min())
    rescaled = (255.0 * raster).astype(int)
    im = Image.fromarray(rescaled.astype(numpy.uint8))
    im.save(os.path.join(path, name + '.tif'))
        
def main():
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) < 3:
        print "Usage: %s <shapefile> <output-path>" % sys.argv[0]
        sys.exit(-1)
    
    shapefile = sys.argv[1]
    output_path = sys.argv[2]
    files = sys.argv[3:]
    
    logging.info('Masking by %s in %s', shapefile, output_path)
    
    if not os.path.exists(output_path):
        os.mkdir(output_path)
        
    scene_ids = clip_imagery(files, shapefile, output_path)
    
    with (open(os.path.join(output_path, 'results.csv'), 'w')) as dataout:
        csvfile = csv.writer(dataout)
        csvfile.writerow(["scene_id", "mean", "std_dev"])
        
        numpy.seterr(divide='ignore')
        
        for scene_id in scene_ids:
            logger.debug('Calling combiner for %s', scene_id)
            result_raster = landsat.combine_landsat_bands(output_path, scene_id, compute_ndvi, [4, 5])
            write_raster(result_raster, output_path, scene_id + '_index')
            mean = numpy.mean(result_raster)
            sigma = numpy.std(result_raster)
            print mean, sigma
            csvfile.writerow([scene_id, mean, sigma])
    
if __name__ == '__main__':
    main()