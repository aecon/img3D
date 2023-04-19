import tifffile
import numpy as np

tifffile.imwrite("large_data.tif",
                 np.random.randint(0, 255, (10, 20, 30), 'uint8'))
