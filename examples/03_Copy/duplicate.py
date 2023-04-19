###################################################
# File Name     : copy.py
# Creation Date : 19-04-2023
# Last Modified : Wed 19 Apr 2023 01:56:54 PM UTC
# Author        : Athena Economides
# Email         : athena.economides@uzh.ch
###################################################


import img3
import numba


@numba.njit(parallel=True)
def copy_array(inp, out):
    nx, ny, nz = inp.shape
    for k in numba.prange(nz):
        for j in numba.prange(ny):
            for i in numba.prange(nx):
                out[i, j, k] = inp[i, j, k]


if __name__ == "__main__":

    # Generate raw/nrrd files from tif data
    tif_path = "../large_data.tif"
    raw_path = "example3.raw"
    nrrd_path = "example3.nrrd"
    img3.tif2raw(tif_path, raw_path, nrrd_path)

    # Load raw/nrrd files
    dtype, path, shape, offset, dx, dy, dz = img3.nrrd_details(nrrd_path)
    input_raw = img3.read_input(nrrd_path, path, dtype, offset, shape)

    # Reserve storage for output file
    output_raw = img3.mmap_create("example3o.raw", dtype, shape)
    spacings = (dx,dy,dz)
    img3.nrrd_write("example3o.nrrd", "example3o.raw", output_raw.dtype, output_raw.shape, spacings)

    # Copy data from raw_path to output_raw
    copy_array(input_raw, output_raw)

