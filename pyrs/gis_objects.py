"""
Interface definitions for GIS objects to be delegated to kernel implementations
"""

class GisObjectRegistry(object):
    """
    Factory class for creating GIS objects.
    """
    def open_feature(self, filename):
        """
        Open a new feature from a file.
        """
        raise NotImplementedError

    def open_raster(self, filename):
        """
        Open a raster from a file.
        """
        raise NotImplementedError

class Raster(object):
    """
    Interface for raster objects.
    """
    def get_extent(self):
        """
        Get the extent of a raster in its spatial reference.
        Returns a tuple (top, left, right, bottom)
        """
        raise NotImplementedError

    def get_pixel_size(self):
        """
        Get the pixel size of the raster in its spatial reference.
        Returns a tuple (pixel_size_x, pixel_size_y)
        """
        raise NotImplementedError

    def create_feature(self, output, polygon):
        """
        Create a polygonal feature using the spatial reference
        of this raster.
        
        Parameters
        ----------
        output : str
        polygon : iterable set of (x, y) tuples.

        Returns
        -------
        Feature
        """
        raise NotImplementedError

    def clip(self, **kwargs):
        """
        Clip this raster given a feature.
        """
        raise NotImplementedError

