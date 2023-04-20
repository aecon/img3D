###################################################
# File Name     : tif_to_raw.py
# Creation Date : 18-04-2023
# Last Modified : Thu 20 Apr 2023 10:14:13 AM UTC
# Author        : Athena Economides
# Email         : athena.economides@uzh.ch
###################################################

import img3

if __name__ == "__main__":

    # Input tif data
    tif_path = "../data/data.tif"

    # Specify output raw and nrrd paths
    raw_path = "example1.raw"
    nrrd_path = "example1.nrrd"

    # Convert tif to raw/nrrd
    img3.tif2raw(tif_path, raw_path, nrrd_path)

