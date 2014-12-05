import arcpy
from arcpy import env
from arcpy.sa import *
import random
import os
import csv
import numpy as np

def get_float_property(raster, name):
    return float(arcpy.GetRasterProperties_management(raster, name).getOutput(0))
