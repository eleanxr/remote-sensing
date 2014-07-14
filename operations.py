import cv2
import numpy as np
from matplotlib import pyplot as plt

import constants

months = ['SEPT', 'DEC', 'MAR']

def ndvi(red, nir):
    red_float = red.astype(float)
    nir_float = nir.astype(float)
    return 256 * np.divide(nir_float - red_float, nir_float + red_float)

def main():
    RED = 4
    NIR = 5
    
    histograms = {}
    for month in months:
        print 'Month = %s' % month
        red_image = cv2.imread(constants.base_name_named % (month, RED))
        nir_image = cv2.imread(constants.base_name_named % (month, NIR))
        
        print "Computing NDVI..."
        ndvi_image = ndvi(red_image, nir_image)
        
        print "Writing output..."
        filename = 'ndvi_%s.tif' % month
        cv2.imwrite(filename, ndvi_image)
        
        print "Computing histogram..."
        read_image = cv2.imread(filename)
        histograms[month] = cv2.calcHist([read_image], [0], None, [256], [1, 256])

    for month, hist in histograms.iteritems():
        plt.plot(hist, lw=2, label = month)
    plt.legend()
    plt.show()

if __name__ == '__main__':
    main()