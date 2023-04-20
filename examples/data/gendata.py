import img3
import tifffile
import numpy as np


# Generate tif data
tifffile.imwrite("data.tif",
                 np.random.randint(0, 255, (10, 20, 30), 'uint8'))

# Generate corresponding raw/nrrd data
img3.tif2raw("data.tif", "data.raw", "data.nrrd")

