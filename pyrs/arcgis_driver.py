from kernel.arcgis.arcgis_kernel import arcgis_registry
import sample_region

def sample_rasters():
    registry = arcgis_registry("C:\\Data\\FractionalCoverDemo3")
    sample_region.run_sampling(
        registry,
        "ndvi_landsat_13SDU05049011.tif",
        "13SDU050490_201203_0x2000m_CL_1.jp2",
        5)
