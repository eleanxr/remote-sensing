import arcpy
from arcpy import env
from arcpy.sa import *

import numpy as np
from matplotlib import pyplot as plt

env.workspace = 'C:/Data/Grazing'
env.overwriteOutput = True

base_name = 'SEPT_B%d.TIF'

inside_point = (351940.756, 3806355.54)
outside_point = (353462.113, 3811316.488)
radius = 2000
extractionType = "INSIDE"

def make_point(t):
    return arcpy.Point(t[0], t[1])

def compute_ndvi(red, nir):
    
    def map_raster(raster):
        return Float(Raster(raster))
    
    result = (map_raster(nir) - map_raster(red)) / (map_raster(nir) + map_raster(red))
    
    # Save the result for examination later.
    result.save('ndvi')
    
    return result
    
def main():
    arcpy.CheckOutExtension("Spatial")
    RED = 4
    NIR = 5
    
    red_raster = base_name % RED
    nir_raster = base_name % NIR

    ndvi_raster = compute_ndvi(red_raster, nir_raster)
    inside_circle = ExtractByCircle(ndvi_raster, make_point(inside_point), radius, extractionType)
    inside_circle.save('out_inside')
    outside_circle = ExtractByCircle(ndvi_raster, make_point(outside_point), radius, extractionType)
    outside_circle.save('out_outside')
    
    inside_array = arcpy.RasterToNumPyArray(inside_circle)
    outside_array = arcpy.RasterToNumPyArray(outside_circle)

    plt.hist(inside_array.ravel(), 256, [-1, 1])
    plt.hist(outside_array.ravel(), 256, [-1, 1])
    plt.show()

if __name__ == '__main__':
    main()
