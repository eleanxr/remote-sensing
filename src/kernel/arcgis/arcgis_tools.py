import arcpy
from arcpy import env
from arcpy.sa import *

import numpy as np
from matplotlib import pyplot as plt

env.workspace = 'C:/Data/Grazing'
env.overwriteOutput = True

months = ["SEPT", "DEC", "MAR"]

base_name = 'SEPT_B%d.TIF'

inside_point = (351940.756, 3806355.54)
outside_point = (353462.113, 3811316.488)
radius = 2000
extractionType = "INSIDE"

def make_point(t):
    return arcpy.Point(t[0], t[1])

def compute_ndvi(red, nir, savename):
    
    def map_raster(raster):
        return Float(Raster(raster))
    
    result = (map_raster(nir) - map_raster(red)) / (map_raster(nir) + map_raster(red))
    
    # Save the result for examination later.
    result.save(savename)
    
    return result
    
def main():
    arcpy.CheckOutExtension("Spatial")
    RED = 4
    NIR = 5

    inside_sums = []
    outside_sums = []
    
    for month in months:
        print "Begin month %s" % month
        red_raster = '%s_B%d.TIF' % (month, RED)
        nir_raster = '%s_B%d.TIF' % (month, NIR)
    
        print "Compute NDVI..."
        ndvi_raster = compute_ndvi(red_raster, nir_raster, 'NDVI_%s' % month)
        print "Extracting regions..."
        inside_circle = ExtractByCircle(ndvi_raster, make_point(inside_point), radius, extractionType)
        inside_circle.save('out_inside')
        outside_circle = ExtractByCircle(ndvi_raster, make_point(outside_point), radius, extractionType)
        outside_circle.save('out_outside')
        
        print "Compute sums..."
        inside_array = arcpy.RasterToNumPyArray(inside_circle).ravel()
        inside_sums.append(np.sum(inside_array))
        outside_array = arcpy.RasterToNumPyArray(outside_circle).ravel()
        outside_sums.append(np.sum(outside_array))
        del inside_array
        del outside_array

    
    plt.plot(inside_sums, color='blue')
    plt.plot(outside_sums, color='red')
    plt.show()

if __name__ == '__main__':
    main()
