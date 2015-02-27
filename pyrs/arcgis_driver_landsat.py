from kernel.arcgis.arcgis_kernel import arcgis_registry
import landsat

import logging
logging.basicConfig(level=logging.DEBUG)

def make_composite():
    registry = arcgis_registry("C:\\Data\\Landsat")
    r, g, b = landsat.read_bands(registry, "C:\\Data\\Landsat", "LC80380382015022LGN00.tar.gz", [4, 3, 2])
    registry.create_composite("visible.tif", b, g, r)
    
if __name__ == '__main__':
    make_composite()
