import os
import tarfile
import sys

LANDSAT_BANDS = [
    None,
    {"Name": "Coastal Aerosol", "Range": (0.43e-6, 0.45e-6), "Resolution": 30.0}, #1
    {"Name": "Blue", "Range": (0.45e-6, 0.51e-6), "Resolution": 30.0}, #2
    {"Name": "Green", "Range": (0.53e-6, 0.59e-6), "Resolution": 30.0}, #3
    
    {"Name": "Red", "Range": (0.64e-6, 0.67e-6), "Resolution": 30.0}, #4
    {"Name": "NIR", "Range": (0.85e-6, 0.88e-6), "Resolution": 30.0}, #5
    {"Name": "SWIR 1", "Range": (1.57e-6, 1.65e-6), "Resolution": 30.0}, #6
    
    {"Name": "SWIR 2", "Range": (2.11e-6, 2.29e-6), "Resolution": 30.0}, #7
    {"Name": "Pan Chromatic", "Range": (0.50e-6, 0.68e-6), "Resolution": 15.0}, #8
    {"Name": "Cirrus", "Range": (1.36e-6, 1.38e-6), "Resolution": 30.0}, #9
    
    {"Name": "TIRS 1", "Range": (10.6e-6, 11.19e-6), "Resolution": 30.0 * 100.0}, #10
    {"Name": "TIRS 2", "Range": (11.5e-6, 12.51e-6), "Resolution": 30.0 * 100.0}, #11
]

def extract_landsat_bundle(landsat_download, output_path):
    archive = tarfile.open(landsat_download)
    archive.extractall(output_path)
    
def process_landsat_bundle(landsat_download, output_path, raster_transform):
    archive = tarfile.open(landsat_download)
    rasters = filter(lambda f: os.path.splitext(f.name)[1].lower() == '.tif', archive.getmembers())
    # Extract them.
    archive.extractall(output_path, rasters)
    # Process them
    for raster in rasters:
        raster_path = os.path.join(output_path, raster.name)
        raster_transform(raster_path)
    
    
def main():
    if len(sys.argv) < 2:
        print "Usage: %s <output-path>" % sys.argv[0]
        sys.exit(-1)
    for archive in sys.argv[2:]:
        print "Extracting %s" % archive
        extract_landsat_bundle(archive, sys.argv[1])
        
if __name__ == '__main__':
    main()
    