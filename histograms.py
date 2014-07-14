import cv2
import numpy as np
from matplotlib import pyplot as plt

base_name = '/Users/willdichary/Data/Grazing/LC80330362013269LGN00/LC80330362013269LGN00_B%d.TIF'

for band in range(1, 12):
    band_image = cv2.imread(base_name % band)
    band_hist = cv2.calcHist([band_image], [0], None, [256], [1, 256])
    plt.plot(band_hist)
plt.show()