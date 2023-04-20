###################################################
# File Name     : create_nrrd.py
# Creation Date : 20-04-2023
# Last Modified : Thu 20 Apr 2023 09:45:56 AM UTC
# Author        : Athena Economides
# Email         : athena.economides@uzh.ch
###################################################


import img3
import numpy as np

if __name__ == "__main__":

    # Define shape of array:
    #   shape = (px, py, pz)
    #   where px, py, pz is the number of pixels
    #   in the x,y,z directions respectively
    shape = np.asarray([10,10,10])

    # Create new arrays with types commonly 
    # used in image processing pipelines

    # - uint8 for binary (0/1) data
    array1 = img3.mmap_create("example2i.raw", np.dtype(np.uint8), shape)

    # - float32 for floating point values
    array2 = img3.mmap_create("example2ii.raw", np.dtype(np.float32), shape)

    # - int64 for indexing objects
    array3 = img3.mmap_create("example2iii.raw", np.dtype(np.int64), shape)

