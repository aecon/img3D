###################################################
# File Name     : copy.py
# Creation Date : 19-04-2023
# Last Modified : Wed 19 Apr 2023 10:08:16 AM UTC
# Author        : Athena Economides
# Email         : athena.economides@uzh.ch
###################################################


import img3
import numba


@numba.njit(parallel=True)
def copy(inp, out):
    nx, ny, nz = inp.shape
    for k in numba.prange(nz):
        for j in numba.prange(ny):
            for i in numba.prange(nx):
                out[i, j, k] = inp[i, j, k]


if __name__ == "__main__":

    nrrd_path = "../data/example.nrrd"

    # Load raw/nrrd files
    dtype, path, shape, offset, dx, dy, dz = img3.nrrd_details(nrrd_path)
    raw_path = img3.read_input(nrrd_path, path, dtype, offset, shape)

    # Create space for output file
    output_raw = img3.mmap_create("output.raw", dtype, shape)
    spacings = (1,1,1)
    img3.nrrd_write("output.nrrd", "output.raw", output_raw.dtype, output_raw.shape, spacings)

    # Copy data from raw_path to output_raw
    copy(input_raw, output_raw)

