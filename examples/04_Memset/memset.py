###################################################
# File Name     : memset.py
# Creation Date : 19-04-2023
# Last Modified : Wed 19 Apr 2023 10:09:36 AM UTC
# Author        : Athena Economides
# Email         : athena.economides@uzh.ch
###################################################


import img3

if __name__ == "__main__":

    nrrd_path = "../data/example.nrrd"

    # Create space for output file
    output_raw = img3.mmap_create("output.raw", dtype, shape)
    spacings = (1,1,1)
    img3.nrrd_write("output.nrrd", "output.raw", output_raw.dtype, output_raw.shape, spacings)

    # Set all values inside output_raw to 0
    img3.memset(output_raw, 0)

