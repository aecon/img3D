###################################################
# File Name     : save_nrrd.py
# Creation Date : 18-04-2023
# Last Modified : Wed 19 Apr 2023 01:47:13 PM UTC
# Author        : Athena Economides
# Email         : athena.economides@uzh.ch
###################################################


import img3
import numpy as np

if __name__ == "__main__":

    # Create a new raw array of type uint8 with given shape
    shape = np.asarray([10,10,10])
    new_array = img3.mmap_create("example2b.raw", np.dtype(np.uint8), shape)

    # Create corresponding nrrd file
    #   spacings: pixel size in x,y,z
    spacings = (1,1,1)
    img3.nrrd_write("example2b.nrrd", "example2b.raw", new_array.dtype, new_array.shape, spacings)

