###################################################
# File Name     : erosion.py
# Creation Date : 19-04-2023
# Last Modified : Wed 19 Apr 2023 09:04:58 AM UTC
# Author        : Athena Economides
# Email         : athena.economides@uzh.ch
###################################################


import img3
import os

if __name__ == "__main__":

    nrrd_path = "../data/example.nrrd"

    # Load raw/nrrd files
    dtype, path, shape, offset, dx, dy, dz = img3.nrrd_details(nrrd_path)
    raw_path = img3.read_input(nrrd_path, path, dtype, offset, shape)

    # Create space for input and output files
    input_raw  = img3.mmap_create("input.raw",  np.dtype("uint8"), shape)
    output_raw = img3.mmap_create("output.raw", np.dtype("uint8"), shape)

    input_raw[:,:,:] = raw_path[:,:,:]

    # Perform an erosion within a mask, Nstep times
    Nstep = 10
    img3.erosion(input_raw, Nstep, output_raw)

