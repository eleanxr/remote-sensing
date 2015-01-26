import sample_region

import unittest

class test_registry(object):
    def __init__(self):
        pass
    def open_raster(self, filename):
        return test_raster()

class test_raster(object):
    def __init__(self):
        pass

    def get_extent(self):
        return (1.0, 0.0, 1.0, 0.0)

    def get_pixel_size(self):
        return (0.5, 0.5)

    def create_feature(self, output, polygon):
        pass

    def clip(self, feature, output):
        pass

class TestSampleRaster(unittest.TestCase):
    def setUp():
        self.regsitry = test_registry()

    def test_sample_raster():
        sample_region.sample_raster(
            self.registry.open_raster('lo'),
            self.registry.open_raster('hi'),
            2,
            1)
        
