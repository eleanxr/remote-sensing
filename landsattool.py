from pyrs.kernel.arcgis.arcgis_kernel import arcgis_registry
import pyrs.landsat

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

import os

import argparse

def main():
    parser = argparse.ArgumentParser(description="Tool for bulk processing Landsat imagery")
    parser.add_argument("landsat_download")
    parser.add_argument("output_file")
    parser.add_argument("--bands", nargs="+", default=[4,3,2])
    args = parser.parse_args()
    
    data_path = os.path.dirname(args.landsat_download)
    landsat_file = os.path.basename(args.landsat_download)
    
    bands = map(lambda x: int(x), args.bands)
    logger.info("processing %s bands %s in %s to %s", landsat_file, bands, data_path, args.output_file)
    
    registry = arcgis_registry(data_path)
    rasters = pyrs.landsat.read_bands(registry, data_path, landsat_file, bands)
    registry.create_composite(args.output_file, *rasters)
    
if __name__ == '__main__':
    main()
