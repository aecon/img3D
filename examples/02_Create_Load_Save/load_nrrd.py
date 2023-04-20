###################################################
# File Name     : load_nrrd.py
# Creation Date : 18-04-2023
# Last Modified : Thu 20 Apr 2023 10:17:36 AM UTC
# Author        : Athena Economides
# Email         : athena.economides@uzh.ch
###################################################


import img3


if __name__ == "__main__":

    # nrrd file path
    nrrd_path = "../data/data.nrrd"

    # Load raw/nrrd files
    dtype, path, shape, offset, dx, dy, dz = img3.nrrd_details(nrrd_path)
    raw_data = img3.read_input(nrrd_path, path, dtype, offset, shape)
    print("Shape of raw data:", raw_data.shape)

