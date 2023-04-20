###################################################
# File Name     : load_nrrd.py
# Creation Date : 18-04-2023
# Last Modified : Wed 19 Apr 2023 01:46:01 PM UTC
# Author        : Athena Economides
# Email         : athena.economides@uzh.ch
###################################################


import img3


if __name__ == "__main__":

    # Generate raw/nrrd files from tif data
    tif_path = "../large_data.tif"
    raw_path = "example2.raw"
    nrrd_path = "example2.nrrd"
    img3.tif2raw(tif_path, raw_path, nrrd_path)

    # Load raw/nrrd files
    dtype, path, shape, offset, dx, dy, dz = img3.nrrd_details(nrrd_path)
    raw_data = img3.read_input(nrrd_path, path, dtype, offset, shape)
    print("Shape of raw data:", raw_data.shape)

