###################################################
# File Name     : cluster_overlay.py
# Creation Date : 14-03-2023
# Last Modified : Wed 29 Mar 2023 12:26:19 PM UTC
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
from tifffile import imsave
from scipy.ndimage import label as slabel
from scipy.ndimage import binary_dilation

import img3


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# UTILITY FUNCTIONS
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~

me = "cluster_overlay.py"

def stamp(s):
    sys.stderr.write("%s: %d: %s\n" % (me, time.time() - start, s))

def nrrd_details(fnrrd):
    nrrd        = img3.nrrd_read(fnrrd)
    dtype       = nrrd["type"]
    path        = nrrd["path"]
    shape       = nrrd["sizes"]
    offset      = nrrd.get("byte skip", 0)
    dx, dy, dz  = nrrd.get("spacings")
    return dtype, path, shape, offset, dx, dy, dz

def read_input(argsi, me, path, dtype, offset, shape):
    try:
        a0 = np.memmap(path, dtype, 'r', offset=offset, shape=shape, order='F')
    except FileNotFoundError:
        sys.stderr.write("%s: file not found '%s'\n" % (me, argsi))
        sys.exit(1)
    except ValueError:
        sys.stderr.write("%s: wrong size/type '%s'\n" % (me, argsi))
        sys.exit(1)
    return a0

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




start = time.time()

parser = argparse.ArgumentParser()
parser.add_argument('-m', type=str, nargs='+', required=True, help="nrrd, marker img data")
parser.add_argument('-c', type=str, nargs='+', required=True, help="nrrd, channel img data")
parser.add_argument('-o', type=str, required=True, help="output directory")
args = parser.parse_args()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LOAD FILES
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~
for fm,fc in zip(args.m, args.c):

    stamp("load image files")
    # marker
    dtype, path, shapem, offset, dx, dy, dz = nrrd_details(fm)
    img_m = read_input(fm, me, path, dtype, offset, shapem)
    # channel
    dtype, path, shapec, offset, dx, dy, dz = nrrd_details(fc)
    img_c = read_input(fc, me, path, dtype, offset, shapec)
    spacings = (dx,dy,dz)
    assert(shapem == shapec)
    shape = shapem


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # CREATE WORK ARRAYS
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    stamp("create working arrays")
    odir = args.o
    if not os.path.exists(odir):
        os.makedirs(odir)

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
    min_particles = 3 # Ignore bins with 3 and fewer particles
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
    com[:,0] = com[:,0]*dx
    com[:,1] = com[:,1]*dy
    com[:,2] = com[:,2]*dz
    volumes *= (dx*dy*dz)

    # Export data file
    stamp("export data file")
    with open('%s/data_ClusterInfo_%s.dat' % (odir,os.path.basename(fc)), 'w') as f:
        f.write("%12s %12s %12s %12s %12s %12s\n" % ("ClusterID", "Volume(um3)", "Nparticles", "comX(um)", "comY(um)", "comZ(um)"))
        for i in range(Nc):
            f.write("%12d %12.2e %12d %12.2e %12.2e %12.2e\n" % (i+1, volumes[i], particles[i], com[i,0], com[i,1], com[i,2]) )
        f.close()


