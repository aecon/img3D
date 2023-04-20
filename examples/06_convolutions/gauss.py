###################################################
# File Name     : gauss.py
# Creation Date : 20-04-2023
# Last Modified : Thu 20 Apr 2023 10:39:36 AM UTC
# Author        : Athena Economides
# Email         : athena.economides@uzh.ch
###################################################


import img3
import numpy as np


if __name__ == "__main__":

    nrrd_path = "../data/data.nrrd"

    # Load raw/nrrd data
    dtype, path, shape, offset, dx, dy, dz = img3.nrrd_details(nrrd_path)
    input_raw = img3.read_input(nrrd_path, path, dtype, offset, shape)

    # Storage for generated data
    mask       = img3.mmap_create("mask.raw",  np.dtype(np.uint8),   shape)
    tmp32      = img3.mmap_create("tmp32.raw", np.dtype(np.float32), shape)
    output_raw = img3.mmap_create("gauss.raw", np.dtype(np.float32), shape)
    img3.nrrd_write("gauss.nrrd", "gauss.raw", output_raw.dtype, output_raw.shape, (dx,dy,dz))

    # Set all pixels of the mask to 1
    img3.memset(mask, 1)

    # Copy input data to tmp32
    # because it will be modified by img3.gauss
    tmp32[:,:,:] = input_raw[:,:,:]

    # Gaussian smoothing in a mask
    sigma = 1  # standard deviation
    img3.gauss(tmp32, mask, sigma, output_raw)

