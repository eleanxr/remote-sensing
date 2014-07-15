import cv2
import numpy as np
from matplotlib import pyplot as plt

import constants

months = ['JUN', 'SEPT', 'DEC', 'MAR']

def ndvi(red, nir):
    red_float = red.astype(float)
    nir_float = nir.astype(float)
    return 256 * np.divide(nir_float - red_float, nir_float + red_float)

def compute_roi(x_range, y_range, name):
    RED = 4
    NIR = 5
    histograms = {}
    for month in months:
        print 'Month = %s' % month
        red_image = cv2.imread(constants.base_name_named % (month, RED))
        nir_image = cv2.imread(constants.base_name_named % (month, NIR))
        
        print 'Subsetting...'
        red_image = red_image[y_range[0]:y_range[1], x_range[0]:x_range[1]]
        nir_image = nir_image[y_range[0]:y_range[1], x_range[0]:x_range[1]]

        
        cv2.imwrite('subset_red_%s.tif' % month, red_image)
        cv2.imwrite('subset_nir_%s.tif' % month, nir_image)
        
        print "Computing NDVI..."
        ndvi_image = ndvi(red_image, nir_image)
        
        print "Writing output..."
        filename = 'ndvi_%s_%s.tif' % (name, month)
        cv2.imwrite(filename, ndvi_image)
        
        print "Computing histogram..."
        read_image = cv2.imread(filename)
        histograms[month] = cv2.calcHist([read_image], [0], None, [256], [0, 256]) / read_image.size
    return histograms

def plot_histograms(histograms, plot_obj, title):
    for month, hist in histograms.iteritems():
        plot_obj.plot(hist, lw=2, label = month)
    plot_obj.legend()
    plot_obj.set_title(title)
    plot_obj.set_xlim([0, 128])

boundary = 4648
xmin = 1231
xmax = 1924
ymin = 4418
ymax = 4859

def main():
    fig, (whole, north, south) = plt.subplots(nrows = 3)
    plot_histograms(compute_roi((xmin, xmax), (ymin, ymax), 'Region'), whole, 'Region')
    plot_histograms(compute_roi((xmin, xmax), (boundary, ymax), 'South'), south, 'South')
    plot_histograms(compute_roi((xmin, xmax), (ymin, boundary), 'North'), north, 'North')
    plt.show()

if __name__ == '__main__':
    main()