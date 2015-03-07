# Remote Sensing Tools

A set of tools and Python libraries to automate various tasks involved in
remote sensing.

## Executable Tools

### landsattool.py

A tool to build image composites from Landsat 8 OLI/TIRS datasets. It supports
using either GDAL or ArcGIS as its GIS layer and builds composite images from
individual bands in a Landsat 8 download. Does not require extracting the
downloaded tar.gz file prior to operation.

#### Examples

Build a true color image from a downloaded Landsat 8 OLI/TIRS bundle:

```
$ python landsattool.py LC80340352014167LGN00.tar.gz visible.tif
```

Build an image using SWIR for red, NIR for green, and coastal aerosol for blue:

```
$ python landsattool.py --bands 7 5 1 -- LC80340352014167LGN00.tar.gz visible.tif
```

## Framework and API

The `pyrs` package contains a collection of Python modules that can be used to
automate image processing in other Python applications. The top level modules
are built using GIS kernels, the implementations of which are defined in the
`python.kernel` package. The GIS kernels are expected to provide the underlying
image I/O and GIS operations that algorithms defined in the top level package
may utilize for their analyses.
