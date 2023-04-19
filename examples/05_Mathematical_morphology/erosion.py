###################################################
# File Name     : erosion.py
# Creation Date : 19-04-2023
# Last Modified : Wed 19 Apr 2023 02:30:56 PM UTC
# Author        : Athena Economides
# Email         : athena.economides@uzh.ch
###################################################


import img3
import numpy as np


if __name__ == "__main__":

    nrrd_path = "example5.nrrd"

    # Load raw/nrrd files
    dtype, path, shape, offset, dx, dy, dz = img3.nrrd_details(nrrd_path)
    original_raw = img3.read_input(nrrd_path, path, dtype, offset, shape)

    # Create space for input and output files
    # - arrays must have data type uint8
    input_raw  = img3.mmap_create("input.raw", np.dtype("uint8"), shape)
    img3.nrrd_write("input.nrrd", "input.raw", input_raw.dtype, input_raw.shape, (1,1,1))
    output_raw = img3.mmap_create("output.raw", np.dtype("uint8"), shape)
    img3.nrrd_write("output.nrrd", "output.raw", output_raw.dtype, output_raw.shape, (1,1,1))

    # Copy original_raw into input_raw
    input_raw[:,:,:] = original_raw[:,:,:]

    # Perform an erosion on input_raw, Nstep times
    Nstep = 10
    img3.erosion(input_raw, Nstep, output_raw)

