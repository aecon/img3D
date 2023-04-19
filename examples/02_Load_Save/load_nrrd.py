###################################################
# File Name     : load_nrrd.py
# Creation Date : 18-04-2023
# Last Modified : Wed 19 Apr 2023 08:32:05 AM UTC
# Author        : Athena Economides
# Email         : athena.economides@uzh.ch
###################################################


import img3
import os

if __name__ == "__main__":

    nrrd_path = "example.nrrd"

    # If raw/nrrd files do not exist, generate them
    if os.path.isfile(nrrd_path) == False:
        tif_path = "../data/example.tif"
        raw_path = "example.raw"
        nrrd_path = "example.nrrd"
        img3.tif2raw(tif_path, raw_path, nrrd_path)

    # Load raw/nrrd files
    dtype, path, shape, offset, dx, dy, dz = img3.nrrd_details(nrrd_path)
    raw_data = img3.read_input(nrrd_path, path, dtype, offset, shape)
    print("Shape of raw data:", raw_data.shape)

