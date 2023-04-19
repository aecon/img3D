###################################################
# File Name     : save_nrrd.py
# Creation Date : 18-04-2023
# Last Modified : Wed 19 Apr 2023 08:36:23 AM UTC
# Author        : Athena Economides
# Email         : athena.economides@uzh.ch
###################################################


import img3
import numpy as np

if __name__ == "__main__":

    # Create a new raw array of type uint8 with given shape
    shape = np.asarray([10,10,10])
    new_array = img3.mmap_create("new_array.raw", np.dtype(np.uint8), shape)

    # Create corresponding nrrd file
    #   spacings: pixel size in x,y,z
    spacings = (1,1,1)
    img3.nrrd_write("new_array.nrrd", "new_array.raw", new_array.dtype, new_array.shape, spacings)

