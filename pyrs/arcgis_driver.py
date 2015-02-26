from kernel.arcgis.arcgis_kernel import arcgis_registry
import sample_region

import logging
logging.basicConfig(level=logging.DEBUG)

def sample_rasters():
    registry = arcgis_registry("C:\\Data\\TestSampling")
    sample_region.run_sampling(
        registry,
        "ndvi_landsat_13SDU05049011.tif",
        "13SDU050490_201203_0x2000m_CL_1.jp2",
        5)

if __name__ == "__main__":
    sample_rasters()
