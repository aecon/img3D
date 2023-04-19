###################################################
# File Name     : memset.py
# Creation Date : 19-04-2023
# Last Modified : Wed 19 Apr 2023 02:00:08 PM UTC
# Author        : Athena Economides
# Email         : athena.economides@uzh.ch
###################################################


import img3
import numpy as np


if __name__ == "__main__":

    # Create space for output file
    shape = np.asarray([100,100,100])
    output_raw = img3.mmap_create("example4.raw", np.dtype(np.uint8), shape)
    spacings = (1,1,1)
    img3.nrrd_write("example4.nrrd", "example4.raw", output_raw.dtype, output_raw.shape, spacings)

    # Set all values inside output_raw to 10
    img3.memset(output_raw, 10)

