import cv2
import numpy as np
from matplotlib import pyplot as plt

import constants

import os

months = ['JUN', 'SEPT', 'DEC', 'MAR']

def ndvi(red, nir):
    red_float = red.astype(float)
    nir_float = nir.astype(float)
    return np.divide(nir_float - red_float, nir_float + red_float)

def compute_roi(x_range, y_range, name, outdir=''):
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

        
        cv2.imwrite(
            os.path.join(outdir, 'subset_red_%s_%s.tif' % (name, month)), red_image)
        cv2.imwrite(
            os.path.join(outdir, 'subset_nir_%s_%s.tif' % (name, month)), nir_image)
        
        print "Computing NDVI..."
        ndvi_image = ndvi(red_image, nir_image)
        
        print "Writing output..."
        filename = os.path.join(outdir, 'ndvi_%s_%s.tif' % (name, month))
        cv2.imwrite(filename, ndvi_image)
        
        print "Computing histogram..."
        hist, edges = np.histogram(ndvi_image, 128)
        hist = hist / float(ndvi_image.size)
        histograms[month] = (hist, edges)
    return histograms

def plot_histograms(histograms, plot_obj, title):
    for month, (hist, edges) in histograms.iteritems():
        centers = 0.5 * (edges[1:] + edges[:-1])
        plot_obj.plot(centers, hist, lw=2, label = month)
    plot_obj.legend()
    plot_obj.set_title(title)
    plot_obj.set_xlim([0, 0.3])

boundary = 4648
xmin = 1231
xmax = 1924
ymin = 4418
ymax = 4859

def main():
    output_path = 'output_images'
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    
    fig, (whole, north, south) = plt.subplots(nrows = 3)
    plot_histograms(compute_roi((xmin, xmax), (ymin, ymax), 'Region', output_path), whole, 'Region')
    plot_histograms(compute_roi((xmin, xmax), (boundary, ymax), 'South', output_path), south, 'South')
    plot_histograms(compute_roi((xmin, xmax), (ymin, boundary), 'North', output_path), north, 'North')
    plt.show()

if __name__ == '__main__':
    main()
