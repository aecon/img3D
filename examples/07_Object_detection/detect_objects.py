###################################################
# File Name     : detect_objects.py
# Creation Date : 20-04-2023
# Last Modified : Thu 20 Apr 2023 12:46:07 PM UTC
# Author        : Athena Economides
# Email         : athena.economides@uzh.ch
###################################################


import img3
import numpy as np


if __name__ == "__main__":

    # Specify shape of arrays
    shape = np.asarray([10, 20, 30])

    # Storage for generated data
    raw      = img3.mmap_create("input.raw",    np.dtype(np.uint8 ), shape)
    work     = img3.mmap_create("work.raw",     np.dtype(np.int64 ), shape)
    labels   = img3.mmap_create("labels.raw",   np.dtype(np.int64 ), shape)
    labels32 = img3.mmap_create("labels32.raw", np.dtype(np.uint32), shape)
    img3.nrrd_write("labels32.nrrd", "labels32.raw", labels32.dtype, labels32.shape, (1,1,1))

    # Generate binary (0/1) raw data
    raw[:,:,:] = np.random.randint(0, 2, shape, 'uint8')

    # Label connected components
    img3.memset(labels, 0)
    Nclusters = img3.labels(raw, labels, work)
    print("Detected %d clusters" % Nclusters)

    # Remove small objects
    min_volume = 2
    Nlarge = img3.remove_small_objects(labels, min_volume, work)
    print("Detected %d clusters with volume > %d" % (Nlarge, min_volume))

    # To visualize the clusters store in np.uint32 type
    labels32[:,:,:] = labels[:,:,:]

    # Get x,y,z coordinates of all pixels belonging in a cluster
    lst = img3.objects(labels, Nlarge)

