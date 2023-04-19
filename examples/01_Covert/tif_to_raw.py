###################################################
# File Name     : tif_to_raw.py
# Creation Date : 18-04-2023
# Last Modified : Wed 19 Apr 2023 01:43:20 PM UTC
# Author        : Athena Economides
# Email         : athena.economides@uzh.ch
###################################################

import img3

if __name__ == "__main__":

    # Input tif data
    tif_path = "../large_data.tif"

    # Specify output raw and nrrd paths
    raw_path = "example1.raw"
    nrrd_path = "example1.nrrd"

    # Convert tif to raw/nrrd
    img3.tif2raw(tif_path, raw_path, nrrd_path)

