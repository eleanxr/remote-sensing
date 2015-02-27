from kernel.arcgis.arcgis_kernel import arcgis_registry
import landsat

import logging
logging.basicConfig(level=logging.DEBUG)

def make_composite():
    registry = arcgis_registry("C:\\Data\\Landsat")
    r, g, b = landsat.read_bands(registry, "C:\\Data\\Landsat", "LC80330362014160LGN00.tar.gz", [7, 5, 1])
    registry.create_composite("visible.tif", r, g, b)
    
if __name__ == '__main__':
    make_composite()
