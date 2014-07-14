import cv2
import numpy as np
from matplotlib import pyplot as plt

import constants

def ndvi(red, nir):
    return np.divide(nir - red, nir + red)

RED = 4
NIR = 5

red_image = cv2.imread(constants.base_name % RED)
nir_image = cv2.imread(constants.base_name % NIR)

ndvi_image = ndvi(red_image, nir_image)

cv2.imshow('NDVI', ndvi_image)
cv2.waitKey(0)
cv2.destroyAllWindows()