###################################################
# File Name     : process_all.py
# Creation Date : 29-03-2023
# Last Modified : Mon 03 Apr 2023 08:52:47 AM UTC
# Author        : Athena Economides
# Email         : athena.economides@uzh.ch
###################################################


import os
import sys
import time
import numba
import pickle
import argparse
import skimage.io
import numpy as np
import pandas as pd
from tifffile import imsave
from scipy.ndimage import label as slabel
from scipy.ndimage import binary_dilation

import img3


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# UTILITY FUNCTIONS
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~

me = "process_all.py"

def stamp(s):
    sys.stderr.write("%s: %d: %s\n" % (me, time.time() - start, s))

@numba.njit(parallel=True)
def binarize(a, out, value):
    nx, ny, nz = a.shape
    for k in numba.prange(nz):
        for j in numba.prange(ny):
            for i in numba.prange(nx):
                out[i, j, k] = 1 if a[i, j, k] > value else 0

@numba.njit(parallel=True)
def binarize2(a, out):
    nx, ny, nz = a.shape
    for k in numba.prange(nz):
        for j in numba.prange(ny):
            for i in numba.prange(nx):
                out[i, j, k] = 1 if a[i, j, k] == 2 else 0

def bin_particles(shape, limits, sample, odir, myfile):
    # 3D histogram
    H, edges = np.histogramdd(sample, range=( (0,limits[0]), (0,limits[1]), (0,limits[2]) ), bins=shape )

    # save to 3D image
    if not os.path.exists(odir):
        os.makedirs(odir)
    fraw  = "%s/%s.raw"  % (odir, os.path.basename(myfile))
    fnrrd = "%s/%s.nrrd" % (odir, os.path.basename(myfile))
    print(fraw)
    print(fnrrd)
    particles = img3.mmap_create(fraw, np.dtype("uint16"), shape)
    img3.nrrd_write(fnrrd, fraw, particles.dtype, particles.shape, (px,py,pz))
    particles[:,:,:] = H[:,:,:]

    return particles






start = time.time()

parser = argparse.ArgumentParser()
parser.add_argument('-m', type=str, nargs='+', required=True, help="MARKER (C2) csv file")
parser.add_argument('-c', type=str, nargs='+', required=True, help="LOCATION (C1/4) csv file")
parser.add_argument('-o', type=str, required=True, help="outdir")
# Defaults
parser.add_argument('-res', type=float, default=10, help="minimum resolution in nm")
args = parser.parse_args()



# Loop over csv file pairs
for fm,fc in zip(args.m, args.c):

    odir = args.o
    print("Output directory:", odir)

    print("Processing files:")
    print(" > %s" % fc)
    print(" > %s" % fm)


    #----------------------------------
    # Exclude duplicated C2 entries
    #----------------------------------
    stamp("loading csv data")
    datafile = pd.read_csv(fm)
    x = np.asarray(datafile['x [nm]'])
    y = np.asarray(datafile['y [nm]'])
    z = np.asarray(datafile['z [nm]'])

    # truncated coordinates
    zmin = abs(np.min(z))
    zres = args.res
    xt = np.floor(x/zres)
    yt = np.floor(y/zres)
    zt = np.floor((z+zmin)/zres)

    # unique particle rows
    C2 = (np.vstack([xt,yt,zt])).T
    stamp("np.unique")
    unique_C2, indices = np.unique(C2, axis=0, return_index=True)
    print(np.shape(indices))

    percentage_removed = (len(C2)-len(unique_C2)) / len(C2) * 100.
    stamp("Percentage of C2 markers removed: %.2f%%" % percentage_removed)

    # keep unique markers from original data
    xu = x[indices]
    yu = y[indices]
    zu = z[indices]


    #----------------------------------
    # Bin particles to 3D grid
    #----------------------------------
    # voxel size in um
    px = 0.0235
    py = 0.0235
    pz = 0.01
    spacings = (pz, py, pz)

    # 3D image shape
    shape = (2120, 3405, 200)
    limits = (shape[0]*px*1.e3, shape[1]*py*1.e3, shape[2]*pz*1.e3)

    # bin marker
    sample = (np.vstack([xu,yu,zu+1000])).T
    stamp("bin marker")
    img_m = bin_particles(shape, limits, sample, odir, fm)

    # bin channel
    stamp("loading channel csv data")
    datafile = pd.read_csv(fc)
    x = np.asarray(datafile['x [nm]'])
    y = np.asarray(datafile['y [nm]'])
    z = np.asarray(datafile['z [nm]'])
    sample = (np.vstack([x,y,z+1000])).T
    stamp("bin channel")
    img_c = bin_particles(shape, limits, sample, odir, fc)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # CREATE WORK ARRAYS
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    stamp("create working arrays")
    tmp8    = img3.mmap_create("%s/tmp8.raw" % odir, np.dtype("uint8"), shape)
    img3.memset(tmp8, 0)
    work    = img3.mmap_create("%s/work.raw" % odir, np.dtype(np.int64), shape)
    img3.memset(work, 0)
    labels  = img3.mmap_create("%s/labels.raw" % odir, np.dtype(np.int64), shape)
    img3.memset(labels, 0)

    debug = True
    if debug == True:
        fraw = "%s/labels16_%s.raw"  % (odir, os.path.basename(fc))
        fnrrd= "%s/labels16_%s.nrrd" % (odir, os.path.basename(fc))
        labels16 = img3.mmap_create(fraw, np.dtype(np.int16), shape)
        img3.memset(labels16, 0)
        img3.nrrd_write(fnrrd, fraw, labels16.dtype, labels16.shape, spacings)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # IMAGE PROCESSING
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # Binarization
    stamp("Thresholding and Binarization x2")
    min_particles = 2 # Ignore bins with 2 and fewer particles
    # marker
    bin_m = np.zeros(img_m.shape, dtype=np.dtype("uint8"))
    binarize(img_m, bin_m, min_particles)
    # channel
    bin_c = np.zeros(img_c.shape, dtype=np.dtype("uint8"))
    binarize(img_c, bin_c, min_particles)

    # Overlay marker and channel
    stamp("memset0 x2, overlay x1, binarization x1")
    img3.memset(work, 0)
    img3.memset(tmp8, 0)
    work[:,:,:] = (bin_m + bin_c)[:,:,:]
    binarize2(work, tmp8)

    # Connected components and labels of overlay
    img3.memset(work, 0)
    stamp("img3.labels")
    Nc = img3.labels(tmp8, labels, work)
    sys.stderr.write("  Nc(all): %d\n" % Nc)

    # Filter small clusters (<8:2x2x2)
    min_Vcluster = 8
    stamp("img3.remove_small_objects")
    img3.memset(work, 0)
    Nc = img3.remove_small_objects(labels, min_Vcluster, work)
    sys.stderr.write("  Nc(Vmin): %d\n" % Nc)
    if debug == True:
        labels16[:,:,:] = labels[:,:,:]

    # Store object info
    stamp("candidate cells (img3.objects)")
    lst = img3.objects(labels, Nc)
#    stamp("save candidate list to pickle")
#    with open("%s/lst.pkl" % odir,'wb') as fl:
#        pickle.dump(lst, fl)

    # Volume per cluster
    stamp("Volume and Nparticles per cluster")
    volumes = np.zeros(np.max(labels))
    particles = np.zeros(np.max(labels))
    com = np.zeros((Nc, 3))
    for i in range(Nc):
        volumes[i] = np.shape(lst[i])[0]
        l = lst[i]
        particles[i] = np.sum( img_m[l[:,0], l[:,1], l[:,2]] )
        com[i, 0] = np.mean(l[:,0])
        com[i, 1] = np.mean(l[:,1])
        com[i, 2] = np.mean(l[:,2])

    # Convert coms and volumes to micro-meters
    com[:,0] = com[:,0]*px
    com[:,1] = com[:,1]*py
    com[:,2] = com[:,2]*pz
    volumes *= (px*py*pz)

    # Export data file
    stamp("export data file")
    with open('%s/data_ClusterInfo_%s.dat' % (odir,os.path.basename(fc)), 'w') as f:
        f.write("%12s %12s %12s %12s %12s %12s\n" % ("ClusterID", "Volume(um3)", "Nparticles", "comX(um)", "comY(um)", "comZ(um)"))
        for i in range(Nc):
            f.write("%12d %12.2e %12d %12.2e %12.2e %12.2e\n" % (i+1, volumes[i], particles[i], com[i,0], com[i,1], com[i,2]) )
        f.close()


