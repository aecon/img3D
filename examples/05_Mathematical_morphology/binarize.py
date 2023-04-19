###################################################
# File Name     : binarize.py
# Creation Date : 19-04-2023
# Last Modified : Wed 19 Apr 2023 02:28:15 PM UTC
# Author        : Athena Economides
# Email         : athena.economides@uzh.ch
###################################################


import img3
import numba
import numpy as np


@numba.njit(parallel=True)
def binary(inp, out, val):
    nx, ny, nz = inp.shape
    for k in numba.prange(nz):
        for j in numba.prange(ny):
            for i in numba.prange(nx):
                out[i, j, k] = 1 if inp[i, j, k] > val else 0


if __name__ == "__main__":

    # Generate raw/nrrd files from tif data
    tif_path = "../large_data.tif"
    raw_path = "example5.raw"
    nrrd_path = "example5.nrrd"
    img3.tif2raw(tif_path, raw_path, nrrd_path)

    # Load raw/nrrd files
    dtype, path, shape, offset, dx, dy, dz = img3.nrrd_details(nrrd_path)
    input_raw = img3.read_input(nrrd_path, path, dtype, offset, shape)

    # Reserve storage for output file
    output_raw = img3.mmap_create("binary.raw", np.dtype("uint8"), shape)
    img3.nrrd_write("binary.nrrd", "binary.raw", output_raw.dtype, output_raw.shape, (1,1,1))

    # Binarize raw_path based on a threshold
    binary(input_raw, output_raw, 220)

