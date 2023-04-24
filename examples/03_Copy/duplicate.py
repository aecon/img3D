###################################################
# File Name     : copy.py
# Creation Date : 19-04-2023
# Last Modified : Mon 24 Apr 2023 10:01:29 AM UTC
# Author        : Athena Economides
# Email         : athena.economides@uzh.ch
###################################################


import img3
import numpy as np


if __name__ == "__main__":

    # nrrd file path
    nrrd_path = "../data/data.nrrd"

    # Load raw/nrrd files
    dtype, path, shape, offset, dx, dy, dz = img3.nrrd_details(nrrd_path)
    input_raw = img3.read_input(nrrd_path, path, dtype, offset, shape)

    # Reserve storage for output file
    output_raw = img3.mmap_create("example3.raw", dtype, shape)
    spacings = (dx,dy,dz)
    img3.nrrd_write("example3.nrrd", "example3.raw", output_raw.dtype, output_raw.shape, spacings)

    # Copy data from input_raw to output_raw
    np.copyto(output_raw, input_raw, casting='no')

