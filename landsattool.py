import pyrs.landsat

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

import os

import argparse

def get_arcgis_registry(data_path):
    from pyrs.kernel.arcgis import arcgis_kernel
    return arcgis_kernel.arcgis_registry(data_path)
    
def get_gdal_registry(data_path):
    from pyrs.kernel.gdal import gdal_kernel
    return gdal_kernel.gdal_registry(data_path)


    
def main():
    parser = argparse.ArgumentParser(description="Tool for bulk processing Landsat imagery")
    parser.add_argument("landsat_download", help="The name of the Landsat download to process")
    parser.add_argument("output_file", help="The name of the raster to save results to")
    parser.add_argument("--bands", nargs="+", default=[4,3,2], help="The spectral bands to build the composite image from")
    parser.add_argument("--publish", help="The name of the image server instance to publish the result to")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite results if they already exist")
    args = parser.parse_args()
    
    data_path = os.path.dirname(args.landsat_download)
    landsat_file = os.path.basename(args.landsat_download)
    
    bands = map(lambda x: int(x), args.bands)
    logger.info("processing %s bands %s in %s to %s", landsat_file, bands, data_path, args.output_file)
    
    # TODO make a parameter for this.
    try:
        import arcpy    
        registry = get_arcgis_registry(data_path)
    except:
        registry = get_gdal_registry(data_path)
    
    if args.overwrite or not os.path.exists(os.path.join(data_path, args.output_file)):
        info, rasters = pyrs.landsat.read_bands(registry, data_path, landsat_file, bands)
        composite_raster = registry.create_composite(args.output_file, *rasters)
    else:
        info = pyrs.landsat.LandsatInfo(data_path, pyrs.landsat.get_scene_id_from_filename(landsat_file))
        composite_raster = registry.open_raster(args.output_file)
        print("{} already exists. Use --overwrite to recompute.".format(args.output_file))
    
    if (args.publish and composite_raster):
        logger.info("Publishing result for %s to %s", info.get_scene_id(), args.publish)
        publisher = registry.get_publishing_service(args.publish.strip())
        publisher.publish_image(composite_raster, info)
        
    
if __name__ == '__main__':
    main()
